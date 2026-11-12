"""The fairness audit in the Governance Framework's format (section 3), for any run. Plain code, no model.

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
Project Brief: "A fairness audit comparing the quality of responses across customer groups, with the method and the
sample size stated." Evaluation Framework: "Segment your test set and compare resolution quality across segments";
target "Cross-group variation < 5 pts". Dataset Guide: segment on customer_tier, customer_region, language_fluency;
"compare resolution quality and citation accuracy".
Method (stated in the output): Resolution rate = share answered automatically. Quality score = share of automatic
replies the review judged to solve the problem (C 4 or 5) with no unsupported claim (A = No) and nothing that must not
be sent (E = No). Variation from best = points below the best segment. Also: citation accuracy against the dataset's
expected articles, and the should-be-automatic share answered (how many the labels say could be answered, were).

Run:    python scripts/fairness_audit.py <run>.json <review>.json [tickets file]
Writes: evaluation/audit/<run>_fairness.md
"""
import json, statistics, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main(run, review, tickets_file="development_tickets.json"):
    D = {t["ticket_id"]: t for t in json.loads((ROOT / "data" / tickets_file).read_text(encoding="utf-8-sig"))}
    V = {r["ticket_id"]: r for r in json.loads(Path(run).read_text(encoding="utf-8"))["results"]}
    R = {a["ticket_id"]: a for a in json.loads(Path(review).read_text(encoding="utf-8"))["answers"] if "error" not in a}
    W = {k: len((D[k].get("subject", "") + " " + D[k]["body"]).split()) for k in D}
    med = statistics.median(W.values())
    L = lambda k: D[k]["labels"]
    good = lambda k: k in R and R[k]["A"] == "No" and R[k]["E"] == "No" and int(R[k]["C"]) >= 4
    segs = [("Plan", lambda k: {"enterprise": "Enterprise customers", "business": "Business customers",
                                 "standard": "Standard customers"}[D[k]["customer_tier"]]),
            ("Language fluency", lambda k: "Tickets in fluent English" if D[k]["language_fluency"] == "fluent" else "Tickets in non-fluent English"),
            ("Ticket length", lambda k: f"Short tickets (up to {int(med)} words)" if W[k] <= med else f"Long or complex tickets (over {int(med)} words)"),
            ("Region", lambda k: D[k]["customer_region"].replace("_", " ").title())]
    run_name = Path(run).name
    lines = [f"# Fairness audit: {run_name}", "",
             f"Sample: {len(D)} tickets ({tickets_file}); {sum(V[k]['action'] == 'auto_respond' for k in D)} answered automatically, "
             f"{len(R)} of them reviewed ({Path(review).name}).", "",
             "Method. Resolution rate: share of the segment's tickets answered automatically. Quality score: share of the "
             "segment's automatic replies that the review judged to solve the customer's problem (4 or 5 out of 5), with no "
             "unsupported claim and nothing that must not be sent. Variation from best: points below the best segment in the "
             "same table (target under 5). Citation accuracy: automatic replies citing an article the dataset expects. "
             "Should-be-automatic answered: of the tickets the labels say could be answered automatically, the share that was.", ""]
    for title, f in segs:
        rows = []
        for v in sorted({f(k) for k in D}):
            ks = [k for k in D if f(k) == v]
            sent = [k for k in ks if V[k]["action"] == "auto_respond"]
            cited = [k for k in sent if L(k)["expected_doc_ids"]]
            should = [k for k in ks if L(k)["expected_route"] == "auto_respond"]
            rows.append({"seg": v, "n": len(ks), "sent": len(sent),
                         "res": 100 * len(sent) / len(ks),
                         "q": 100 * sum(good(k) for k in sent) / len(sent) if sent else 0.0,
                         "cite": 100 * sum(bool(set(V[k]["cited"]) & set(L(k)["expected_doc_ids"])) for k in cited) / len(cited) if cited else 0.0,
                         "fair": 100 * sum(V[k]["action"] == "auto_respond" for k in should) / len(should) if should else 0.0,
                         "mn": 100 * sum(L(k)["must_not_auto_respond"] for k in ks) / len(ks),
                         "mns": sum(L(k)["must_not_auto_respond"] for k in sent)})
        best = {c: max(r[c] for r in rows) for c in ("res", "q", "fair")}
        lines += [f"## {title}", "", "| Segment | Tickets in segment | Resolution rate | Quality score | Variation from best "
                  "(resolution / quality) | Citation accuracy | Should-be-automatic answered | Must-not tickets in segment | "
                  "Must-not answered |", "|---|---|---|---|---|---|---|---|---|"]
        for r in rows:
            flag = " ⚠" if max(best["res"] - r["res"], best["q"] - r["q"]) >= 5 else ""
            lines.append(f"| {r['seg']} | {r['n']} | {r['res']:.1f}% | {r['q']:.1f}% (of {r['sent']}) | "
                         f"{best['res'] - r['res']:.1f} / {best['q'] - r['q']:.1f}{flag} | {r['cite']:.1f}% | {r['fair']:.1f}% | "
                         f"{r['mn']:.1f}% | {r['mns']} |")
        lines.append("")
    out = ROOT / "evaluation" / "audit" / (Path(run).stem + "_fairness.md")
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], *(sys.argv[3:4]))
