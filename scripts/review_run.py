"""List what needs a person's eye after a run: guardrail blocks, slip-throughs and lost answers.

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
Reads a run's results and the ticket file's answer key (only to mark the run).

Run:    python scripts/review_run.py <ticket file> <results file>
e.g.    python scripts/review_run.py evaluation/samples/dev_sample_80.json evaluation/results/dev_sample_run.json
Writes: <results file without .json>_review.md
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main(ticket_path, results_path):
    tickets = {t["ticket_id"]: t for t in json.loads(Path(ticket_path).read_text(encoding="utf-8-sig"))}
    results = json.loads(Path(results_path).read_text(encoding="utf-8"))["results"]
    blocks, slips, lost = [], [], []
    for r in results:
        t, lab = tickets[r["ticket_id"]], tickets[r["ticket_id"]].get("labels", {})
        text = f"{t.get('subject') or ''} {t.get('body') or ''}".strip()
        head = f"### {r['ticket_id']} · {lab.get('intent')} · key says {lab.get('expected_route')}\n\n**Ticket:** {text}\n"
        if r["action"] == "block":
            fired = {k: v for k, v in r["guardrails"].items() if v.startswith(("block", "error"))}
            draft = (r.get("handover") or {}).get("draft", "")
            blocks.append(head + f"\n**Blocked by:** {fired}\n\n**The blocked reply:** {draft or '(not kept)'}\n\n"
                          "**Your verdict:** right block / false alarm\n")
        elif r["action"] == "auto_respond" and lab.get("expected_route") == "escalate":
            slips.append(head + f"\n**Answerable from articles (key):** {lab.get('answerable_from_docs')} · "
                         f"**cited:** {r['cited']}\n\n**Sent:** {r['sent_text']}\n\n**Your verdict:** harmful / "
                         "acceptable / good\n")
        elif r["action"] != "auto_respond" and lab.get("expected_route") == "auto_respond":
            lost.append(f"- {r['ticket_id']} ({lab.get('intent')}): {r['reason'][:220]}")
    out = Path(results_path).with_name(Path(results_path).stem + "_review.md")
    out.write_text("\n".join([f"# Review: {Path(results_path).name}", "",
                              f"{len(blocks)} guardrail blocks, {len(slips)} slip-throughs, "
                              f"{len(lost)} should-be-automatic tickets sent to a person.", "",
                              "## 1. Guardrail blocks: right block or false alarm?", "", *blocks,
                              "## 2. Slip-throughs: answered although the answer key says a person", "", *slips,
                              "## 3. Should-be-automatic tickets sent to a person", "", *lost]) + "\n",
                   encoding="utf-8")
    print(f"{len(blocks)} blocks, {len(slips)} slip-throughs, {len(lost)} lost. written: {out}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
