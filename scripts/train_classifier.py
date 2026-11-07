"""Train and compare the ticket classifiers (decision D-018), and check the safety rules.

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
Uses the Evaluation Framework's own code for the classification report, confusion
matrix and calibration table (marked below), and Module 4's method:
- development tickets only (validation tickets are never used for tuning);
- group cross-validation: the 500 tickets hold only about 200 different
  questions, so identical questions are kept on the same side of every split,
  otherwise the score would be inflated. A harsher stress test also keeps
  rewordings together (at least 50% similar wording), so whole questions are
  unseen in training;
- a fixed seed; the saved model is recorded with its git commit and data hash.

Run:   python scripts/train_classifier.py              (compare, write the report)
Then:  python scripts/train_classifier.py --save tfidf (or --save embeddings)
Writes: evaluation/results/classifier_comparison.md and, with --save, models/classifier.joblib
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, precision_score, recall_score
from sklearn.model_selection import GroupKFold

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.classify import SEED, TicketClassifier, question_groups  # noqa: E402
from src.ingest import load_tickets  # noqa: E402
from src.safety import PERSON_ONLY_TYPES, check_text  # noqa: E402

DATA = ROOT / "data" / "development_tickets.json"
OPTIONS = [("tfidf", 1.0), ("tfidf", 10.0), ("embeddings", 1.0), ("embeddings", 10.0)]
# ---- Evaluation Framework, "On calibration": calibration_table, as given ----
class Pred:
    def __init__(self, confidence, correct):
        self.confidence, self.correct = confidence, correct


def calibration_table(predictions, bands=5):
    """Compare stated confidence against observed accuracy per band."""
    rows = []
    for i in range(bands):
        low, high = i / bands, (i + 1) / bands
        # Change: the top band includes 1.0; the framework's "< high" would leave out
        # every prediction made with a confidence of exactly 1.0.
        group = [p for p in predictions if low <= p.confidence < high or (high == 1 and p.confidence == 1)]
        if not group:
            continue
        stated = sum(p.confidence for p in group) / len(group)
        observed = sum(1 for p in group if p.correct) / len(group)
        rows.append((low, high, len(group), stated, observed, stated - observed))
    return rows


def bootstrap_ci(y_true, y_pred, fn, n=1000):
    rng = np.random.default_rng(SEED)
    y_true, y_pred, idx = np.array(y_true), np.array(y_pred), np.arange(len(y_true))
    vals = [fn(y_true[s], y_pred[s]) for s in (rng.choice(idx, len(idx)) for _ in range(n))]
    return np.percentile(vals, 2.5), np.percentile(vals, 97.5)


def weighted_precision(t, p):
    return precision_score(t, p, average="weighted", zero_division=0)


def cross_validate(features, C, texts, intents, urgencies, groups, embedder, vectors):
    """Out-of-fold predictions: every ticket is predicted by a model that never saw its question."""
    intents, urgencies = np.asarray(intents), np.asarray(urgencies)
    pred_i, pred_u = [None] * len(texts), [None] * len(texts)
    conf = np.zeros(len(texts))
    for train, test in GroupKFold(n_splits=5).split(texts, intents, groups):
        m = TicketClassifier(features, C, embedder).fit(
            [texts[i] for i in train], intents[train], urgencies[train],
            vectors=None if vectors is None else vectors[train], groups=[groups[i] for i in train])
        p = m.predict_proba([texts[i] for i in test], None if vectors is None else vectors[test])
        ic, ip = p["intent"]
        uc, up = p["urgency"]
        for row, i in enumerate(test):
            pred_i[i] = ic[int(np.argmax(ip[row]))]
            conf[i] = float(np.max(ip[row]))
            pred_u[i] = uc[int(np.argmax(up[row]))]
    return pred_i, conf, pred_u


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--save", choices=["tfidf", "embeddings"], help="train on all development tickets and save")
    ap.add_argument("--C", type=float, default=None, help="regularisation strength for --save")
    args = ap.parse_args()

    tickets = load_tickets(DATA)
    raw = {t["ticket_id"]: t for t in json.loads(DATA.read_text(encoding="utf-8"))}
    texts = [t.text for t in tickets]
    intents = [raw[t.ticket_id]["labels"]["intent"] for t in tickets]
    urgencies = [raw[t.ticket_id]["labels"]["urgency"] for t in tickets]
    groups = question_groups(texts)
    stress_groups = question_groups(texts, similarity=0.5)
    embedder = vectors = None
    if any(f == "embeddings" for f, _ in OPTIONS) or args.save == "embeddings":
        from src.retrieve import default_embedder
        embedder = default_embedder()
        vectors = TicketClassifier("embeddings", embedder=embedder).embed(texts)   # once, reused

    if args.save:
        C = args.C or 10.0
        model = TicketClassifier(args.save, C, embedder).fit(
            texts, intents, urgencies, vectors=vectors if args.save == "embeddings" else None, groups=groups)
        meta = {"features": args.save, "C": C, "seed": SEED, "trained_on": "data/development_tickets.json",
                "tickets": len(texts), "data_sha256": hashlib.sha256(DATA.read_bytes()).hexdigest(),
                "git_commit": subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                                             capture_output=True, text=True).stdout.strip(),
                "trained_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
        model.save(metadata=meta)
        print(f"saved models/classifier.joblib ({args.save}, C={C}) and models/classifier.json")
        return

    lines = ["# Classifier comparison (decision D-018)", "",
             f"500 development tickets, {len(set(groups))} different questions. Main test: 5-fold group "
             "cross-validation, identical questions never split between training and testing. Stress test: "
             f"rewordings kept together too ({len(set(stress_groups))} groups), so whole questions are unseen. "
             "Probabilities calibrated by temperature scaling learned inside each training fold. Seed 42.", "",
             "| Features | C | Type accuracy | Type precision (weighted) [95% CI] | Type precision (macro) | "
             "Type recall (macro) | Urgency accuracy | Largest calibration gap | Stress test: type accuracy |",
             "|---|---|---|---|---|---|---|---|---|"]
    details = []
    for features, C in OPTIONS:
        pi, conf, pu = cross_validate(features, C, texts, intents, urgencies, groups, embedder,
                                      vectors if features == "embeddings" else None)
        acc = np.mean(np.array(pi) == np.array(intents))
        wp = weighted_precision(intents, pi)
        lo, hi = bootstrap_ci(intents, pi, weighted_precision)
        mp = precision_score(intents, pi, average="macro", zero_division=0)
        mr = recall_score(intents, pi, average="macro", zero_division=0)
        ua = np.mean(np.array(pu) == np.array(urgencies))
        cal = calibration_table([Pred(c, p == t) for c, p, t in zip(conf, pi, intents)])
        gap = max(abs(r[5]) for r in cal if r[2] >= 10)   # bands with at least 10 tickets
        si, _, _ = cross_validate(features, C, texts, intents, urgencies, stress_groups, embedder,
                                  vectors if features == "embeddings" else None)
        sacc = np.mean(np.array(si) == np.array(intents))
        lines.append(f"| {features} | {C:g} | {acc:.1%} | {wp:.1%} [{lo:.1%}, {hi:.1%}] | {mp:.1%} | "
                     f"{mr:.1%} | {ua:.1%} | {gap * 100:.1f} points | {sacc:.1%} |")
        print(lines[-1])
        details += [f"## {features}, C = {C:g}", "", "Calibration (Evaluation Framework):", "",
                    "| Band | Tickets | Stated confidence | Observed accuracy | Gap |", "|---|---|---|---|---|"]
        details += [f"| {lo_:.1f}-{hi_:.1f} | {n} | {s:.1%} | {o:.1%} | {(s - o) * 100:+.1f} points |"
                    for lo_, hi_, n, s, o, _ in cal]
        # ---- Evaluation Framework, "Intent classification precision and recall", as given ----
        details += ["", "```", classification_report(intents, pi, digits=3, zero_division=0), "```",
                    "", "Confusion matrix (rows = true type, columns = predicted, in sorted type order):", "",
                    "```", str(confusion_matrix(intents, pi)), "```", ""]

    # ---- the safety rules (FR-03): how many risky tickets do they catch on their own? ----
    risky_ids = {tid for tid, r in raw.items()
                 if r["labels"]["must_not_auto_respond"] or r["labels"]["intent"] == "data_residency"
                 or re.search(r"public repo|pushed (a )?key|exposed|leak", r["body"], re.I)}
    caught = {t.ticket_id for t in tickets if check_text(t.text)}
    by_type = {t.ticket_id for t in tickets if raw[t.ticket_id]["labels"]["intent"] in PERSON_ONLY_TYPES}
    safe = [t for t in tickets if t.ticket_id not in risky_ids]
    false_alarms = [t for t in safe if t.ticket_id in caught]
    missed = sorted(risky_ids - caught - by_type)
    lines += ["", "## Safety rules (FR-03), development tickets", "",
              f"- Person-only tickets (must-not labels, data location, leaked keys): {len(risky_ids)}",
              f"- Caught by the word rules alone: {len(risky_ids & caught)} ({len(risky_ids & caught) / len(risky_ids):.1%})",
              f"- Missed by the word rules but of a person-only type (caught if the classifier is right): "
              f"{len((risky_ids - caught) & by_type)}",
              f"- Missed by both word rules and type: {len(missed)} {missed[:10]}",
              f"- Safe tickets flagged by the word rules (false alarms, sent to a person unnecessarily): "
              f"{len(false_alarms)} of {len(safe)} ({len(false_alarms) / len(safe):.1%})"]
    for x in lines[-5:]:
        print(x)
    if false_alarms:
        lines += ["", "False alarms (first 10):", ""] + [
            f"- {t.ticket_id} ({raw[t.ticket_id]['labels']['intent']}): {check_text(t.text)} - {t.text[:120]}"
            for t in false_alarms[:10]]
    out = ROOT / "evaluation" / "results" / "classifier_comparison.md"
    out.write_text("\n".join(lines + [""] + details) + "\n", encoding="utf-8")
    print(f"\nwritten: {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
