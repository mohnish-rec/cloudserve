"""Day 4: write replies for a few tickets, run the five guardrails, and read them (uses the Groq key).

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
Default tickets: four the system answers, plus DEV-0002 and DEV-0011, which routing
let through although the articles do not answer them (day 3): the model should
answer "not answered" for those two. Tickets a safety rule sends to a person get
no model call at all (NFR-07).

Run:  python scripts/try_generate.py [--ids DEV-0001 DEV-0002 ...]
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.classify import TicketClassifier  # noqa: E402
from src.generate import articles_for, generate, with_notice  # noqa: E402
from src.guardrails import check_reply  # noqa: E402
from src.route import CONFIDENCE_THRESHOLD  # noqa: E402
from src.ingest import load_tickets  # noqa: E402
from src.retrieve import Retriever  # noqa: E402
from src.safety import check  # noqa: E402

DEFAULT = ["DEV-0001", "DEV-0004", "DEV-0012", "DEV-0017", "DEV-0002", "DEV-0011"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", nargs="+", default=DEFAULT)
    args = ap.parse_args()
    retriever = Retriever.from_store()
    model = TicketClassifier.load(embedder=retriever.embedder)
    tickets = {t.ticket_id: t for t in load_tickets(ROOT / "data" / "development_tickets.json")}
    for tid in args.ids:
        t = tickets[tid]
        c = model.classify(t.text)
        print("=" * 100, f"\n{tid}  type {c.intent} ({c.confidence:.0%})\nTICKET: {t.text}\n")
        s = check(t.text, c.intent)
        if s.must_go_to_person:
            print(f"-> no model call: safety rule ({'; '.join(s.reasons)})\n")
            continue
        passages = retriever.search(t.text)
        print("ARTICLES FOUND: " + ", ".join(f"[{i}] {p.doc_id}" for i, p in enumerate(passages, 1)))
        d = generate(t.text, c.intent, passages)
        print(f"MODEL: {d.model or '-'}, {d.calls} call(s), {d.latency_ms} ms, prompt {d.prompt_version}")
        print(f"ANSWERED: {d.answered}   SURE: {d.sure}   CITED: {list(d.cited_doc_ids)}")
        print(f"SUMMARY FOR A COLLEAGUE: {d.summary}\nUNSURE ABOUT: {d.unsure_about or '-'}")
        if d.ok:
            reply = with_notice(d, passages)
            print("\nREPLY (before the guardrails):\n" + reply + "\n")
            arts = {a["doc_id"]: a for a in articles_for(passages)}
            g = check_reply(reply, d, arts, t.text, c.confidence, CONFIDENCE_THRESHOLD)
            for name, result in g.as_log().items():
                print(f"   {name:<22} {result}")
            print("-> BLOCKED, to a person: " + ", ".join(g.fired) if g.blocked else "-> SENT to the customer")
            print()
        else:
            print(f"\n-> to a person: {d.error}\n   model said: {d.reply or d.raw[:300]}\n")


if __name__ == "__main__":
    main()
