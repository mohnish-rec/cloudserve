"""Build the human review sheets (Evaluation Framework: hallucination rate and customer-satisfaction proxy).

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
"Sample at least fifty responses, have two people assess them independently, and report your
agreement rate." 50 replies the system actually sent, drawn at random (seed 42) from the full
development run (the 500 tickets, with the D-022 re-run replacing its 50 tickets). Each assessor gets an
identical copy and fills it in without seeing the other's.

Run:    python scripts/make_review_sheet.py
Writes: evaluation/human_review/review_assessor_1.xlsx and review_assessor_2.xlsx
"""
import json
import random
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "evaluation" / "results"
COLUMNS = [
    ("A. Does any sentence say something the cited article does not support?", ["Yes", "No"]),
    ("B. Do the citations [1], [2] support the sentences they are attached to?", ["All", "Some", "None"]),
    ("C. Would this reply solve the customer's problem? (1 = not at all, 5 = fully)", ["1", "2", "3", "4", "5"]),
    ("D. Is the tone right for a paying customer?", ["Yes", "No"]),
    ("E. Anything that must never be sent? (private data, a promise, wrong situation)", ["Yes", "No"]),
]


def main():
    results = {r["ticket_id"]: r for r in json.loads((RES / "dev_all_run.json").read_text(encoding="utf-8"))["results"]}
    rerun = RES / "dev_word_blocked_rerun.json"
    if rerun.exists():
        results.update({r["ticket_id"]: r for r in json.loads(rerun.read_text(encoding="utf-8"))["results"]})
    tickets = {t["ticket_id"]: t for t in json.loads((ROOT / "data" / "development_tickets.json").read_text(encoding="utf-8-sig"))}
    docs = {d["doc_id"]: d for d in json.loads((ROOT / "data" / "documentation.json").read_text(encoding="utf-8-sig"))}
    sent = sorted(tid for tid, r in results.items() if r["action"] == "auto_respond")
    sample = sorted(random.Random(42).sample(sent, 50))

    for k in (1, 2):
        wb = Workbook()
        ws = wb.active
        ws.title = "Review"
        head = ["#", "Ticket ID", "Customer's ticket", "Reply the system sent", "Article(s) it cited"] + \
               [c for c, _ in COLUMNS] + ["Notes (optional)"]
        ws.append(head)
        for i, tid in enumerate(sample, 1):
            t, r = tickets[tid], results[tid]
            arts = "\n\n".join(f"[{n}] {d} · {docs[d]['title']}\n{docs[d]['content']}" for n, d in enumerate(r["cited"], 1)
                               if d in docs)
            ws.append([i, tid, f"{t.get('subject') or ''}\n{t.get('body') or ''}".strip(), r["sent_text"], arts])
        widths = [4, 11, 40, 60, 70, 22, 22, 22, 18, 22, 30]
        for col, w in enumerate(widths, 1):
            ws.column_dimensions[ws.cell(1, col).column_letter].width = w
        for row in ws.iter_rows(min_row=1, max_row=51):
            for cell in row:
                cell.alignment = Alignment(wrap_text=True, vertical="top")
        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="14213D")
        for j, (_, choices) in enumerate(COLUMNS):
            col = ws.cell(1, 6 + j).column_letter
            dv = DataValidation(type="list", formula1='"' + ",".join(choices) + '"', allow_blank=True)
            dv.add(f"{col}2:{col}51")
            ws.add_data_validation(dv)
            for row in range(2, 52):
                ws[f"{col}{row}"].fill = PatternFill("solid", fgColor="FFF4D6")
        ws.freeze_panes = "F2"
        guide = wb.create_sheet("How to review")
        for line in [
            f"Assessor {k}. Fill in the yellow cells for all 50 replies. Do not look at the other assessor's sheet.",
            "Read the customer's ticket, then the reply, then the article(s) it cites.",
            "A: Yes if ANY sentence states something the cited article does not say (a step, number, promise or fact). "
            "This is the hallucination rate: target 5% or lower.",
            "B: for every [n], does that article actually support the sentence it is attached to? All, Some or None.",
            "C: as the customer, would this reply solve your problem? 1 not at all, 3 partly, 5 fully. "
            "This is the customer-satisfaction proxy.",
            "D: polite, clear and right for a paying business customer?",
            "E: Yes if it contains private data, a promise (refund, fix, date), or answers a different situation.",
            "Judge the reply as written; the ending 'This reply was written automatically…' is added on purpose.",
            "Sample: 50 replies the system sent, chosen at random (seed 42) from the full run of 500 development tickets.",
        ]:
            guide.append([line])
        guide.column_dimensions["A"].width = 140
        out = ROOT / "evaluation" / "human_review" / f"review_assessor_{k}.xlsx"
        wb.save(out)
        print(f"wrote {out.relative_to(ROOT)}")
    (ROOT / "evaluation" / "human_review" / "sample_ids.json").write_text(json.dumps(sample, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
