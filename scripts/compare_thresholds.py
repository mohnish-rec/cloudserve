"""Compare confidence thresholds for routing (decision D-019).

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
Module 4's method: development tickets only (validation is never used for tuning),
out-of-fold predictions from the chosen classifier (D-018: embeddings, C = 10), so
every ticket is judged by a model that never saw its question, and recall first:
the threshold must first let no must-not ticket through, and only then is the
highest share of automatic answers taken.

A ticket is answered automatically only when ALL of these hold:
  1. no safety rule fires and the predicted type is not person-only (FR-03);
  2. search finds a relevant article (best match at least 0.35, D-017);
  3. the classifier's confidence is at least the threshold (FR-06).
Everything else goes to a person, labelled (FR-07):
  "Draft ready: check and send"  - safe and an article was found, only confidence was too low;
  "Needs a specialist"           - a safety rule fired, the type is person-only, or no article.

Run:    python scripts/compare_thresholds.py
Writes: evaluation/results/threshold_comparison.md
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from src.classify import TicketClassifier, question_groups  # noqa: E402
from src.ingest import load_tickets  # noqa: E402
from src.retrieve import Retriever  # noqa: E402
from src.safety import check  # noqa: E402
from train_classifier import cross_validate  # noqa: E402

DATA = ROOT / "data" / "development_tickets.json"
FEATURES, C = "embeddings", 10.0                       # D-018
THRESHOLDS = [0.50, 0.60, 0.70, 0.80, 0.85, 0.90, 0.95, 0.98]   # 0.80 is the Setup Guide's default
SEGMENTS = ["customer_tier", "customer_region", "language_fluency"]
CHOSEN = 0.85                                          # D-019 (Mohnish's choice, 7 Nov 2026)


def largest_gap(rate_by_group):
    rates = [r for r, n in rate_by_group.values() if n >= 10]   # groups of at least 10 tickets
    return (max(rates) - min(rates)) if len(rates) > 1 else 0.0


def step(message):
    print(message, flush=True)


def main():
    step("1/4 loading tickets")
    tickets = load_tickets(DATA)
    raw = {t["ticket_id"]: t for t in json.loads(DATA.read_text(encoding="utf-8-sig"))}
    lab = [raw[t.ticket_id]["labels"] for t in tickets]
    texts = [t.text for t in tickets]
    intents = [x["intent"] for x in lab]
    urgencies = [x["urgency"] for x in lab]
    groups = question_groups(texts)

    step("2/4 loading the search index")
    retriever = Retriever.from_store()
    embedder = retriever.embedder
    vectors = TicketClassifier(FEATURES, embedder=embedder).embed(texts) if FEATURES == "embeddings" else None
    step("3/4 predicting every ticket (5 folds)")
    pred, conf, _ = cross_validate(FEATURES, C, texts, intents, urgencies, groups, embedder, vectors)

    step("4/4 routing at each threshold")
    safety = [check(t.text, p) for t, p in zip(tickets, pred)]
    blocked = np.array([s.must_go_to_person for s in safety])
    found = np.array([retriever.best_similarity(t.text) >= retriever.min_similarity for t in tickets])
    conf = np.asarray(conf)
    wrong_type = np.array([p != i for p, i in zip(pred, intents)])
    must_not = np.array([x["must_not_auto_respond"] for x in lab])
    should_auto = np.array([x["expected_route"] == "auto_respond" for x in lab])
    answerable = np.array([x["answerable_from_docs"] for x in lab])
    n = len(tickets)

    lines = ["# Confidence threshold comparison (decision D-019)", "",
             f"{n} development tickets; classifier {FEATURES}, C = {C:g} (D-018), out-of-fold predictions "
             f"(5-fold group cross-validation). The answer key says {should_auto.sum()} tickets "
             f"({should_auto.mean():.1%}) should be answered automatically and {must_not.sum()} must never be.",
             "",
             f"Before any threshold: safety rules or person-only type send {blocked.sum()} tickets to a person; "
             f"search finds no relevant article for {(~found).sum()}.", "",
             "| Threshold | Answered automatically (FCR estimate) | Escalated | Must-not answered automatically | "
             "Other escalate tickets answered | Wrong type among automatic | Not answerable from articles among automatic | "
             "Should-be-automatic tickets answered | Draft ready / Needs a specialist | Largest gap between groups |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    details = []
    for T in THRESHOLDS:
        auto = ~blocked & found & (conf >= T)
        draft = ~auto & ~blocked & found
        gaps = {}
        for seg in SEGMENTS:
            values = [getattr(t, seg) for t in tickets]
            by = {}
            for g in sorted(set(values)):
                idx = np.array([v == g for v in values]) & should_auto
                if idx.sum():
                    by[g] = (auto[idx].mean(), int(idx.sum()))
            gaps[seg] = (largest_gap(by), by)
        worst = max(gaps, key=lambda s: gaps[s][0])
        lines.append(
            f"| {T:.2f} | {auto.mean():.1%} ({auto.sum()}) | {1 - auto.mean():.1%} | "
            f"{(auto & must_not).sum()} | {(auto & ~should_auto & ~must_not).sum()} | "
            f"{(auto & wrong_type).sum()} | {(auto & ~answerable).sum()} | "
            f"{(auto & should_auto).sum()} of {should_auto.sum()} ({(auto & should_auto).sum() / should_auto.sum():.1%}) | "
            f"{draft.sum()} / {(~auto & ~draft).sum()} | {gaps[worst][0] * 100:.1f} points ({worst.replace('customer_', '')}) |")
        print(lines[-1])
        details += [f"## Threshold {T:.2f}", "",
                    "Share of should-be-automatic tickets answered automatically, by group (groups under 10 tickets not compared):", ""]
        for seg in SEGMENTS:
            details.append(f"- {seg}: " + ", ".join(f"{g} {r:.1%} (of {k})" for g, (r, k) in gaps[seg][1].items()))
        leaks = [t.ticket_id for t, a, m in zip(tickets, auto, must_not) if a and m]
        if leaks:
            details += ["", "Must-not tickets answered automatically (zero tolerance):", ""] + [
                f"- {tid} ({raw[tid]['labels']['intent']}): {raw[tid]['body'][:120]}" for tid in leaks]
        details.append("")

    # ---- why were should-be-automatic tickets sent to a person? (at the chosen threshold) ----
    auto = ~blocked & found & (conf >= CHOSEN)
    reasons = []
    for k, t in enumerate(tickets):
        if not should_auto[k] or auto[k]:
            continue
        if check(t.text).must_go_to_person:
            why = "safety word rule: " + ", ".join(safety[k].reasons)
        elif blocked[k]:
            why = f"predicted a person-only type ({pred[k]}; true type {intents[k]})"
        elif not found[k]:
            why = "search found no relevant article"
        else:
            why = f"confidence {conf[k]:.2f} below {CHOSEN:.2f}"
        reasons.append((t, why.split(":")[0].split(" (")[0].split(" 0")[0], why))
    lines += ["", f"## Why should-be-automatic tickets went to a person (threshold {CHOSEN:.2f})", "",
              f"{len(reasons)} of {should_auto.sum()} tickets.", "",
              "| Reason | All | " + " | ".join(f"{seg.replace('customer_', '')}: worst group" for seg in SEGMENTS) + " |",
              "|---|---|" + "---|" * len(SEGMENTS)]
    kinds = sorted({r[1] for r in reasons}, key=lambda x: -sum(r[1] == x for r in reasons))
    for kind in kinds:
        cells = []
        for seg in SEGMENTS:
            counts = {}
            for t, kd, _ in reasons:
                if kd == kind:
                    counts[getattr(t, seg)] = counts.get(getattr(t, seg), 0) + 1
            size = {g: sum(1 for k, t in enumerate(tickets) if should_auto[k] and getattr(t, seg) == g)
                    for g in counts}
            g = max(counts, key=lambda x: counts[x] / size[x])       # highest share, not highest count
            cells.append(f"{g} {counts[g]} of {size[g]} ({counts[g] / size[g]:.1%})")
        lines.append(f"| {kind} | {sum(r[1] == kind for r in reasons)} | " + " | ".join(cells) + " |")
    print("\n".join(lines[-(len(kinds) + 5):]))

    # how certain is the region gap? bootstrap over tickets (Module 4)
    rng = np.random.default_rng(42)
    idx = np.where(should_auto)[0]
    for seg in SEGMENTS:
        values = np.array([getattr(tickets[k], seg) for k in idx])
        gaps_b = []
        for _ in range(1000):
            s_ = rng.choice(len(idx), len(idx))
            v, a = values[s_], auto[idx][s_]
            rates = [a[v == g].mean() for g in set(values) if (v == g).sum() >= 10]
            gaps_b.append(max(rates) - min(rates))
        lo, hi = np.percentile(gaps_b, [2.5, 97.5])
        lines.append(f"- {seg}: gap 95% range {lo * 100:.1f} to {hi * 100:.1f} points")
        print(lines[-1])
    lines += ["", "Every ticket sent to a person (reason in full):", ""] + [
        f"- {t.ticket_id} [{t.customer_region}, {t.language_fluency}] {why}: {t.text[:110]}" for t, _, why in reasons]

    lines += ["", "Notes:",
              "- FCR (first contact resolution) here counts only the routing step. The reply must still pass the "
              "grounding check and guardrails, which can only lower it.",
              "- 'Not answerable from articles among automatic': search found something, but the answer key says the "
              "articles do not answer it. The grounding check (the model answers only from the article, or abstains) "
              "must catch these; measured on Day 5.",
              "- Gaps compare groups of at least 10 should-be-automatic tickets; the target is under 5 points."]
    out = ROOT / "evaluation" / "results" / "threshold_comparison.md"
    out.write_text("\n".join(lines + [""] + details) + "\n", encoding="utf-8")
    print(f"\nwritten: {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
