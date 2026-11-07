"""Retrieve (FR-04), tested with a tiny word-counting stand-in for the embedding
model, so the tests need no model download (here or in CI)."""
import re

import numpy as np

from src.retrieve import BM25, Retriever, rrf

VOCAB = ["revert", "revision", "release", "rollback", "password", "reset", "login",
         "rate", "limit", "429", "requests", "invoice", "billing", "charge"]


class WordCounter:
    """Stand-in embedder: counts known words, so similar wording scores higher."""
    def _vec(self, text):
        words = re.findall(r"[a-z0-9]+", text.lower())
        return [float(words.count(w)) for w in VOCAB] + [0.01]
    def embed_documents(self, texts):
        return [self._vec(t) for t in texts]
    def embed_query(self, text):
        return self._vec(text)


CHUNKS = [
    {"doc_id": "DOC-DEPLOY-002", "title": "Rollback", "category": "deployment",
     "text": "To revert to an earlier revision, open the release history and choose rollback."},
    {"doc_id": "DOC-AUTH-001", "title": "Login", "category": "authentication",
     "text": "If login fails, reset your password from the sign-in page."},
    {"doc_id": "DOC-API-001", "title": "Rate limits", "category": "api",
     "text": "A 429 response means the rate limit for requests was exceeded."},
    {"doc_id": "DOC-BILL-001", "title": "Invoices", "category": "billing",
     "text": "Each invoice lists every charge on your billing account."},
]


def retriever(**kw):
    return Retriever(CHUNKS, WordCounter(), min_similarity=0.3, **kw)


def test_a_known_question_returns_the_right_article_first():
    results = retriever().search("How do I revert to an earlier revision of my release?")
    assert results and results[0].doc_id == "DOC-DEPLOY-002" and results[0].rank == 1


def test_an_unrelated_question_returns_nothing():
    assert retriever().search("What is the capital of France?") == []
    assert retriever().search("   ") == []


def test_every_result_names_a_real_article_and_carries_scores():
    real = {c["doc_id"] for c in CHUNKS}
    for p in retriever(top_k=3).search("password reset after login failed"):
        assert p.doc_id in real and -1 <= p.similarity <= 1 and p.keyword >= 0


def test_keyword_search_scores_exact_codes():
    scores = BM25([c["text"] for c in CHUNKS]).scores("getting 429 errors")
    assert int(np.argmax(scores)) == 2 and scores[2] > 0


def test_rank_fusion_rewards_agreement():
    assert rrf([["a", "b", "c"], ["b", "a"]])[:2] == ["a", "b"]
    assert rrf([[1, 2], [2, 3]])[0] == 2


def test_same_question_gives_the_same_results():
    r = retriever()
    assert r.search("rate limit 429") == r.search("rate limit 429")


def test_common_words_are_ignored_and_each_article_appears_once():
    assert BM25(["how do I do it", "rollback a release"]).scores("how do I")[0] == 0
    chunks = CHUNKS + [{"doc_id": "DOC-DEPLOY-002", "title": "Rollback", "category": "deployment",
                        "text": "Rollback restores the previous revision of a release."}]
    ids = [p.doc_id for p in Retriever(chunks, WordCounter(), min_similarity=0.3).search(
        "revert release revision rollback")]
    assert len(ids) == len(set(ids))
