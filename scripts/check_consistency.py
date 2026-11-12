"""A5 check (12 Nov 2026): within each run, do all 10 copies of a ticket get the same decision; and across the two
runs? Plain code, no model. Run after the two consistency runs (see scripts/make_consistency_set.py)."""
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
runs = {}
for n in (1, 2):
    p = ROOT / "evaluation" / "results" / f"consistency_run_{n}.json"
    if p.exists():
        runs[n] = {r["ticket_id"]: r for r in json.loads(p.read_text(encoding="utf-8"))["results"]}
L = ["# A5 consistency check: 10 tickets x 10 copies", "",
     "| Source ticket | Run 1 decisions | Same in run 1? | Run 2 decisions | Same in run 2? | Same across runs? |", "|---|---|---|---|---|---|"]
ok_in, ok_across = 0, 0
srcs = sorted({k.split("-")[1] for k in next(iter(runs.values()))})
for s in srcs:
    cells, sets = [], []
    for n in (1, 2):
        if n in runs:
            acts = [v["action"] for k, v in runs[n].items() if k.split("-")[1] == s]
            same = len(set(acts)) == 1
            ok_in += same
            sets.append(set(acts))
            cells += [", ".join(f"{a} x{acts.count(a)}" for a in sorted(set(acts))), "yes" if same else "NO"]
        else:
            cells += ["-", "-"]
    across = len(sets) == 2 and sets[0] == sets[1] and len(sets[0]) == 1
    ok_across += across
    L.append(f"| DEV-{s} | {' | '.join(cells)} | {'yes' if across else ('NO' if len(sets) == 2 else '-')} |")
L += ["", f"Same decision for all 10 copies within a run: {ok_in} of {len(srcs) * len(runs)}.",
      f"Same decision across the two runs: {ok_across} of {len(srcs)}." if len(runs) == 2 else ""]
out = ROOT / "evaluation" / "results" / "consistency_check.md"
out.write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L))
