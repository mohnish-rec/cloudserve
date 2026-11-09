"""Split the 500 development tickets into 5 parts of 100, so a full run can stop and continue safely.

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
A full run is about 400 model calls; if the free tier's daily limit runs out mid-run, every
later ticket fails the model call. In parts, nothing done is lost and each part is checked.

Run:    python scripts/split_dev.py
Writes: evaluation/samples/dev_part_1.json ... dev_part_5.json (in the original order)
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
tickets = json.loads((ROOT / "data" / "development_tickets.json").read_text(encoding="utf-8-sig"))
for k in range(5):
    out = ROOT / "evaluation" / "samples" / f"dev_part_{k + 1}.json"
    out.write_text(json.dumps(tickets[k * 100:(k + 1) * 100], indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)} ({len(tickets[k * 100:(k + 1) * 100])} tickets)")
