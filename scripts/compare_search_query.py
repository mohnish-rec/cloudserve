"""14 Nov 2026 (walkthrough, Q09/Q25/Q27/Q30/Q34): does a misleading subject line pull the search to the wrong article?
Runs the real search (with type-aware search, as the system does) on all 500 development tickets three ways:
  now       subject + message together (the system today)
  message   the message alone (the subject only when the message has fewer than 6 words)
  combined  both searches, merged by reciprocal rank fusion: an article ranked well by both comes first
No model calls. The labels' expected articles are used only to score the search, never by the system.

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
CASES = ["DEV-0008", "DEV-0374", "DEV-0378", "DEV-0169", "DEV-0209", "DEV-0236", "DEV-0310", "DEV-0295", "DEV-0474"]
tickets = load_tickets(ROOT / "data" / "development_tickets.json")
labels = {t["ticket_id"]: t["labels"] for t in json.loads((ROOT / "data" / "development_tickets.json").read_text(encoding="utf-8-sig"))}
run = {r["ticket_id"]: r for r in json.loads((ROOT / "evaluation" / "results" / "dev500_final_groq.json").read_text(encoding="utf-8"))["results"]}
retriever = Retriever.from_store()


def docs(text, intent):
    return list(dict.fromkeys(p.doc_id for p in search_typed(retriever, text, intent)))


def fuse(a, b, k=60):
    score = {}
    for ranking in (a, b):
        for r, d in enumerate(ranking, 1):
            score[d] = score.get(d, 0) + 1 / (k + r)
    return sorted(score, key=lambda d: -score[d])


res = {}
for t in tickets:
    intent = run[t.ticket_id]["type"]
    query = t.body if len(t.body.split()) >= MIN_WORDS else t.text
    now, msg = docs(t.text, intent), docs(query, intent)
    res[t.ticket_id] = {"now": now[:3], "message": msg[:3], "combined": fuse(now, msg)[:3]}

exp = {k: set(labels[k]["expected_doc_ids"] or []) for k in res}
scored = [k for k in res if exp[k]]
rank = lambda k, v: next((i for i, d in enumerate(res[k][v]) if d in exp[k]), 9)
L = ["# Search: subject + message (now) vs the message alone vs both combined", "",
     "| Measure (tickets whose labels name an article) | Now | Message alone | Combined |", "|---|---|---|---|"]
for name, f in [("Expected article in the top 3", lambda k, v: rank(k, v) < 3), ("Expected article ranked first", lambda k, v: rank(k, v) == 0)]:
    L.append(f"| {name} | " + " | ".join(f"{sum(f(k, v) for k in scored)} of {len(scored)}" for v in ("now", "message", "combined")) + " |")
for v in ("message", "combined"):
    up = sum(rank(k, v) < rank(k, "now") for k in scored); down = sum(rank(k, v) > rank(k, "now") for k in scored)
    L.append(f"| Compared with now: expected article moved up / down ({v}) | | {up} / {down} |" if v == "message" else
             f"| Compared with now: expected article moved up / down ({v}) | | | {up} / {down} |")
L += ["", "## The subject-line cases from the walkthrough", "", "| Ticket | Subject | Now | Message alone | Combined |", "|---|---|---|---|---|"]
subj = {t.ticket_id: t.subject for t in tickets}
L += [f"| {k} | {subj[k]} | {', '.join(res[k]['now'])} | {', '.join(res[k]['message'])} | {', '.join(res[k]['combined'])} |" for k in CASES]
L += ["", "## Every ticket where combined differs from now", "", "| Ticket | Now | Combined | Expected |", "|---|---|---|---|"]
L += [f"| {k} | {', '.join(res[k]['now'])} | {', '.join(res[k]['combined'])} | {', '.join(sorted(exp[k])) or '-'} |"
      for k in res if res[k]["combined"] != res[k]["now"]]
out = ROOT / "evaluation" / "results" / "compare_search_query.md"
out.write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L[:20]))
print(f"Written: {out}")
