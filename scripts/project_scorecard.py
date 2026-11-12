"""The Evaluation Framework's results table for one run, measured the way the project defines each measure.

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover. Plain code, no model.
Definitions (Project Brief / Evaluation Framework): first contact resolution = tickets closed without escalation
/ total; escalation rate = tickets passed to a person / total; time to first reply = arrival to reply (here the
system's processing time); satisfaction proxy = mean 1-5 rating across reviewed replies (method stated);
classification precision per class; hallucination rate = share of reviewed replies with a claim the cited source
does not support; citation accuracy = share whose citations support their sentences; latency 95th percentile end to
end; private data occurrences in outbound text; cross-group variation in resolution and quality (with sample sizes);
decision logging reconciles; confidence calibration by bin. Every rate carries a 95% interval (Wilson), because the
Submission Guide asks for uncertainty to be stated.
Run:    python scripts/project_scorecard.py evaluation/results/<run>.json <tickets file> [<review json>]
Writes: evaluation/scorecards/<run>_scorecard.md
"""
import json, math, re, statistics, sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def wilson(k, n, z=1.96):
    if n == 0:
        return "-"
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return f"{100 * (c - h):.1f}-{100 * (c + h):.1f}%"


def pct(k, n):
    return f"{100 * k / n:.1f}%" if n else "-"


