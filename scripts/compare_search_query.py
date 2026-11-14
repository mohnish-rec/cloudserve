"""14 Nov 2026 (walkthrough, Q09/Q25/Q27/Q30/Q34): does a misleading subject line pull the search to the wrong article?
Runs the real search (with type-aware search, as the system does) on all 500 development tickets twice: on subject +
message (as now) and on the message alone (the subject only when the message has fewer than 6 words). No model calls.

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
Run:    python scripts/compare_search_query.py
Writes: evaluation/results/compare_search_query.md
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import src  # noqa: E402,F401  (loads Chroma first, the Windows load-order fix)
from src.ingest import load_tickets  # noqa: E402
from src.retrieve import Retriever, search_typed  # noqa: E402

MIN_WORDS = 6
tickets = load_tickets(ROOT / "data" / "development_tickets.json")
labels = {t["ticket_id"]: t["labels"] for t in json.loads((ROOT / "data" / "development_tickets.json").read_text(encoding="utf-8-sig"))}
run = {r["ticket_id"]: r for r in json.loads((ROOT / "evaluation" / "results" / "dev500_final_groq.json").read_text(encoding="utf-8"))["results"]}
retriever = Retriever.from_store()


def top3(text, intent):
    return list(dict.fromkeys(p.doc_id for p in search_typed(retriever, text, intent)))[:3]


rows, changed = [], []
for t in tickets:
    intent = run[t.ticket_id]["type"]
    query = t.body if len(t.body.split()) >= MIN_WORDS else t.text
    a, b = top3(t.text, intent), top3(query, intent)
    exp = set(labels[t.ticket_id]["expected_doc_ids"] or [])
    rows.append((t.ticket_id, bool(exp), bool(exp & set(a)), bool(exp & set(b)), a == b, bool(exp & set(a[:1])), bool(exp & set(b[:1]))))
    if a != b:
        changed.append(f"| {t.ticket_id} | {t.subject} | {t.body[:70]} | {', '.join(a)} | {', '.join(b)} |")
with_exp = [r for r in rows if r[1]]
L = ["# Search on subject + message (now) vs the message alone", "",
     f"Development tickets: {len(rows)}. Top 3 articles changed for {sum(not r[4] for r in rows)} tickets.", "",
     "| Measure (tickets whose labels name an article) | Subject + message | Message alone |", "|---|---|---|",
     f"| Expected article in the top 3 | {sum(r[2] for r in with_exp)} of {len(with_exp)} | {sum(r[3] for r in with_exp)} of {len(with_exp)} |",
     f"| Expected article ranked first | {sum(r[5] for r in with_exp)} of {len(with_exp)} | {sum(r[6] for r in with_exp)} of {len(with_exp)} |", "",
     "## Every ticket whose top 3 changed", "",
     "| Ticket | Subject | Message (start) | Top 3 now | Top 3 on the message alone |", "|---|---|---|---|---|"] + changed
out = ROOT / "evaluation" / "results" / "compare_search_query.md"
out.write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L[:9]))
print(f"Written: {out}")
