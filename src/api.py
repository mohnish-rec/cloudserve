"""The FastAPI application (Setup Guide 08: src/api.py; Build Specification: "python -m src.api").

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
One ticket in, one decision out, through exactly the same pipeline as the unattended run (src/pipeline.py):
every guardrail runs, every decision is written to the decision log, and the Prometheus metrics count it.
The answer key is never read: only the ticket fields in TicketIn are kept, anything else sent is dropped.

Run:    python -m src.api                      (http://127.0.0.1:8000/docs to try a ticket in the browser)
        API_PORT=8000, METRICS_PORT=8001 (the port prometheus.yml reads; 0 turns the metrics server off)
Ends:   GET  /          a web page: choose a ticket file and press Run (src/web_runs.py)
        POST /runs      start the unattended run for an uploaded ticket file; GET /runs/<id> shows its progress
        POST /live-charts  start the live charts from zero (src/live_charts.py); GET /live-charts shows how far it got
        POST /kill-switch  {"on": true} or {"on": false}: turn the kill switch on or off from the web page (FR-16)
        GET  /limits       how much of the free tier's limits each model has used (src/limits.py); POST /limits/check
                           makes one tiny call to each model for fresh figures
        GET  /demo-tickets the seven demo tickets (data/samples/demo_tickets.json), for the page's demo button
        GET  /decision-log/<run id>/<ticket id>  every decision-log row for one ticket (the page's ticket details)
        GET  /runs/<id>/tickets/<ticket id>  one ticket's full result from a file run
        GET  /runs/<id>/check  the run's decision-log counts next to its results (README step 10)
        GET  /runs/<id>/download/results or /report  the run's results file or metrics report
        GET  /health    is the system up, and is the kill switch on?
        GET  /healthz   alive (FR-17)
        GET  /readyz    ready to answer tickets: models, article index and AI key all in place (FR-17)
        POST /tickets   one ticket -> the decision, the reply or the handover, and the reasons
"""
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel

from src import logging_store as log
from src import metrics
from src.ingest import normalise
from src.pipeline import process
from src.run_evaluation import as_result, failed, log_ticket, record_metrics
from src.live_charts import LiveCharts
from src.web_runs import PAGE, FileRuns


class KillSwitchIn(BaseModel):
    """The web page's kill switch button: on (true) or off (false)."""
    on: bool


class TicketIn(BaseModel):
    """The ticket fields the system reads. Anything else sent (such as labels) is dropped."""
    ticket_id: str
    channel: str
    subject: Optional[str] = ""
    body: str
    received_at: Optional[str] = None
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    customer_tier: Optional[str] = None
    customer_region: Optional[str] = None
    language_fluency: Optional[str] = None


def readiness(root=None) -> list:
    """What is missing before tickets can be answered: the trained models, the article index, the AI key."""
    root = Path(root) if root else Path(__file__).resolve().parent.parent
    need = {"classifier model (python scripts/train_classifier.py)": root / "models" / "classifier.joblib",
            "learned decisions model (python scripts/train_decision_router.py)": root / "models" / "decision_router.joblib",
            "article index (python scripts/setup_vector_store.py)": root / os.getenv("CHROMA_PATH", "storage/chroma")}
    missing = [name for name, path in need.items() if not Path(path).exists()]
    if not (os.getenv("LLM_API_KEY") or os.getenv("WRITER_API_KEY")):
        missing.append("AI key (LLM_API_KEY in .env)")
    return missing


FIELDS = tuple(getattr(TicketIn, "model_fields", None) or TicketIn.__fields__)


