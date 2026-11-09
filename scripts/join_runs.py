"""Join the results of several runs (e.g. the 5 development parts) into one results file.

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
Also counts tickets whose reply could not be written because the model was unavailable,
so a run hit by the daily limit is spotted rather than mistaken for a real result.

Run:    python scripts/join_runs.py evaluation/results/dev_all_run.json evaluation/results/dev_part_*_run.json
"""
import glob
import json
import sys
from pathlib import Path

out, patterns = sys.argv[1], sys.argv[2:]
files = sorted({f for p in patterns for f in glob.glob(p)})
results, metas = [], []
for f in files:
    data = json.loads(Path(f).read_text(encoding="utf-8"))
    results += data["results"]
    metas.append(data["meta"])
unavailable = [r["ticket_id"] for r in results if "model unavailable" in json.dumps(r)]
Path(out).write_text(json.dumps({"meta": {"joined_from": [Path(f).name for f in files], "runs": metas},
                                 "results": results}, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"joined {len(files)} runs, {len(results)} tickets -> {out}")
print(f"tickets hit by 'model unavailable': {len(unavailable)} {unavailable[:10]}")
