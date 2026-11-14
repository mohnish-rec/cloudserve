"""14 Nov 2026 (Q25, Mohnish Grover): a misleading subject ("Database restore taking hours") pulls an article into the
reply that the message never asks about (DEV-0374, DEV-0378). Proposed fix, a "message check": the search stays as
it is (subject + message), but an article it found is kept only if a search on the MESSAGE ALONE also finds it
(in its top 5). Nothing is ever added; if the check would leave no article, or the message is under 6 words, the
articles stay as they are. No new number to tune: it reuses the search's own top 5.

This script changes nothing in the system. It runs the real search on all 500 development tickets, with no model
calls, and lists every ticket whose articles would change. The labels' expected articles are used only to score.

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
Run:    python scripts/compare_message_check.py
Writes: evaluation/results/compare_message_check.md
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
READS = 3                      # the writer reads the top 3 articles
tickets = load_tickets(ROOT / "data" / "development_tickets.json")
raw = {t["ticket_id"]: t for t in json.loads((ROOT / "data" / "development_tickets.json").read_text(encoding="utf-8-sig"))}
run = {r["ticket_id"]: r for r in json.loads(
    (ROOT / "evaluation" / "results" / "dev500_message_only_SANDBOX_PAID.json").read_text(encoding="utf-8"))["results"]}
W = json.loads((ROOT / "evaluation" / "human_review" / "dev_walkthrough.json").read_text(encoding="utf-8"))["questions"]
qof = {k: q["question"] for q in W for k in q["tickets"]}
retriever = Retriever.from_store()
docs = lambda text, intent: list(dict.fromkeys(p.doc_id for p in search_typed(retriever, text, intent)))

rows = []
for t in tickets:
    intent = run[t.ticket_id]["type"]                       # the type the system decided
    now = docs(t.text, intent)[:READS]
    if len(t.body.split()) >= MIN_WORDS:
        msg = set(docs(t.body, intent))
        kept = [d for d in now if d in msg] or now
    else:
        kept = now
    exp = set(raw[t.ticket_id]["labels"]["expected_doc_ids"] or [])
    rows.append((t, now, kept, exp))

changed = [r for r in rows if r[1] != r[2]]
lost = [r for r in changed if (r[3] & set(r[1])) - set(r[2])]          # an expected article removed
scored = [r for r in rows if r[3]]
first = lambda arts, exp: bool(arts) and arts[0] in exp
L = ["# Message check: keep an article only if the message alone also finds it", "",
     f"Development tickets: {len(rows)}. Articles would change for **{len(changed)}** tickets "
     f"(an article removed; nothing is ever added).", "",
     "| Measure (tickets whose labels name an article) | Now | With the message check |", "|---|---|---|",
     f"| Expected article among the articles the writer reads | {sum(bool(r[3] & set(r[1])) for r in scored)} of {len(scored)} "
     f"| {sum(bool(r[3] & set(r[2])) for r in scored)} of {len(scored)} |",
     f"| Expected article first | {sum(first(r[1], r[3]) for r in scored)} of {len(scored)} "
     f"| {sum(first(r[2], r[3]) for r in scored)} of {len(scored)} |",
     f"| Tickets where an expected article would be removed | | **{len(lost)}** |", "",
     "## Every ticket whose articles would change", "",
     "| Ticket | Question | Subject | Message (start) | Now | With the check | Removed | Expected (labels) |",
     "|---|---|---|---|---|---|---|---|"]
for t, now, kept, exp in changed:
    L.append(f"| {t.ticket_id} | {qof.get(t.ticket_id, '')} | {t.subject} | {t.body[:60]} | {', '.join(now)} | "
             f"{', '.join(kept)} | {', '.join(d for d in now if d not in kept)}{' **(expected!)**' if (exp & set(now)) - set(kept) else ''} "
             f"| {', '.join(sorted(exp)) or '-'} |")
out = ROOT / "evaluation" / "results" / "compare_message_check.md"
out.write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L))
