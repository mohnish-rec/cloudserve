"""14 Nov 2026: a fair-size test of the fairness gaps, and a like-for-like check, from an existing run of the 500
development tickets (no model calls, no new run).

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
1. Balanced sample (Mohnish Grover, 14 Nov: 120 tickets): 40 per plan, 30 per region, 60 per fluency, chosen with a
   fixed seed so it can be repeated. Gaps are worked out on that sample.
2. Own percentage first (Mohnish Grover, 14 Nov): for each group on its own, of the tickets that should be answered,
   what share was answered; then those shares are compared. "Should be answered" is measured two ways: by his
   decisions, and by the answer key (used only to measure, never to decide).
3. Inside each category first (Mohnish Grover, 14 Nov): the 22 ticket types, then his 67 questions. For each
   question, did customers in different groups get the same decision? And the gaps if every group had asked the
   same mix of questions (direct standardisation).
The labels are used only to report must-not; groups come from the ticket fields (customer_tier, region, fluency).
Run:    python scripts/fairness_balanced.py <run.json> [--tickets data/development_tickets.json]
Writes: evaluation/results/fairness_balanced.md
"""
import argparse
import json
import random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEED = 42
GROUPS = {"plan": "customer_tier", "region": "customer_region", "fluency": "language_fluency"}
WANT = {"plan": 40, "region": 30, "fluency": 60}

ap = argparse.ArgumentParser()
ap.add_argument("run"); ap.add_argument("--tickets", default=str(ROOT / "data" / "development_tickets.json"))
a = ap.parse_args()
res = {x["ticket_id"]: x for x in json.loads(Path(a.run).read_text(encoding="utf-8"))["results"]}
T = {x["ticket_id"]: x for x in json.loads(Path(a.tickets).read_text(encoding="utf-8"))}
W = json.loads((ROOT / "evaluation" / "human_review" / "dev_walkthrough.json").read_text(encoding="utf-8"))["questions"]
qof = {k: q["question"] for q in W for k in q["tickets"]}
auto = lambda k: res[k]["action"] == "auto_respond"
val = lambda k, g: T[k][GROUPS[g]]
values = {g: sorted({val(k, g) for k in T}) for g in GROUPS}


def miss(sample):
    return sum(abs(sum(val(k, g) == v for k in sample) - WANT[g]) for g in ("region", "fluency") for v in values[g])


rng = random.Random(SEED)
by_plan = {p: sorted(k for k in T if val(k, "plan") == p) for p in values["plan"]}
sample = {k for p in by_plan for k in rng.sample(by_plan[p], WANT["plan"])}
for _ in range(200000):                                  # swap within the same plan until regions and fluency fit
    if miss(sample) == 0:
        break
    p = rng.choice(values["plan"])
    out = rng.choice(sorted(k for k in sample if val(k, "plan") == p))
    inn = rng.choice(sorted(k for k in by_plan[p] if k not in sample))
    new = (sample - {out}) | {inn}
    if miss(new) <= miss(sample):
        sample = new


def rates(keys, g):
    r = {}
    for v in values[g]:
        ks = [k for k in keys if val(k, g) == v]
        r[v] = (sum(map(auto, ks)), len(ks))
    return r


def gap(r, min_n=10):
    p = [100 * x / n for x, n in r.values() if n >= min_n]
    return max(p) - min(p) if len(p) > 1 else 0.0


L = ["# Fairness: a balanced sample and a like-for-like check", "",
     f"Run: {Path(a.run).name}. Development tickets only. Sample seed {SEED}; "
     f"sample fits the target sizes exactly: {'yes' if miss(sample) == 0 else 'no (off by ' + str(miss(sample)) + ')'}.", "",
     "## 1. Gaps: all 500 tickets and the balanced sample of 120", "",
     "| Group | Value | All 500: answered | Sample 120: answered |", "|---|---|---|---|"]
for g in GROUPS:
    ra, rs = rates(T, g), rates(sample, g)
    L += [f"| {g} | {v} | {ra[v][0]} of {ra[v][1]} ({100 * ra[v][0] / ra[v][1]:.1f}%) | "
          f"{rs[v][0]} of {rs[v][1]} ({100 * rs[v][0] / max(rs[v][1], 1):.1f}%) |" for v in values[g]]
L += ["", "| Gap (points, target under 5) | All 500 | Sample 120 | Same question mix (inside each question, 3b) |", "|---|---|---|---|"]

# direct standardisation: every group gets the overall question mix
qn = defaultdict(int)
for k in T:
    qn[qof[k]] += 1
