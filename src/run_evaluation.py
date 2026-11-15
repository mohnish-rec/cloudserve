"""The end-to-end run (Build Specification section 04, FR-12, acceptance criterion A9).

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
The Dataset Guide's signature, run_evaluation(input_path, output_path), filled in.

One command, any ticket file, no intervention:
    python -m src.run_evaluation data/validation_tickets.json evaluation/results/validation_run.json
Writes the per-ticket results (output_path), the metrics report beside it (..._metrics.md),
and every decision to the decision log under a new run ID. Running the same file again gives
the same decisions under a new run ID and duplicates nothing (FR-11).
A ticket that fails in any unexpected way is escalated with the reason, never dropped or skipped.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src import logging_store as log  # noqa: E402
from src import metrics  # noqa: E402
from src import report  # noqa: E402
from src.classify import TicketClassifier  # noqa: E402
from src.generate import ACTIVE_PROMPT  # noqa: E402
from src.guardrails import GUARD_MODEL  # noqa: E402
from src.ingest import load_tickets  # noqa: E402
from src import followups  # noqa: E402
from src.pipeline import ACKNOWLEDGEMENT, Outcome, citation_trail, process  # noqa: E402
from src.retrieve import Retriever  # noqa: E402
from src.route import CONFIDENCE_THRESHOLD, SPECIALIST  # noqa: E402

CLASSIFIER = "logistic regression on all-MiniLM-L6-v2 embeddings, C=10 (D-018)"


def summary(t) -> str:
    return (f"{t.channel} ticket, {len(t.text)} characters; plan {t.customer_tier}, "
            f"region {t.customer_region}, {t.language_fluency} English")


def log_ticket(con, run_id, t, o: Outcome):
    """Every stage that ran, then the final outcome: one trace per ticket (FR-10)."""
    base = dict(run_id=run_id, ticket_id=t.ticket_id, input_summary=summary(t))
    c, d = o.classification, o.route
    if c is not None:
        log.write(log.DecisionRecord(**base, stage="classification", prediction=c.intent, confidence=c.confidence,
                                     alternatives=[{"value": v, "confidence": p} for v, p in c.alternatives],
                                     action_taken="classified", model=CLASSIFIER, requirement_ids=["FR-02"],
                                     reason=(f"Type {c.intent} at {c.confidence:.0%}, urgency {c.urgency}."
                                             if not c.fallback else f"Could not classify: {c.reason}.")), con)
    if d is not None:
        log.write(log.DecisionRecord(**base, stage="routing", prediction=c.intent if c else None,
                                     confidence=d.confidence, threshold=d.threshold, action_taken=d.action,
                                     label=d.label, reason=d.reason, model="rules (src/route.py)",
                                     sources_used=list(o.sources) or [{"doc_id": x} for x in o.passage_ids],
                                     requirement_ids=list(d.requirement_ids)), con)
    if o.draft is not None:
        g = o.draft
        log.write(log.DecisionRecord(**base, stage="generation", action_taken="auto_respond" if g.ok else "escalate",
                                     reason=(f"Reply drafted from {', '.join(g.cited_doc_ids)}; writer {g.sure}"
                                             if g.ok else f"No reply: {g.error}")
                                     + f"; tokens {g.tokens_in} in, {g.tokens_out} out.",
                                     sources_used=citation_trail(g, o.sources) or [{"doc_id": x} for x in g.cited_doc_ids],
                                     provider="groq",
                                     model=g.model or None, latency_ms=g.latency_ms, prompt_version=g.prompt_version,
                                     requirement_ids=["FR-05", "FR-11"]), con)
    if o.guardrails is not None:
        log.write(log.DecisionRecord(**base, stage="validation", guardrails=o.guardrails.as_log(),
                                     action_taken="block" if o.guardrails.blocked else "auto_respond",
                                     reason=("Blocked: " + ", ".join(o.guardrails.fired) + "." if o.guardrails.blocked
                                             else f"All {len(o.guardrails.checks)} guardrails passed."),
                                     model=GUARD_MODEL, prompt_version="PR-02 v1.0", requirement_ids=["FR-09"]), con)
    log.write(log.DecisionRecord(**base, stage="outcome", prediction=c.intent if c else None,
                                 confidence=c.confidence if c else None, threshold=CONFIDENCE_THRESHOLD,
                                 action_taken=o.action, label=o.label, reason=o.reason,
                                 sources_used=citation_trail(o.draft, o.sources)
                                 or [{"doc_id": x} for x in (o.draft.cited_doc_ids if o.draft else ())],
                                 latency_ms=o.latency_ms, requirement_ids=list(o.requirement_ids) or ["FR-12"]), con)


def failed(t, e) -> Outcome:
    """An unexpected error: the ticket goes to a person with the reason (fail closed)."""
    return Outcome(t.ticket_id, "escalate", SPECIALIST, "medium",
                   f"Sent to a person ({SPECIALIST}) because the system hit an unexpected error: {type(e).__name__}.",
                   ACKNOWLEDGEMENT, {"summary": "", "tried": [f"error: {type(e).__name__}: {str(e)[:200]}"],
                                     "article": "", "draft": "", "unsure": "system error"},
                   requirement_ids=("FR-11",))


def record_metrics(t, o: Outcome):
    """Setup Guide 06: what the Prometheus metrics count, for the run and for the API alike."""
    metrics.TICKETS.labels(t.channel, o.action).inc()
    metrics.LATENCY.observe(o.latency_ms / 1000)
    if o.classification is not None:
        metrics.CONFIDENCE.observe(o.classification.confidence)
    for name in (o.guardrails.fired if o.guardrails else []):
        metrics.GUARDRAIL.labels(name).inc()


def as_result(o: Outcome) -> dict:
    """One ticket's result, as written to the results file and returned by the API."""
    return {"ticket_id": o.ticket_id, "action": o.action, "label": o.label, "priority": o.priority,
            "reason": o.reason, "sent_text": o.sent_text, "handover": o.handover,
            "type": o.classification.intent if o.classification else None,
            "confidence": o.classification.confidence if o.classification else None,
            "articles_found": list(o.passage_ids),
            "cited": list(o.draft.cited_doc_ids) if o.draft else [],
            "citations": citation_trail(o.draft, o.sources),     # 11 Nov: each cited article -> passages, sentences
            "guardrails": o.guardrails.as_log() if o.guardrails else {},
            "model_calls": o.model_calls, "tokens": o.tokens, "latency_ms": o.latency_ms}


