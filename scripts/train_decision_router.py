"""Train and save the learned decisions model (src/decisions.py) on Mohnish Grover's decisions for the 500 development
tickets. Same set-up as scripts/learn_decisions.py, which tested it on unseen wordings and unseen questions.

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
Run:    python scripts/train_decision_router.py
Writes: models/decision_router.joblib and models/decision_router.json (what it learned from, and when)
"""
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import src  # noqa: E402,F401  (loads Chroma first)
import joblib  # noqa: E402
import numpy as np  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from src.classify import SEED, TicketClassifier  # noqa: E402
from src.decisions import MODEL_PATH, THRESHOLD, text_of  # noqa: E402
from src.ingest import load_tickets  # noqa: E402
from src.retrieve import default_embedder  # noqa: E402

FIXED = {"Q22", "Q23", "Q24"}            # Daniel's data-location rule; Q53 = zero-tolerance types: both stay rules
wfile = ROOT / "evaluation" / "human_review" / "dev_walkthrough.json"
W = json.loads(wfile.read_text(encoding="utf-8"))["questions"]
person_q = {q["question"] for q in W if q["decision_13nov"].startswith("Person")}
qof = {k: q["question"] for q in W for k in q["tickets"]}
keep = {q["question"] for q in W if not q["question"].startswith("Q53") and q["question"] not in FIXED}
tickets = [t for t in load_tickets(ROOT / "data" / "development_tickets.json") if qof[t.ticket_id] in keep]
y = np.array([qof[t.ticket_id] in person_q for t in tickets], dtype=int)
X = np.asarray(TicketClassifier(features="embeddings", embedder=default_embedder()).embed([text_of(t) for t in tickets]))  # message only (14 Nov)
model = LogisticRegression(C=10.0, max_iter=5000, random_state=SEED, class_weight="balanced").fit(X, y)
pred = (model.predict_proba(X)[:, 1] >= THRESHOLD).astype(int)
joblib.dump(model, MODEL_PATH)
git = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
meta = {"trained": datetime.now(timezone.utc).isoformat(timespec="seconds"), "git_commit": git,
        "learned_from": "Mohnish Grover's decisions, evaluation/human_review/dev_walkthrough.json (development tickets only)",
        "decisions_sha256": hashlib.sha256(wfile.read_bytes()).hexdigest()[:16], "tickets": len(y),
        "to_a_person": int(y.sum()), "model": "logistic regression, C=10, balanced classes, on all-MiniLM-L6-v2", "reads": "the message only (14 Nov)",
        "threshold": THRESHOLD, "on_its_own_training_tickets": f"{int((pred == y).sum())} of {len(y)} match",
        "tested_on_unseen_wordings": "see scripts/learn_decisions.py and scripts/compare_decision_text.py"}
MODEL_PATH.with_suffix(".json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
print(json.dumps(meta, indent=2))
