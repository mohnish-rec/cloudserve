"""The FastAPI application (Setup Guide 08: src/api.py; Build Specification: "python -m src.api").

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
One ticket in, one decision out, through exactly the same pipeline as the unattended run (src/pipeline.py):
every guardrail runs, every decision is written to the decision log, and the Prometheus metrics count it.
The answer key is never read: only the ticket fields in TicketIn are kept, anything else sent is dropped.

Run:    python -m src.api                      (http://127.0.0.1:8000/docs to try a ticket in the browser)
        API_PORT=8000, METRICS_PORT=8001 (the port prometheus.yml reads; 0 turns the metrics server off)
Ends:   GET  /health    is the system up, and is the kill switch on?
        POST /tickets   one ticket -> the decision, the reply or the handover, and the reasons
"""
import os
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

from src import logging_store as log
from src import metrics
from src.ingest import normalise
from src.pipeline import process
from src.run_evaluation import as_result, failed, log_ticket, record_metrics


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


FIELDS = tuple(getattr(TicketIn, "model_fields", None) or TicketIn.__fields__)


def create_app(classifier=None, retriever=None, write_log=True, **options) -> FastAPI:
    """classifier and retriever load on the first ticket unless given (tests pass fakes). options go to process()."""
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

    @app.get("/health")
    def health():
        from src.route import kill_switch_on
        return {"status": "ok", "kill_switch_on": kill_switch_on(options.get("kill_switch_file")), "run_id": run_id}

    @app.post("/tickets")
    def tickets(ticket: TicketIn):
        return handle(ticket.model_dump() if hasattr(ticket, "model_dump") else ticket.dict())

    app.state.handle = handle            # the same function, callable directly (tests)
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