CIRCUIT_AFTER = 3   # consecutive tickets with the model unavailable before the circuit opens


def provider_down(t) -> Outcome:
    """Circuit open: the provider has failed for several tickets in a row (e.g. the daily limit),
    so the rest go straight to a person instead of each waiting through every retry (FR-11)."""
    return Outcome(t.ticket_id, "escalate", SPECIALIST, "medium",
                   f"Sent to a person ({SPECIALIST}) because the model provider is unavailable "
                   f"(failed for {CIRCUIT_AFTER} tickets in a row): model unavailable, circuit open.",
                   ACKNOWLEDGEMENT, {"summary": "", "tried": ["not attempted: model provider unavailable"],
                                     "article": "", "draft": "", "unsure": "model provider unavailable"},
                   requirement_ids=("FR-11",))


def run_evaluation(input_path: str, output_path: str, metrics_port: int = None, use_cache: bool = False) -> dict:
    """use_cache is OFF unless asked for: validation, hidden-set and final runs must be a fresh test that
    neither reads nor writes stored answers (D-025). Only development test runs may turn it on."""
    started = time.perf_counter()
    os.environ["REPLY_CACHE"] = "on" if use_cache else "off"
    if metrics_port:
        metrics.start_metrics_server(metrics_port)
    raw = json.loads(Path(input_path).read_text(encoding="utf-8-sig"))
    raw = raw.get("tickets", raw) if isinstance(raw, dict) else raw
    raw_by_id = {str(r.get("ticket_id")): r for r in raw if isinstance(r, dict)}
    tickets = load_tickets(input_path)
    retriever = Retriever.from_store()
    classifier = TicketClassifier.load(embedder=retriever.embedder)
    run_id = "run-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:6]
    con = log.connect()
    outcomes, down_in_a_row = [None] * len(tickets), 0
    followups.reset()                     # 14 Nov: follow-ups are recognised within this run only
    # In time order, so a customer's earlier ticket is handled before its follow-up; results keep the file's order.
    order = sorted(range(len(tickets)), key=lambda i: tickets[i].received_at or "~")
    print(f"{run_id}: {len(tickets)} tickets from {input_path}", flush=True)
    for k, i in enumerate(order, 1):
        t = tickets[i]
        try:
            o = provider_down(t) if down_in_a_row >= CIRCUIT_AFTER else process(t, classifier, retriever)
        except Exception as e:  # noqa: BLE001 - never drop or skip a ticket
            o = failed(t, e)
        if down_in_a_row < CIRCUIT_AFTER:
            down_in_a_row = down_in_a_row + 1 if "model unavailable" in (o.reason + str(o.handover)) else 0
        try:
            log_ticket(con, run_id, t, o)
        except Exception as e:  # noqa: BLE001 - a record that fails the schema: escalate, log the minimum
            o = failed(t, e)
            log.write(log.DecisionRecord(run_id=run_id, ticket_id=t.ticket_id, stage="outcome", input_summary=summary(t),
                                         action_taken="escalate", label=SPECIALIST, reason=o.reason,
                                         requirement_ids=["FR-10"]), con)
        record_metrics(t, o)
        outcomes[i] = o
        print(f"  [{k}/{len(tickets)}] {t.ticket_id} {o.action:<12} {o.label or '-':<28} {o.latency_ms / 1000:5.1f} s", flush=True)

    rows = log.read(con, run_id)
    con.close()
    logged = {"total": len(rows), "outcome": sum(r["stage"] == "outcome" for r in rows)}
    git = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    meta = {"input": Path(input_path).name, "run_id": run_id,
            "date": datetime.now(timezone.utc).isoformat(timespec="seconds"), "git_commit": git or "unknown",
            "prompts": f"{ACTIVE_PROMPT[1]}, PR-02 v1.0", "writer": os.getenv("MODEL_NAME", "openai/gpt-oss-20b"),
            "backup": os.getenv("BACKUP_MODEL_NAME", "openai/gpt-oss-120b"), "checker": GUARD_MODEL,
            "classifier": CLASSIFIER, "threshold": CONFIDENCE_THRESHOLD,
            "reply_cache": "on (development run)" if use_cache else "off (fresh run)",
            "writer_provider": "Groq direct (free tier)",
            "experiment": (f"trim {os.getenv('TRIM_UNSUPPORTED', 'on')}, writer reads {os.getenv('WRITER_ARTICLES', '3')} "
                           f"articles, narrowed safety rules {os.getenv('NARROW_RULES', 'on')}, "
                           f"type-aware search {os.getenv('TYPE_AWARE_SEARCH', 'on')}, "
                           f"question rules {os.getenv('QUESTION_RULES', 'on')}, "
                           f"learned decisions {os.getenv('LEARNED_DECISIONS', 'on')}, "
                           f"plan rule {os.getenv('PLAN_RULE', 'on')}"),   # the switches as run (12 Nov)
            "input_sha256": hashlib.sha256(Path(input_path).read_bytes()).hexdigest()[:16],
            "minutes": round((time.perf_counter() - started) / 60, 1)}
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    results = [as_result(o) for o in outcomes]
    out.write_text(json.dumps({"meta": meta, "results": results}, indent=2, ensure_ascii=False), encoding="utf-8")
    md = out.with_name(out.stem + "_metrics.md")
    try:
        text = report.build(outcomes, tickets, raw_by_id, meta, logged)
    except Exception as e:  # noqa: BLE001 - the results are already saved; say what failed, never lose the run
        text = f"# Metrics report\n\nThe report could not be built: {type(e).__name__}: {e}\n"
    md.write_text(text + f"\nRun time: {meta['minutes']} minutes.\n", encoding="utf-8")
    print(f"\ndone in {meta['minutes']} min. results: {out}  report: {md}", flush=True)
    return meta


def main():
    ap = argparse.ArgumentParser(description="Run the whole ticket file through the system, unattended.")
    ap.add_argument("input_path")
    ap.add_argument("output_path")
    ap.add_argument("--metrics-port", type=int, default=None, help="serve Prometheus metrics while running (e.g. 8001)")
    ap.add_argument("--use-cache", action="store_true",
                    help="development runs only: reuse stored answers. Never for validation or final runs (D-025)")
    a = ap.parse_args()
    run_evaluation(a.input_path, a.output_path, a.metrics_port, a.use_cache)


if __name__ == "__main__":
    main()
