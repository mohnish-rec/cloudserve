"""Exit with code 1 if any ticket in a run could not reach the model (e.g. the daily limit ran out).

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
Used between the parts of a long unattended run, so a part hit by the limit is waited for and
re-run instead of its results being mistaken for real ones.
Run: python scripts/check_run.py evaluation/results/dev_part_1_run.json
"""
import json
import sys
from pathlib import Path

results = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["results"]
bad = [r["ticket_id"] for r in results if "model unavailable" in json.dumps(r)]
print(f"{Path(sys.argv[1]).name}: {len(results)} tickets, {len(bad)} with the model unavailable {bad[:5]}")
sys.exit(1 if bad else 0)
