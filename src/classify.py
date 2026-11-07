"""Classify: predict each ticket's type and urgency, with a confidence (FR-02).

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
Decision D-016: a classifier trained on the 500 labelled development tickets,
not the language model. Module 4: compare a simple baseline, keep it in one
pipeline, fixed seed, never tune on the validation tickets.

Build Specification, "Classify":
- assigns a type (intent) and an urgency to every ticket;
- attaches a numeric confidence that reflects the probability of being right;
- returns a defined fallback rather than raising an exception;
- records the alternatives it considered, not only the one it chose.

Two ways of turning a ticket into numbers are compared (scripts/train_classifier.py):
- "tfidf": word scores (TF-IDF, term frequency-inverse document frequency);
- "embeddings": meaning, from the same model as the search (all-MiniLM-L6-v2).
Both feed a logistic regression. Its raw probabilities are then calibrated with
temperature scaling, learned on held-out questions inside the training data, so
that a stated 80% is right about 80% of the time (Evaluation Framework).
"""
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import GroupKFold

ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / "models" / "classifier.joblib"
SEED = 42
FALLBACK_TYPE = "unclear_request"
POLITE = (r"(please do the needful|kindly check and revert|please tell what to do|please help fast|"
          r"waiting for your reply|sorry for my english|this is urgent|pls|please)")


@dataclass(frozen=True)
class Classification:
    intent: str
    confidence: float                 # calibrated probability the intent is right (0 to 1)
    urgency: str
    urgency_confidence: float
    alternatives: tuple = field(default_factory=tuple)   # ((type, probability), ...) top 3
    fallback: bool = False            # True when it could not classify
    reason: str = ""


def normalise_question(text: str) -> str:
    """The question without politeness phrases, punctuation or capitals."""
    return re.sub(r"[^a-z0-9]+", " ", re.sub(POLITE, " ", text.lower())).strip()


def question_groups(texts, similarity=None) -> list:
    """Group tickets that ask the same question, for group-aware cross-validation (Module 4).

    similarity=None: identical questions once politeness and punctuation are
    removed (the main test: the 500 tickets hold only about 200 of these).
    similarity=0.5: also joins rewordings whose word profiles are at least 50%
    similar (a harsher stress test: whole questions are unseen in training).
    """
    clean = [normalise_question(t) for t in texts]
    if similarity is None:
        ids = {}
        return [ids.setdefault(c, len(ids)) for c in clean]
    sims = cosine_similarity(TfidfVectorizer().fit_transform(clean))
    parent = list(range(len(texts)))

    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for i, j in zip(*np.where(sims >= similarity)):
        if i < j:
            parent[root(i)] = root(j)
    return [root(i) for i in range(len(texts))]


def _softmax(scores, temperature=1.0):
    z = np.asarray(scores, dtype=float) / temperature
    z -= z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


def _fit_temperature(scores, true_index):
    """The temperature that makes probabilities match reality best (lowest log loss)."""
    best_t, best_loss = 1.0, np.inf
    for t in np.exp(np.linspace(np.log(0.02), np.log(5.0), 120)):
        p = _softmax(scores, t)[np.arange(len(true_index)), true_index]
        loss = -np.mean(np.log(np.clip(p, 1e-12, 1)))
        if loss < best_loss:
            best_t, best_loss = float(t), loss
    return best_t


