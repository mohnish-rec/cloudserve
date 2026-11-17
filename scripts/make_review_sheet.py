"""Build the human review sheets (Evaluation Framework: hallucination rate and customer-satisfaction proxy).

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
"Sample at least fifty responses, have two people assess them independently, and report your
agreement rate." 50 replies the system actually sent, drawn at random (seed 42) from the final
development run (10 Nov 2026: trim, prompt v1.3, answer library, narrowed rules; 500 tickets). Each assessor gets an
identical copy and fills it in without seeing the other's.

Run:    python scripts/make_review_sheet.py
Writes: evaluation/human_review/review_assessor_1.xlsx and review_assessor_2.xlsx
Also:   python scripts/make_review_sheet.py --results validation_run_3.json --tickets validation_tickets.json --all
        (10 Nov, the user's choice: a performance check, never tuning) EVERY reply sent in that run, written to
        evaluation/human_review/<results file name>/ 
"""
import json
import random
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parent.parent
import sys  # noqa: E402
sys.path.insert(0, str(ROOT / "scripts"))
from review_rubric import V4, V2_HOW_MADE  # noqa: E402  the shared rubric (PR-03 v4)
RES = ROOT / "evaluation" / "results"
COLUMNS = [
    ("A. Does any sentence say something the cited article does not support?", ["Yes", "No"]),
    ("B. Is every bullet under the heading of the article it comes from?", ["All", "Some", "None"]),   # rubric v2 (12 Nov)
    ("C. Would this reply let the customer solve their problem? (see the scale on 'How to review')", ["1", "2", "3", "4", "5"]),
    ("D. Is the tone right for a paying customer?", ["Yes", "No"]),
    ("E. Anything that must never be sent? (private data, a promise, wrong situation)", ["Yes", "No"]),
]


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="sandbox_dev500_final.json")
    ap.add_argument("--tickets", default="development_tickets.json")
    ap.add_argument("--all", action="store_true", help="every sent reply instead of a random 50")
    a = ap.parse_args()
    out_dir = ROOT / "evaluation" / "human_review" / (Path(a.results).stem if a.all else "")
    out_dir.mkdir(parents=True, exist_ok=True)
    results = {r["ticket_id"]: r for r in json.loads((RES / a.results).read_text(encoding="utf-8"))["results"]}
    refs = {g["ticket_id"]: g for g in json.loads((ROOT / "data" / "ground_truth_responses.json").read_text(encoding="utf-8-sig"))}
    tickets = {t["ticket_id"]: t for t in json.loads((ROOT / "data" / a.tickets).read_text(encoding="utf-8-sig"))}
    docs = {d["doc_id"]: d for d in json.loads((ROOT / "data" / "documentation.json").read_text(encoding="utf-8-sig"))}
    sent = sorted(tid for tid, r in results.items() if r["action"] == "auto_respond")
    sample = sent if a.all else sorted(random.Random(42).sample(sent, 50))
    n = len(sample)

    for k in (1, 2):
        wb = Workbook()
        ws = wb.active
        ws.title = "Review"
        head = ["#", "Ticket ID", "Customer's ticket", "Reply the system sent", "Article(s) it cited",
                "Senior agent's reference answer (where one exists)"] + \
               [c for c, _ in COLUMNS] + ["Notes (optional)"]
        ws.append(head)
        for i, tid in enumerate(sample, 1):
            t, r = tickets[tid], results[tid]
            arts = "\n\n".join(f"[{n}] {d} · {docs[d]['title']}\n{docs[d]['content']}" for n, d in enumerate(r["cited"], 1)
                               if d in docs)
            g = refs.get(tid)
            ref = (f"{g['reference_response']}\n\nMUST MENTION: {', '.join(g.get('must_mention', []))}"
                   f"\nMUST NOT CLAIM: {', '.join(g.get('must_not_claim', []))}") if g else "(no reference for this ticket)"
            ws.append([i, tid, f"{t.get('subject') or ''}\n{t.get('body') or ''}".strip(), r["sent_text"], arts, ref])
        widths = [4, 11, 40, 60, 70, 50, 22, 22, 22, 18, 22, 30]
        for col, w in enumerate(widths, 1):
            ws.column_dimensions[ws.cell(1, col).column_letter].width = w
        for row in ws.iter_rows(min_row=1, max_row=n + 1):
            for cell in row:
                cell.alignment = Alignment(wrap_text=True, vertical="top")
        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="14213D")
        for j, (_, choices) in enumerate(COLUMNS):
            col = ws.cell(1, 7 + j).column_letter
            dv = DataValidation(type="list", formula1='"' + ",".join(choices) + '"', allow_blank=True)
            dv.add(f"{col}2:{col}{n + 1}")
            ws.add_data_validation(dv)
            for row in range(2, n + 2):
                ws[f"{col}{row}"].fill = PatternFill("solid", fgColor="FFF4D6")
        ws.freeze_panes = "G2"
        guide = wb.create_sheet("How to review")
        for line in [
            f"Assessor {k}. Fill in the yellow cells for all {n} replies. Do not look at the other assessor's sheet.",
            "Read the customer's ticket, then the reply, then the article(s) it cites.",
            "Rubric v4 (17 Nov 2026, PR-03):",
            *([V2_HOW_MADE] + V4),
            "A gives the hallucination rate (target 5% or lower); C is the customer-satisfaction proxy (target 4.0 or better).",
            (f"Every reply the system sent in {a.results} ({n} replies): a performance check on tickets the system "
             f"never learned from. Nothing in the system is changed because of this review." if a.all else
             "Sample: 50 replies the system sent, chosen at random (seed 42) from the final run of 500 development "
             "tickets (10 Nov 2026).") + " How each reply was produced (written, trimmed or from the answer library) "
            "is deliberately not shown, so it cannot sway the review.",
        ]:
            guide.append([line])
        guide.column_dimensions["A"].width = 140
        out = out_dir / f"review_assessor_{k}.xlsx"
        wb.save(out)
        print(f"wrote {out.relative_to(ROOT)}")
    (out_dir / "sample_ids.json").write_text(json.dumps(sample, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