std = {}
for g in GROUPS:
    s = {}
    for v in values[g]:
        tot = 0.0
        for q, n in qn.items():
            ks = [k for k in T if qof[k] == q and val(k, g) == v]
            if not ks:                                   # this group never asked q: use q's overall rate
                ks = [k for k in T if qof[k] == q]
            tot += n * sum(map(auto, ks)) / len(ks)
        s[v] = 100 * tot / sum(qn.values())
    std[g] = max(s.values()) - min(s.values())
for g in GROUPS:
    L.append(f"| {g} | {gap(rates(T, g)):.1f} | {gap(rates(sample, g)):.1f} | {std[g]:.1f} |")

person = {k for q in W if q["decision_13nov"].startswith("Person") for k in q["tickets"]}
key_auto = lambda k: T[k]["labels"]["expected_route"] == "auto_respond" and not T[k]["labels"]["must_not_auto_respond"]
L += ["", "## 2. Own percentage first: of each group's tickets that should be answered, the share answered", "",
      "| Group | Value | Should be answered (his decisions) | Answered | Own % | Should be answered (answer key) | Answered | Own % |",
      "|---|---|---|---|---|---|---|---|"]
own = {}
for g in GROUPS:
    for v in values[g]:
        ks = [k for k in T if val(k, g) == v]
        row = []
        for yard, el in (("decisions", [k for k in ks if k not in person]), ("key", [k for k in ks if key_auto(k)])):
            n_ok = sum(map(auto, el)); pct = 100 * n_ok / len(el) if el else 0.0
            own.setdefault((g, yard), []).append((pct, len(el))); row += [str(len(el)), str(n_ok), f"{pct:.1f}%"]
        L.append(f"| {g} | {v} | " + " | ".join(row) + " |")
L += ["", "| Gap (points, target under 5; groups of 10 or more) | By his decisions | By the answer key |", "|---|---|---|"]
og = lambda g, y: (lambda p: max(p) - min(p))([x for x, n in own[(g, y)] if n >= 10])
L += [f"| {g} | {og(g, 'decisions'):.1f} | {og(g, 'key'):.1f} |" for g in GROUPS]

L += ["", "## 3a. Inside each ticket type: types where groups got different rates", "",
      "| Group | Type | Answered per group | Gap |", "|---|---|---|---|"]
for g in GROUPS:
    flat = 0
    for ty in sorted({res[k]["type"] for k in T}):                  # the type the system decided, not the label
        cells = [(v, [k for k in T if res[k]["type"] == ty and val(k, g) == v]) for v in values[g]]
        p = [100 * sum(map(auto, ks)) / len(ks) for _, ks in cells if ks]
        if max(p) - min(p) == 0:
            flat += 1; continue
        L.append(f"| {g} | {ty} | " + "; ".join(f"{v} {sum(map(auto, ks))}/{len(ks)}" for v, ks in cells) + f" | {max(p) - min(p):.0f} |")
    L.append(f"| {g} | (every other type) | same rate for every group | 0 ({flat} types) |")
L += ["", "A type holds several questions, and he decided some of them differently, so a gap inside a type is "
      "which question each customer asked. His questions are the right category (3b).", ""]
L += ["## 3b. Inside each of his questions: questions where groups got different decisions", "",
      "Every question below had at least one ticket answered and at least one sent to a person.", "",
      "| Question | Tickets | Answered | Not answered (ticket: plan, region, fluency: why) |", "|---|---|---|---|"]
same = 0
for q in W:
    ks = q["tickets"]
    if len({auto(k) for k in ks}) == 1:
        same += 1; continue
    odd = [k for k in ks if auto(k) != (sum(map(auto, ks)) * 2 > len(ks))]
    L.append(f"| {q['question']} {q['title']} | {len(ks)} | {sum(map(auto, ks))} | " + "; ".join(
        f"{k}: {val(k, 'plan')}, {val(k, 'region')}, {val(k, 'fluency')}: {res[k]['reason'][:90]}" for k in odd) + " |")
L += ["", f"Questions where every ticket got the same decision, whatever the group: **{same} of {len(W)}**.", "",
      f"Must-not tickets answered in the sample: {sum(auto(k) and T[k]['labels']['must_not_auto_respond'] for k in sample)}.", "",
      "Sample: " + ", ".join(sorted(sample))]
out = ROOT / "evaluation" / "results" / "fairness_balanced.md"
out.write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L[:-1]))
