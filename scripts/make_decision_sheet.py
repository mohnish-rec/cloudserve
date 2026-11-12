"""After a run: one spreadsheet with every reply that needs a human decision, so they can be judged together.

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover. Plain code, no model.
Groups (each one a tab):
  1. Refund wording: replies blocked because an article's own words mention refunds (e.g. Ines's proration article).
  2. Agent wording: replies sent with words written for a support agent ("Ask the user ...").
  3. Now with a person: answered automatically in the earlier run, sent to a person in this one.
  4. Now automatic: sent to a person in the earlier run, answered automatically in this one.
The decision columns are for the reviewer. The tool never changes the system.
Run:    python scripts/make_decision_sheet.py evaluation/results/<new>.json evaluation/results/<earlier>.json
Writes: evaluation/human_review/<new>_decisions.xlsx
"""
import json, re, sys
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parent.parent
T = {t["ticket_id"]: t for t in json.loads((ROOT / "data/development_tickets.json").read_text(encoding="utf-8-sig"))}
AGENT = re.compile(r"\b(ask the (user|customer)|the customer should|tell the customer)\b", re.I)


def load(p):
    return {r["ticket_id"]: r for r in json.loads(Path(p).read_text(encoding="utf-8"))["results"]}


def draft(r):
    h = r.get("handover")
    if isinstance(h, dict):
        return h.get("draft") or json.dumps(h, ensure_ascii=False)[:2000]
    return r.get("sent_text") or (str(h) if h else "")


def main(new, old):
    N, O = load(new), load(old)
    groups = {
        "1 Refund wording": ([k for k, r in N.items() if "refund or credit" in json.dumps(r.get("guardrails", {}))],
                             "Send it (Ines's policy, word for word)", "A person handles it"),
        "2 Agent wording": ([k for k, r in N.items() if r["action"] == "auto_respond" and AGENT.search(r["sent_text"] or "")],
                            "Send as it is (word for word)", "A person handles it"),
        "3 Now with a person": ([k for k in N if O.get(k, {}).get("action") == "auto_respond" and N[k]["action"] != "auto_respond"],
                                "Right to send to a person", "Should have been answered"),
        "4 Now automatic": ([k for k in N if k in O and O[k]["action"] != "auto_respond" and N[k]["action"] == "auto_respond"],
                            "Right to answer automatically", "Should have gone to a person"),
    }
    wb = Workbook()
    wb.remove(wb.active)
    head = PatternFill("solid", fgColor="1F3864")
    yellow = PatternFill("solid", fgColor="FFF2CC")
    cols = ["Ticket", "Subject", "What the customer wrote", "Labels say", "Decision now", "Reason", "Reply (sent or drafted)",
            "Your decision", "Why", "Earlier run decision"]
    widths = [11, 24, 45, 22, 14, 45, 70, 30, 40, 14]
    summary = []
    for name, (ids, yes, no) in groups.items():
        ws = wb.create_sheet(name)
        for c, (h, w) in enumerate(zip(cols, widths), 1):
            x = ws.cell(row=1, column=c, value=h)
            x.font, x.fill = Font(bold=True, color="FFFFFF"), head
            x.alignment = Alignment(wrap_text=True, vertical="center")
            ws.column_dimensions[x.column_letter].width = w
        for i, k in enumerate(sorted(ids), 2):
            t, r = T[k], N[k]
            lab = t["labels"]
            vals = [k, t.get("subject") or "(none)", t["body"],
                    f"{lab['expected_route']}; articles {', '.join(lab['expected_doc_ids']) or 'none'}"
                    + ("; MUST NOT auto-answer" if lab.get("must_not_auto_respond") else ""),
                    r["action"], r["reason"], draft(r), "", "", O.get(k, {}).get("action", "")]
            for c, v in enumerate(vals, 1):
                x = ws.cell(row=i, column=c, value=v)
                x.alignment = Alignment(wrap_text=True, vertical="top")
                if c in (8, 9):
                    x.fill = yellow
            ws.row_dimensions[i].height = 220
        if ids:
            dv = DataValidation(type="list", formula1=f'"{yes},{no},Unsure"', allow_blank=True)
            ws.add_data_validation(dv)
            dv.add(f"H2:H{len(ids) + 1}")
        ws.freeze_panes = "C2"
        summary.append((name, len(ids)))
    out = ROOT / "evaluation" / "human_review" / (Path(new).stem + "_decisions.xlsx")
    wb.save(out)
    print(f"Saved {out}")
    for name, n in summary:
        print(f"  {name}: {n} tickets")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