def main(run, tickets_file, review=None):
    res = json.loads(Path(run).read_text(encoding="utf-8"))
    R = {r["ticket_id"]: r for r in res["results"]}
    T = {t["ticket_id"]: t for t in json.loads((ROOT / "data" / tickets_file).read_text(encoding="utf-8-sig"))}
    A = {}
    if review:
        rv = json.loads(Path(review).read_text(encoding="utf-8"))
        A = {a["ticket_id"]: a for a in rv["answers"] if "error" not in a}
    n = len(T)
    auto = [k for k in T if R[k]["action"] == "auto_respond"]
    rev = [k for k in auto if k in A]
    lat = sorted(R[k]["latency_ms"] / 1000 for k in T)
    p95 = lat[max(0, math.ceil(0.95 * len(lat)) - 1)]
    has_labels = all("labels" in t for t in T.values())
    rows = [("First contact resolution", "42%", "60% or better", pct(len(auto), n), wilson(len(auto), n),
             f"{len(auto)} of {n} closed without a person"),
            ("Mean time to first reply", "8 to 12 hrs", "under 5 min", f"{statistics.mean(lat):.1f} s",
             f"median {statistics.median(lat):.1f} s", "system processing time; tickets sent to a person get an immediate holding reply"),
            ("Escalation rate", "58%", "30% or lower", pct(n - len(auto), n), wilson(n - len(auto), n),
             f"{n - len(auto)} of {n} passed to a person")]
    if rev:
        C = [int(A[k]["C"]) for k in rev]
        m, sd = statistics.mean(C), (statistics.stdev(C) if len(C) > 1 else 0)
        hal = sum(A[k]["A"] != "No" for k in rev)
        cit = sum(A[k]["B"] == "All" for k in rev)
        rows.append(("Satisfaction proxy", "3.2 / 5", "4.0 or better", f"{m:.2f}",
                     f"{m - 1.96 * sd / math.sqrt(len(C)):.2f}-{m + 1.96 * sd / math.sqrt(len(C)):.2f}",
                     f"mean of review question C over {len(C)} replies ({rv.get('model', '?')}, rubric {rv.get('rubric', 'v1')})"))
    if has_labels:
        per = defaultdict(lambda: [0, 0])
        for k in T:
            pred = R[k]["type"]
            per[pred][1] += 1
            per[pred][0] += pred == T[k]["labels"]["intent"]
        worst = min(per.items(), key=lambda x: x[1][0] / x[1][1])
        allp = sum(v[0] for v in per.values()) / sum(v[1] for v in per.values())
        rows.append(("Classification precision", "-", "85% or better", f"{100 * allp:.1f}% (lowest class {100 * worst[1][0] / worst[1][1]:.0f}%)",
                     wilson(sum(v[0] for v in per.values()), n), f"per class over {len(per)} predicted types; lowest: {worst[0]}"))
    if rev:
        rows.append(("Hallucination rate", "-", "5% or lower", pct(hal, len(rev)), wilson(hal, len(rev)),
                     f"review question A over {len(rev)} replies (the framework asks for human review of at least 50, two assessors)"))
        rows.append(("Citation accuracy", "-", "95% or better", pct(cit, len(rev)), wilson(cit, len(rev)),
                     "review question B: the cited article supports what is attributed to it"))
    if has_labels:
        ck = [k for k in auto if T[k]["labels"].get("expected_doc_ids")]
        ok = sum(bool(set(T[k]["labels"]["expected_doc_ids"]) & set(R[k]["cited"] or [])) for k in ck)
        rows.append(("Citation accuracy (expected articles)", "-", "95% or better", pct(ok, len(ck)), wilson(ok, len(ck)),
                     "Dataset Guide: did you cite the document that actually answers this?"))
    rows.append(("Latency, 95th percentile", "-", "under 3 s", f"{p95:.1f} s", f"median {statistics.median(lat):.1f} s",
                 "end to end, including retrieval and both model calls"))
    pii = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+|\+?\d[\d \-()]{8,}\d|\b(?:\d[ -]?){13,16}\b|\b(sk|pk|gsk|ghp|AKIA)[-_][A-Za-z0-9_-]{8,}")
    leaks = [k for k in auto if pii.search(R[k]["sent_text"] or "")]
    rows.append(("Private data occurrences", "-", "0", str(len(leaks)), "-", "automated scan of every outbound reply"))
    if has_labels:
        mn = [k for k in T if T[k]["labels"].get("must_not_auto_respond")]
        rows.append(("Must-not tickets answered automatically", "-", "0", f"{sum(k in auto for k in mn)} of {len(mn)}", "-",
                     "labels: must_not_auto_respond"))
    good = (lambda k: A[k]["A"] == "No" and A[k]["E"] == "No" and int(A[k]["C"]) >= 4)
    seg = []
    worst_gap = 0
    for f, name in [("customer_tier", "Plan"), ("language_fluency", "Fluency"), ("customer_region", "Region")]:
        vals = sorted({T[k][f] for k in T})
        resr = {v: (sum(k in auto for k in T if T[k][f] == v), sum(1 for k in T if T[k][f] == v)) for v in vals}
        qual = {v: (sum(good(k) for k in rev if T[k][f] == v), sum(1 for k in rev if T[k][f] == v)) for v in vals} if rev else {}
        rbest = max(a / b for a, b in resr.values())
        for v in vals:
            a, b = resr[v]
            q = qual.get(v, (0, 0))
            seg.append(f"| {name} | {v} | {b} | {pct(a, b)} | {pct(*q) if q[1] else '-'} (of {q[1]}) | {100 * (rbest - a / b):.1f} |")
        gap = 100 * (rbest - min(a / b for a, b in resr.values()))
        worst_gap = max(worst_gap, gap)
    rows.append(("Cross-group variation (resolution)", "-", "under 5 pts", f"{worst_gap:.1f} pts", "-",
                 "largest best-minus-worst gap across plan, fluency and region; sample sizes in the table below"))
    bins = defaultdict(lambda: [0, 0, 0.0])
    if has_labels:
        for k in T:
            c = R[k].get("confidence") or 0
            b = min(int(c * 10), 9) / 10
            bins[b][0] += 1
            bins[b][1] += R[k]["type"] == T[k]["labels"]["intent"]
            bins[b][2] += c
        cal = max(abs(100 * v[1] / v[0] - 100 * v[2] / v[0]) for v in bins.values())
        rows.append(("Confidence calibration", "-", "within 5 pts", f"{cal:.1f} pts", "-", "largest gap between stated confidence and observed accuracy, by tenth"))
    mfile = Path(run).with_name(Path(run).stem + "_metrics.md")
    log = re.search(r"Decisions logged:\*\* (.*)", mfile.read_text(encoding="utf-8")).group(1) if mfile.exists() else "see the run report"
    rows.append(("Decision logging", "-", "complete coverage", log, "-", "logged decisions against processed tickets"))
    L = [f"# Scorecard: {Path(run).name} ({tickets_file}, {n} tickets)", "",
         f"System: {res['meta'].get('prompts', '')}; {res['meta'].get('experiment', '')}; run {res['meta'].get('date', '')[:16]}.", "",
         "| Measure | Baseline | Target | Achieved | Confidence (95%) | Notes |", "|---|---|---|---|---|---|"]
    L += [f"| {a} | {b} | {c} | {d} | {e} | {f} |" for a, b, c, d, e, f in rows]
    L += ["", "## Customer groups (sample size stated)", "",
          "| Group | Segment | Tickets | Resolution rate | Quality score | Points below best (resolution) |", "|---|---|---|---|---|---|"] + seg
    L += ["", "Quality score: share of the segment's reviewed automatic replies with no unsupported claim (A = No), nothing "
          "that must not be sent (E = No) and a rating of 4 or 5 (C). Repeat contacts are not measured here: they need "
          "tickets from the same customer over seven days."]
    out = ROOT / "evaluation" / "scorecards" / (Path(run).stem + "_scorecard.md")
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main(*sys.argv[1:4])
