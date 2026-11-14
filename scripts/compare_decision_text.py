"""14 Nov 2026: should the learned decisions layer (src/decisions.py) read the subject and the message together, as now,
or the message only? Three tickets in the sandbox run of the 500 development tickets (DEV-0374, DEV-0378, DEV-0439)
went to a person because of the misleading subject "Database restore taking hours" on a message about connections.

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
Learns from: Mohnish Grover's decisions (evaluation/human_review/dev_walkthrough.json), never the labels.
Changes nothing in the system: it only compares the two ways and writes a report.
Run:    python scripts/compare_decision_text.py
Writes: evaluation/results/compare_decision_text.md
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import src  # noqa: E402,F401  (loads Chroma first)
import numpy as np  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.model_selection import GroupKFold  # noqa: E402
from src.classify import SEED, TicketClassifier  # noqa: E402
from src.decisions import THRESHOLD  # noqa: E402
from src.ingest import load_tickets  # noqa: E402
from src.retrieve import default_embedder  # noqa: E402

FIXED = {"Q22", "Q23", "Q24"}
W = json.loads((ROOT / "evaluation" / "human_review" / "dev_walkthrough.json").read_text(encoding="utf-8"))["questions"]
person_q = {q["question"] for q in W if q["decision_13nov"].startswith("Person")}
qof = {k: q["question"] for q in W for k in q["tickets"]}
keep = {q["question"] for q in W if not q["question"].startswith("Q53") and q["question"] not in FIXED}
all_t = load_tickets(ROOT / "data" / "development_tickets.json")
train = [t for t in all_t if qof[t.ticket_id] in keep]
answered = [t for t in all_t if qof[t.ticket_id] not in person_q]       # every ticket he decided to answer
y = np.array([qof[t.ticket_id] in person_q for t in train], dtype=int)
embed = TicketClassifier(features="embeddings", embedder=default_embedder()).embed
norm = lambda s: re.sub(r"[^a-z0-9 ]", "", s.lower())
make = lambda c: LogisticRegression(C=10.0, max_iter=5000, random_state=SEED, class_weight="balanced")

WAYS = {"Subject and message (now)": lambda t: t.text, "Message only": lambda t: t.body or t.text}
L = ["# Learned decisions: subject and message, or message only?", "",
     f"Learned from {len(train)} development tickets ({int(y.sum())} he sent to a person). "
     f"Threshold {THRESHOLD}. Tickets he decided to answer: {len(answered)}.", ""]
rows, flagged = [], {}
for name, txt in WAYS.items():
    X = np.asarray(embed([txt(t) for t in train]))
    res = {}
    for test, g in {"A": [norm(t.body) for t in train], "B": [qof[t.ticket_id] for t in train]}.items():
        prob = np.zeros(len(y))
        for tr, te in GroupKFold(n_splits=5).split(X, y, g):
            prob[te] = make(0).fit(X[tr], y[tr]).predict_proba(X[te])[:, 1]
        p = (prob >= 0.5).astype(int)
        res[test] = (int((p == y).sum()), int((p & y).sum()), int((p & (1 - y)).sum()))
    m = make(0).fit(X, y)
    fit = (m.predict_proba(X)[:, 1] >= THRESHOLD).astype(int)
    pa = m.predict_proba(np.asarray(embed([txt(t) for t in answered])))[:, 1]
    flagged[name] = {t.ticket_id: (qof[t.ticket_id], round(float(p) * 100)) for t, p in zip(answered, pa) if p >= THRESHOLD}
    rows.append(f"| {name} | {int((fit == y).sum())} of {len(y)} | {res['A'][0]} of {len(y)} | {res['A'][1]} of {int(y.sum())} "
                f"| {res['A'][2]} | {res['B'][1]} of {int(y.sum())} | {len(flagged[name])} |")
L += ["| Way | Matches on its own training tickets | A. new wording: matches | A. person tickets caught "
      "| A. answer tickets wrongly sent to a person | B. new question: person tickets caught "
      "| His answered tickets it would send to a person |", "|---|---|---|---|---|---|---|"] + rows + [""]
for name, f in flagged.items():
    L += [f"## {name}: answered tickets it would send to a person", ""]
    L += [f"- {k} ({q}, {p}% a person)" for k, (q, p) in sorted(f.items())] or ["- none"]
    L += [""]
out = ROOT / "evaluation" / "results" / "compare_decision_text.md"
out.write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L))
