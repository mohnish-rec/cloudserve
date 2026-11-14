"""Learned decisions (14 Nov 2026): answer automatically or send to a person, learned from Mohnish Grover's decisions.

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
He decided every one of the 500 development tickets, question by question (evaluation/human_review/dev_walkthrough.json).
A logistic regression on the same meaning fingerprints the classifier uses (all-MiniLM-L6-v2) learns those decisions,
so a new ticket that MEANS the same as one he sent to a person goes to a person, however it is worded
(scripts/learn_decisions.py: 97.7% match on unseen wordings). Trained only on development tickets, never the labels.
It can only ADD a handover: Daniel's safety rules and the zero-tolerance types stay fixed rules underneath (FR-03),
and the question rules in src/safety.py stay as a backstop. LEARNED_DECISIONS=off turns it off.
"""
import os
from pathlib import Path

import joblib
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / "models" / "decision_router.joblib"
THRESHOLD = 0.5
_cache = {}


def enabled() -> bool:
    return os.getenv("LEARNED_DECISIONS", "on") == "on"


def load(path=MODEL_PATH):
    path = Path(path)
    if path not in _cache:
        if not path.exists():
            raise FileNotFoundError(f"{path} not found: run python scripts/train_decision_router.py")
        _cache[path] = joblib.load(path)
    return _cache[path]


def person_probability(vector, path=MODEL_PATH) -> float:
    """How likely Mohnish would send this ticket to a person, from its meaning fingerprint."""
    return float(load(path).predict_proba(np.asarray(vector, dtype=float).reshape(1, -1))[0, 1])


def reason(p: float) -> str:
    return f"learned from Mohnish Grover's decisions on the development tickets ({p:.0%} a person)"
