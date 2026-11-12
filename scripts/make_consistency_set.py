"""A5 consistency test set (12 Nov 2026): 10 development tickets, each repeated 10 times = 100 tickets.

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
Build Specification A5: "Routing applies a threshold you set, and the same input produces the same routing decision."
The 10 cover answered, escalated and blocked outcomes, fluent and non-fluent, and include DEV-0156, whose identical
twin DEV-0399 was routed differently in the final development run. Copies get new ticket ids (CONS-<source>-<n>).
Run:    python scripts/make_consistency_set.py
        python -m src.run_evaluation data/consistency_10x10.json evaluation/results/consistency_run_1.json
        python -m src.run_evaluation data/consistency_10x10.json evaluation/results/consistency_run_2.json
        python scripts/check_consistency.py
"""
import copy, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PICK = ["DEV-0156", "DEV-0004", "DEV-0035", "DEV-0061", "DEV-0089", "DEV-0102", "DEV-0209", "DEV-0281", "DEV-0450", "DEV-0016"]
T = {t["ticket_id"]: t for t in json.loads((ROOT / "data" / "development_tickets.json").read_text(encoding="utf-8-sig"))}
out = []
for n in range(10):
    for k in PICK:
        t = copy.deepcopy(T[k])
        t["ticket_id"], t["source_ticket"] = f"CONS-{k[4:]}-{n:02d}", k
        out.append(t)
(ROOT / "data" / "consistency_10x10.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"wrote data/consistency_10x10.json: {len(out)} tickets ({len(PICK)} tickets x 10, interleaved)")
