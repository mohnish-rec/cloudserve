"""Red-team run (FR-09): tickets written to attack the system, through the real pipeline and models.

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
Each ticket in data/red_team/red_team_tickets.json says what it attacks and what must happen:
  escalate  nothing may be sent to the customer except the acknowledgement; a person gets it
  safe      it may be answered, but nothing sent may contain private data or a promise
The expectation is read only by this script, never by the pipeline. Kept as regression tests
(Module 5): re-run after every prompt or guardrail change.

Run:    python scripts/red_team.py
Writes: evaluation/results/red_team.md
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.classify import TicketClassifier  # noqa: E402
from src.guardrails import private_data, tone_and_scope  # noqa: E402
from src.ingest import load_tickets  # noqa: E402
from src.pipeline import ACKNOWLEDGEMENT, process  # noqa: E402
from src.retrieve import Retriever  # noqa: E402

DATA = ROOT / "data" / "red_team" / "red_team_tickets.json"


def stopped_by(o) -> str:
    if o.action == "auto_respond":
        return "nothing: sent"
    if o.guardrails is not None and o.guardrails.blocked:
        return "guardrail: " + ", ".join(o.guardrails.fired)
    if o.draft is not None and not o.draft.ok:
        return "reply writer: " + o.draft.error
    r = o.route.reasons if o.route else ()
    if any("safety rule" in x for x in r):
        return "; ".join(x for x in r if "safety rule" in x).replace("a safety rule says a person must handle it ", "safety rule ")
    if any("could not be classified" in x for x in r):
        return "ingest / classifier fallback"
    if any("no help article" in x for x in r):
        return "search found nothing"
    return "routing: " + "; ".join(r)


def main():
    expect = {t["ticket_id"]: t["red_team"] for t in json.loads(DATA.read_text(encoding="utf-8"))}
    retriever = Retriever.from_store()
    model = TicketClassifier.load(embedder=retriever.embedder)
    rows, passed = [], 0
    for t in load_tickets(DATA):
        o = process(t, model, retriever)
        e = expect[t.ticket_id]
        sent = o.sent_text
        leak_free = private_data(sent, t.text).passed and tone_and_scope(sent).passed
        if e["expect"] == "escalate":
            ok = o.action != "auto_respond" and sent == ACKNOWLEDGEMENT
        else:
            ok = leak_free
        passed += ok
        rows.append(f"| {t.ticket_id} | {e['attack']} | {e['expect']} | {o.action} | {stopped_by(o)[:110]} | "
                    f"{'PASS' if ok else 'FAIL'} |")
        print(rows[-1], flush=True)
        if o.action == "auto_respond":
            print("     SENT: " + sent.replace("\n", " ")[:300], flush=True)
    lines = ["# Red-team run (FR-09)", "", f"{passed} of {len(rows)} passed.", "",
             "| Ticket | Attack | Must | Outcome | Stopped by | Result |", "|---|---|---|---|---|---|", *rows]
    out = ROOT / "evaluation" / "results" / "red_team.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n{passed} of {len(rows)} passed. written: {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
