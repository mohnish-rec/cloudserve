"""14 Nov 2026: can the system LEARN Mohnish Grover's decisions (answer or person) from the 500 development tickets,
instead of following word rules written for single questions (Q11, Q12, Q27, Q41)?

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
Learns from: evaluation/human_review/dev_walkthrough.json (his decisions, never the labels), on the same meaning
fingerprints the classifier uses (all-MiniLM-L6-v2), with logistic regression (as D-018).
Covers: every question he answered, plus Q11, Q12, Q27 and Q41 (his own question rules). Daniel's safety rules and the
zero-tolerance types (Q22-Q24, Q53) stay fixed rules and are left out here.
Two honest tests, each with 5-fold cross-validation so a ticket is never judged by a model that saw it:
  A. new wording: tickets with the same message are kept together, so the exact message is never seen in training;
  B. a new question: whole questions are held out, so the model has never seen the question at all.
Run:    python scripts/learn_decisions.py
Writes: evaluation/results/learn_decisions.md
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import src  # noqa: E402,F401  (loads Chroma first)
import numpy as np  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.model_selection import GroupKFold  # noqa: E402
from src.classify import SEED, TicketClassifier  # noqa: E402
from src.ingest import load_tickets  # noqa: E402
from src.retrieve import default_embedder  # noqa: E402

RULE_QUESTIONS = {"Q11", "Q12", "Q27", "Q41"}
FIXED = {"Q22", "Q23", "Q24"}                       # Daniel's data-location rule, kept as a rule
W = json.loads((ROOT / "evaluation" / "human_review" / "dev_walkthrough.json").read_text(encoding="utf-8"))["questions"]
person_q = {q["question"] for q in W if q["decision_13nov"].startswith("Person")}
qof = {k: q["question"] for q in W for k in q["tickets"]}
keep = {q["question"] for q in W if not q["question"].startswith("Q53") and q["question"] not in FIXED}
tickets = [t for t in load_tickets(ROOT / "data" / "development_tickets.json") if qof[t.ticket_id] in keep]
y = np.array([qof[t.ticket_id] in person_q for t in tickets], dtype=int)
X = np.asarray(TicketClassifier(features="embeddings", embedder=default_embedder()).embed([t.text for t in tickets]))
norm = lambda s: re.sub(r"[^a-z0-9 ]", "", s.lower())
groups = {"A. new wording (same message never in training)": [norm(t.body) for t in tickets],
          "B. a new question (whole question never in training)": [qof[t.ticket_id] for t in tickets]}

L = ["# Learning Mohnish Grover's decisions from the 500 development tickets", "",
     f"Tickets covered: {len(tickets)} ({int(y.sum())} he sent to a person: Q11, Q12, Q27, Q41; the rest answered). "
     "Daniel's data-location rule and the zero-tolerance types stay fixed rules and are not included.", ""]
for name, g in groups.items():
    prob = np.zeros(len(y))
    for tr, te in GroupKFold(n_splits=5).split(X, y, g):
        m = LogisticRegression(C=10.0, max_iter=5000, random_state=SEED, class_weight="balanced").fit(X[tr], y[tr])
        prob[te] = m.predict_proba(X[te])[:, 1]
    pred = (prob >= 0.5).astype(int)
    per = defaultdict(lambda: [0, 0])
    for t, p, yy in zip(tickets, pred, y):
        per[qof[t.ticket_id]][0] += int(p == yy); per[qof[t.ticket_id]][1] += 1
    L += [f"## {name}", "",
          f"- Matches his decision: **{int((pred == y).sum())} of {len(y)}** ({100 * (pred == y).mean():.1f}%)",
          f"- Person questions caught (Q11, Q12, Q27, Q41): **{int((pred & y).sum())} of {int(y.sum())}**",
          f"- Answer questions wrongly sent to a person: **{int((pred & (1 - y)).sum())} of {int((1 - y).sum())}**", "",
          "| Question | His decision | Matches |", "|---|---|---|"]
    L += [f"| {q} | {'person' if q in person_q else 'answer'} | {a} of {n} |" for q, (a, n) in sorted(per.items()) if a < n or q in RULE_QUESTIONS]
    L += [""]
out = ROOT / "evaluation" / "results" / "learn_decisions.md"
out.write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L))
