"""SANDBOX 10 Nov: compare an experiment run with the baseline, on the same tickets.

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
Run:    python scripts/compare_runs.py <baseline.json> <experiment.json>
Writes: <experiment>_vs_baseline.md next to the experiment file, and prints it.
Shows every measure on all shared tickets and, separately, on the 100 hold-out tickets; then every
ticket whose outcome changed. A fix is rejected if any must-not ticket is answered automatically.
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
lab = {t["ticket_id"]: t["labels"] for t in json.loads((ROOT / "data" / "development_tickets.json").read_text(encoding="utf-8-sig"))}
hold_file = ROOT / "evaluation" / "samples" / "holdout_ids.json"
hold = set(json.loads(hold_file.read_text(encoding="utf-8"))) if hold_file.exists() else set()
load = lambda p: {r["ticket_id"]: r for r in json.loads(Path(p).read_text(encoding="utf-8"))["results"]}
b, e = load(sys.argv[1]), load(sys.argv[2])
ids = sorted(set(b) & set(e))


def outcome(r):
    if r["action"] == "auto_respond":
        if "answer library" in r["reason"]:
            return "sent (library)"
        return "sent (trimmed)" if "Trimmed:" in r["reason"] else "sent"
    if r["action"] == "block":
        return "blocked: " + ", ".join(k for k, v in r["guardrails"].items() if str(v).startswith("block"))
    return "safety rule" if "safety rule" in r["reason"] else "to a person"


def score(res, keys):
    sent = [k for k in keys if res[k]["action"] == "auto_respond"]
    agree = [k for k in sent if lab[k]["expected_route"] == "auto_respond"]
    should = [k for k in keys if lab[k]["expected_route"] == "auto_respond"]
    cited = [k for k in sent if lab[k]["expected_doc_ids"]]
    ok = sum(bool(set(lab[k]["expected_doc_ids"]) & set(res[k]["cited"])) for k in cited)
    tok = sum(sum(v for k2, v in res[k].get("tokens", {}).items() if not k2.endswith("cached")) for k in keys)
    pct = lambda a, n: f"{a} of {n} ({a / n:.1%})" if n else "-"
    return {"Answered automatically (FCR)": pct(len(sent), len(keys)),
            "Must-not answered (must be 0)": str(sum(lab[k]["must_not_auto_respond"] for k in sent)),
            "Should-be-automatic answered": pct(len(agree), len(should)),
            "Precision (key agrees with the answer)": pct(len(agree), len(sent)),
            "Citation accuracy (target 95%)": pct(ok, len(cited)),
            "Blocked by a guardrail": str(sum(res[k]["action"] == "block" for k in keys)),
            "Trimmed and sent": str(sum("Trimmed:" in res[k]["reason"] for k in sent)),
            "Sent from the answer library": str(sum("answer library" in res[k]["reason"] for k in sent)),
            "Tokens": f"{tok:,}"}


out = [f"# {Path(sys.argv[2]).name} compared with {Path(sys.argv[1]).name}", ""]
for title, keys in (("All shared tickets", ids), ("Hold-out tickets only (kept out of the quick set)", [k for k in ids if k in hold])):
    if not keys:
        continue
    sb, se = score(b, keys), score(e, keys)
    out += [f"## {title}: {len(keys)}", "", "| Measure | Baseline | Experiment |", "|---|---|---|"]
    out += [f"| {m} | {sb[m]} | {se[m]} |" for m in sb] + [""]
must = [k for k in ids if e[k]["action"] == "auto_respond" and lab[k]["must_not_auto_respond"]]
out += ["**REJECT: a must-not ticket was answered automatically: " + ", ".join(must) + "**" if must
        else "Must-not check: passed (none answered automatically).", ""]
changed = [k for k in ids if outcome(b[k]) != outcome(e[k])]
out += [f"## Tickets whose outcome changed: {len(changed)}", "", "| Ticket | Key says | Baseline | Experiment | Hold-out |", "|---|---|---|---|---|"]
out += [f"| {k} | {lab[k]['expected_route']} | {outcome(b[k])} | {outcome(e[k])} | {'yes' if k in hold else ''} |" for k in changed]
text = "\n".join(out) + "\n"
dest = Path(sys.argv[2]).with_name(Path(sys.argv[2]).stem + "_vs_baseline.md")
dest.write_text(text, encoding="utf-8")
print(text)