def create_app(classifier=None, retriever=None, write_log=True, file_runs=None, live_charts=None,
               **options) -> FastAPI:
    """classifier and retriever load on the first ticket unless given (tests pass fakes). options go to process().
    file_runs runs uploaded ticket files for the web page (tests pass one with a fake run); live_charts is the page's
    "Start the live charts from zero" button (tests pass one with a fake script)."""
    app = FastAPI(title="CloudServe support triage",
                  description="One ticket in: answered automatically with cited help articles, or handed to a person "
                              "with a draft and the reasons. Same pipeline, guardrails and decision log as the "
                              "unattended run.")
    parts = {"classifier": classifier, "retriever": retriever}
    run_id = "api-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")

    def load():
        if parts["retriever"] is None:
            from src.classify import TicketClassifier
            from src.retrieve import Retriever
            parts["retriever"] = Retriever.from_store()
            parts["classifier"] = TicketClassifier.load(embedder=parts["retriever"].embedder)
        return parts["classifier"], parts["retriever"]

    def handle(raw: dict) -> dict:
        t = normalise({k: raw.get(k) for k in FIELDS})              # only the ticket's own fields
        try:
            classifier_, retriever_ = load()
            o = process(t, classifier_, retriever_, **options)
        except Exception as e:  # noqa: BLE001 - fail closed: a person gets it, the API never errors on a ticket
            o = failed(t, e)
        if write_log:
            con = log.connect()
            try:
                log_ticket(con, run_id, t, o)
            finally:
                con.close()
        record_metrics(t, o)
        return {"run_id": run_id, **as_result(o)}

    runs = file_runs or FileRuns()
    charts = live_charts or LiveCharts()

    @app.get("/", response_class=HTMLResponse)
    def home():
        """The web page: choose a ticket file, press Run, watch the progress, read the metrics report."""
        return PAGE

    @app.post("/runs")
    async def start_run(file: UploadFile = File(...)):
        """Start the unattended run for an uploaded ticket file, in the background."""
        data = await file.read()
        try:
            return runs.start(file.filename, data)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from None
        except RuntimeError as e:
            raise HTTPException(status_code=409, detail=str(e)) from None

    @app.get("/runs/{job_id}")
    def run_status(job_id: str):
        """How far a file run has got, and its metrics report when it has finished."""
        status = runs.status(job_id)
        if status is None:
            raise HTTPException(status_code=404, detail="No run with that id.")
        return status

    @app.post("/live-charts")
    def start_live_charts():
        """Set the chart numbers back to 0 and start Prometheus afresh (scripts/start_live_charts.ps1)."""
        if runs.busy():
            raise HTTPException(status_code=409, detail="A file is being processed. Start the live charts before "
                                                        "the next run, not during one.")
        try:
            return charts.start()
        except RuntimeError as e:
            raise HTTPException(status_code=409, detail=str(e)) from None

    @app.get("/live-charts")
    def live_charts_status():
        """What the live-charts start has done so far."""
        return charts.status()

    @app.get("/limits")
    def free_tier_limits():
        """What Groq said about its limits on the latest call to each model (no extra call is made)."""
        from src import limits
        return {"models": limits.snapshot(), "capacity": limits.capacity()}

    @app.post("/limits/check")
    def check_limits():
        """One tiny call to each model, then the fresh figures. Uses a few tokens of each limit."""
        from src import limits
        answers = limits.check_now(options.get("limit_call"))
        return {"answers": answers, "models": limits.snapshot(), "capacity": limits.capacity()}

    @app.get("/demo-tickets")
    def demo_tickets():
        """The seven demo tickets of README step 8, with only the fields the system reads (TicketIn); the page sends
        each to POST /tickets."""
        path = Path(__file__).resolve().parent.parent / "data" / "samples" / "demo_tickets.json"
        import json
        fields = TicketIn.model_fields if hasattr(TicketIn, "model_fields") else TicketIn.__fields__
        return [{k: v for k, v in t.items() if k in fields} for t in json.loads(path.read_text(encoding="utf-8"))]

    @app.get("/decision-log/{log_run_id}/{ticket_id}")
    def decision_trail(log_run_id: str, ticket_id: str):
        """Every decision-log row for one ticket: the audit trail behind the page's ticket details."""
        try:
            con = log.connect()
        except FileNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e)) from None
        try:
            return log.ticket_trail(con, log_run_id, ticket_id)
        finally:
            con.close()

    @app.get("/runs/{job_id}/tickets/{ticket_id}")
    def run_ticket(job_id: str, ticket_id: str):
        result = runs.ticket(job_id, ticket_id)
        if result is None:
            raise HTTPException(status_code=404, detail="No such ticket in that run.")
        return result

    @app.get("/runs/{job_id}/check")
    def run_check(job_id: str):
        """README step 10 on the page: the run's results next to what it wrote to the decision log."""
        import json
        status, files = runs.status(job_id), runs.files(job_id)
        if status is None or files is None or not status.get("run_id"):
            raise HTTPException(status_code=404, detail="The run has not finished yet.")
        results = json.loads(Path(files[0]).read_text(encoding="utf-8"))["results"]
        con = log.connect()
        try:
            logged = log.run_check(con, status["run_id"])
        finally:
            con.close()
        counted = {a: sum(r["action"] == a for r in results) for a in ("auto_respond", "escalate", "block")}
        reconciles = logged["tickets"] == logged["outcomes"] == logged["once"] == len(results)
        return {"run_id": status["run_id"], "report": {"processed": len(results), **counted},
                "log": logged, "reconciles": reconciles}

    @app.get("/runs/{job_id}/download/{kind}")
    def run_download(job_id: str, kind: str):
        files = runs.files(job_id)
        if files is None or kind not in ("results", "report"):
            raise HTTPException(status_code=404, detail="Nothing to download yet.")
        path = Path(files[0] if kind == "results" else files[1])
        if not path.exists():
            raise HTTPException(status_code=404, detail="The file is not there.")
        return FileResponse(path, filename=path.name,
                            media_type="application/json" if kind == "results" else "text/markdown")

    @app.post("/kill-switch")
    def kill_switch(choice: KillSwitchIn):
        """FR-16 from the web page: creates or deletes the same file as the README's commands (storage/kill_switch).
        It is checked before every ticket, so it works at once, even in the middle of a run. Each change is also
        written, with the time, to storage/kill_switch_history.txt."""
        from src.route import KILL_SWITCH_FILE, kill_switch_on
        path = Path(options.get("kill_switch_file") or KILL_SWITCH_FILE)
        path.parent.mkdir(parents=True, exist_ok=True)
        if choice.on:
            path.touch()
        elif path.exists():
            path.unlink()
        now_on = kill_switch_on(path)
        stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with open(path.with_name("kill_switch_history.txt"), "a", encoding="utf-8") as history:
            history.write(f"{stamp}  turned {'on' if choice.on else 'off'} from the web page; now "
                          f"{'on' if now_on else 'off'}\n")
        note = ""
        if not choice.on and now_on:
            note = "It is still on because KILL_SWITCH=on is set in the .env file or the environment; change it there."
        return {"kill_switch_on": now_on, "note": note}

    @app.get("/health")
    def health():
        from src.route import kill_switch_on
        return {"status": "ok", "kill_switch_on": kill_switch_on(options.get("kill_switch_file")), "run_id": run_id}

    @app.get("/healthz")
    def healthz():
        """FR-17: the process is alive."""
        return {"status": "alive"}

    @app.get("/readyz")
    def readyz():
        """FR-17: everything a ticket needs is in place. Not ready lists what is missing (nothing is loaded here)."""
        missing = readiness()
        return {"status": "ready" if not missing else "not ready", "missing": missing}

    @app.post("/tickets")
    def tickets(ticket: TicketIn):
        return handle(ticket.model_dump() if hasattr(ticket, "model_dump") else ticket.dict())

    app.state.handle = handle            # the same function, callable directly (tests)
    app.state.file_runs = runs
    app.state.live_charts = charts
    return app


app = create_app()


def main():
    import uvicorn
    port = int(os.getenv("METRICS_PORT", "8001"))
    if port:
        metrics.start_metrics_server(port)
    uvicorn.run(app, host="127.0.0.1", port=int(os.getenv("API_PORT", "8000")))


if __name__ == "__main__":
    main()