class TicketClassifier:
    def __init__(self, features="tfidf", C=10.0, embedder=None):
        if features not in ("tfidf", "embeddings"):
            raise ValueError("features must be 'tfidf' or 'embeddings'")
        self.features, self.C, self._embedder = features, C, embedder
        self.vectorizer = None
        self.models, self.temperatures = {}, {}

    # ---- turning text into numbers ----
    def _embedder_or_default(self):
        if self._embedder is None:
            from src.retrieve import default_embedder
            self._embedder = default_embedder()
        return self._embedder

    def embed(self, texts):
        vectors = np.asarray(self._embedder_or_default().embed_documents(list(texts)), dtype=float)
        return vectors / (np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-12)

    def _matrix(self, texts=None, vectors=None, fit=False):
        if self.features == "embeddings":
            return vectors if vectors is not None else self.embed(texts)
        if fit:
            self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=1)
            return self.vectorizer.fit_transform(texts)
        return self.vectorizer.transform(texts)

    def _model(self):
        return LogisticRegression(C=self.C, max_iter=5000, random_state=SEED)

    # ---- training ----
    def fit(self, texts, intents, urgencies, vectors=None, groups=None):
        """vectors: optional precomputed embeddings (same order as texts)."""
        texts = list(texts)
        groups = groups if groups is not None else question_groups(texts)
        X = self._matrix(texts, vectors, fit=True)
        for name, y in (("intent", np.asarray(intents)), ("urgency", np.asarray(urgencies))):
            self.models[name] = self._model().fit(X, y)
            self.temperatures[name] = self._learn_temperature(texts, vectors, y, groups)
        return self

    def _learn_temperature(self, texts, vectors, y, groups):
        """Held-out scores from 3 group folds inside the training data, never the test data."""
        n_groups = len(set(groups))
        if n_groups < 3:
            return 1.0
        classes = np.unique(y)
        index = {c: k for k, c in enumerate(classes)}
        scores, truth = [], []
        for tr, te in GroupKFold(n_splits=3).split(texts, y, groups):
            inner = TicketClassifier(self.features, self.C, self._embedder)
            Xtr = inner._matrix([texts[i] for i in tr], None if vectors is None else vectors[tr], fit=True)
            m = inner._model().fit(Xtr, y[tr])
            Xte = inner._matrix([texts[i] for i in te], None if vectors is None else vectors[te])
            s = m.decision_function(Xte)
            s = s if s.ndim == 2 else np.column_stack([-s, s])
            # A type missing from this fold's training gets a very low score.
            full = np.full((len(te), len(classes)), -30.0)
            full[:, [index[c] for c in m.classes_]] = s
            scores.append(full)
            truth += [index[c] for c in y[te]]
        return _fit_temperature(np.vstack(scores), np.array(truth))

    # ---- prediction ----
    def predict_proba(self, texts=None, vectors=None):
        X = self._matrix(texts, vectors)
        out = {}
        for name, m in self.models.items():
            s = m.decision_function(X)
            s = s if s.ndim == 2 else np.column_stack([-s, s])
            out[name] = (m.classes_, _softmax(s, self.temperatures.get(name, 1.0)))
        return out

    def classify(self, text: str) -> Classification:
        """Never raises: an empty ticket or any failure gives the defined fallback."""
        if not text or not text.strip():
            return Classification(FALLBACK_TYPE, 0.0, "medium", 0.0, (), True, "empty ticket text")
        try:
            p = self.predict_proba([text])
            ic, ip = p["intent"][0], p["intent"][1][0]
            uc, up = p["urgency"][0], p["urgency"][1][0]
            top, u = np.argsort(-ip)[:3], int(np.argmax(up))
            return Classification(
                intent=str(ic[top[0]]), confidence=round(float(ip[top[0]]), 4),
                urgency=str(uc[u]), urgency_confidence=round(float(up[u]), 4),
                alternatives=tuple((str(ic[i]), round(float(ip[i]), 4)) for i in top))
        except Exception as e:   # noqa: BLE001 - any failure must become the fallback
            return Classification(FALLBACK_TYPE, 0.0, "medium", 0.0, (), True,
                                  f"classifier failed: {type(e).__name__}")

    # ---- saving and loading (the whole fitted model as one file, Module 4) ----
    def save(self, path=MODEL_PATH, metadata=None):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"features": self.features, "C": self.C, "vectorizer": self.vectorizer,
                     "models": self.models, "temperatures": self.temperatures}, path)
        if metadata:
            path.with_suffix(".json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path=MODEL_PATH, embedder=None):
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"{path} not found: run python scripts/train_classifier.py --save <features>")
        saved = joblib.load(path)
        obj = cls(saved["features"], saved["C"], embedder)
        obj.vectorizer, obj.models, obj.temperatures = saved["vectorizer"], saved["models"], saved["temperatures"]
        return obj
