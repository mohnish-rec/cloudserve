"""Build Specification checkpoint, day 3: "Run twenty tickets and read the log.
Every decision has a reason."

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.

For each ticket: ingest -> classify (saved model, D-018) -> safety rules -> search
(D-017) -> route (D-019). Two decisions are logged per ticket (classification and
routing), then read back from the database and printed, and the counts reconciled
(acceptance criterion A8). Each ticket is routed twice to check A5 (same input, same
decision). No reply is generated yet (day 4).

Note: the saved model was trained on all 500 development tickets, so on these
tickets it has seen the questions; this run checks the log, not accuracy.

Run:  python scripts/setup_decision_log.py      (once; adds the new columns)
      python scripts/run_twenty.py [--input data/development_tickets.json] [--n 20]
"""
import argparse
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src import logging_store as log  # noqa: E402
from src.classify import TicketClassifier  # noqa: E402
from src.ingest import is_blocked, load_tickets  # noqa: E402
from src.retrieve import Retriever  # noqa: E402
from src.route import ESCALATE, SPECIALIST, RouteDecision, queue_key, route  # noqa: E402
from src.safety import check  # noqa: E402

MODEL_NAME = "logistic regression on all-MiniLM-L6-v2 embeddings, C=10 (models/classifier.joblib, D-018)"


def summary(t) -> str:
    """What came in, with no personal details: never the text, never the name."""
    return (f"{t.channel} ticket, {len(t.text)} characters; plan {t.customer_tier}, "
            f"region {t.customer_region}, {t.language_fluency} English")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=str(ROOT / "data" / "development_tickets.json"))
    ap.add_argument("--n", type=int, default=20)
    args = ap.parse_args()

    retriever = Retriever.from_store()
    model = TicketClassifier.load(embedder=retriever.embedder)
    tickets = load_tickets(args.input)[: args.n]
    run_id = "checkpoint-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:6]
    con = log.connect()
    unstable, routed = 0, []
    for t in tickets:
        start = time.perf_counter()
        if is_blocked(t):
            c = model.classify("")                       # defined fallback for an unusable ticket
        else:
            c = model.classify(t.text)
        log.write(log.DecisionRecord(
            run_id=run_id, ticket_id=t.ticket_id, stage="classification", input_summary=summary(t),
            prediction=c.intent, confidence=c.confidence,
            alternatives=[{"value": v, "confidence": p} for v, p in c.alternatives],
            action_taken="classified", model=MODEL_NAME, requirement_ids=["FR-02"],
            reason=(f"Type {c.intent} at {c.confidence:.0%}, urgency {c.urgency} at {c.urgency_confidence:.0%}."
                    if not c.fallback else f"Could not classify: {c.reason}.")), con)
        s = check(t.text, c.intent)
        passages = retriever.search(t.text)
        d = route(t.text, c, s, passages, received_at=t.received_at)
        if d != route(t.text, c, s, passages, received_at=t.received_at):
            unstable += 1
        try:
            log.write(log.DecisionRecord(
                run_id=run_id, ticket_id=t.ticket_id, stage="routing", input_summary=summary(t),
                prediction=c.intent, confidence=d.confidence, threshold=d.threshold,
                action_taken=d.action, label=d.label, reason=d.reason,
                sources_used=[{"doc_id": p.doc_id, "score": p.similarity} for p in passages],
                guardrails={"safety_rules": list(s.reasons) or "none fired"}, model="rules (src/route.py)",
                latency_ms=int((time.perf_counter() - start) * 1000), requirement_ids=list(d.requirement_ids)), con)
        except Exception as e:   # noqa: BLE001 - a record that fails the schema is escalated, never dropped
            d = RouteDecision(ESCALATE, SPECIALIST, d.priority, d.near_breach, d.confidence, d.threshold,
                              d.reasons, f"Sent to a person because its log record failed the check: {e}", ("FR-10",))
            log.write(log.DecisionRecord(run_id=run_id, ticket_id=t.ticket_id, stage="routing",
                                         input_summary=summary(t), action_taken="escalate", label=SPECIALIST,
                                         reason=d.reason, requirement_ids=["FR-10"]), con)
        routed.append((t, d))

    rows = log.read(con, run_id)
    by_stage = {st: sum(r["stage"] == st for r in rows) for st in ("classification", "routing")}
    print(f"run {run_id}: {len(tickets)} tickets\n")
    print("| Ticket | Action | Label | Priority | Reason (as logged) |\n|---|---|---|---|---|")
    for r in (r for r in rows if r["stage"] == "routing"):
        pr = next(d.priority for t, d in routed if t.ticket_id == r["ticket_id"])
        print(f"| {r['ticket_id']} | {r['action_taken']} | {r['label'] or '-'} | {pr} | {r['reason']} |")
    auto = sum(d.action == "auto_respond" for _, d in routed)
    print(f"\nAnswered automatically {auto}, sent to a person {len(routed) - auto} "
          f"(Draft ready {sum(d.label.startswith('Draft') for _, d in routed)}, "
          f"Needs a specialist {sum(d.label == SPECIALIST for _, d in routed)})")
    print(f"Reconcile (A8): {len(tickets)} tickets, {by_stage['routing']} routing decisions, "
          f"{by_stage['classification']} classification decisions -> "
          + ("OK" if by_stage["routing"] == by_stage["classification"] == len(tickets) else "MISMATCH"))
    print(f"Same input, same decision (A5): {len(tickets) - unstable} of {len(tickets)}")
    order = [t.ticket_id for t, d in sorted(routed, key=lambda x: queue_key(x[1], x[0].received_at))
             if d.action == ESCALATE]
    print("Agents' queue order (FR-13): " + ", ".join(order[:10]) + (" ..." if len(order) > 10 else ""))
    con.close()


if __name__ == "__main__":
    main()
