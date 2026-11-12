"""Retrieve: find the articles that answer a ticket (FR-04).

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
Chunking uses the Setup Guide's RecursiveCharacterTextSplitter; the keyword
scoring (BM25) and rank fusion (RRF) follow the Module 5 toolkit.

Build Specification, "Retrieve":
- searches the supplied documentation and returns ranked passages with scores;
- returns identifiers that resolve to the real corpus, so citations can be checked;
- applies a relevance threshold and returns nothing rather than something irrelevant;
- the chunking strategy is a decision made, justified and explained (decision D-017).

Two kinds of search are combined (Module 5, hybrid search):
- by meaning: embeddings (all-MiniLM-L6-v2) compared by cosine similarity;
- by keyword: BM25 (Best Matching 25), which is exact on codes such as 429 or 401
  that meaning-based search blurs.
The two rankings are merged with reciprocal rank fusion (RRF). If even the best
meaning-based match is below the threshold, nothing is returned and the ticket
is escalated: retrieving something plausible but irrelevant is worse than nothing.

Check (Build Specification, day two):
    python -m src.retrieve "How do I revert to an earlier revision?"
"""
import json
import math
import os
import re
import sys
import warnings
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
# Same library notices switched off as in scripts/setup_vector_store.py.
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
warnings.filterwarnings("ignore", message=".*cached_download.*", category=FutureWarning)

# Chosen in decision D-017 from scripts/compare_retrieval.py on the development tickets.
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "400"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "80"))
TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "5"))
MIN_SIMILARITY = float(os.getenv("RETRIEVAL_MIN_SIMILARITY", "0.35"))
SEARCH_MODE = os.getenv("RETRIEVAL_MODE", "hybrid")  # "hybrid" or "vector"


@dataclass(frozen=True)
class Passage:
    doc_id: str          # resolves to an article in data/documentation.json
    title: str
    category: str
    text: str
    similarity: float    # meaning-based score, cosine similarity (-1 to 1)
    keyword: float       # BM25 keyword score (0 = no shared words)
    rank: int            # 1 = best


# Common words carry no meaning for search. Without this list, "how do I ... to"
# matched the billing article as strongly as real words (found on day two).
STOPWORDS = set("""a about after again all am an and any are as at be been being but by can
could did do does doing for from had has have having he her here how i if in into is it its
me my no not of on once only or our ours out over please same she should so some such than
that the their them then there these they this those to too under until up very was we were
what when where which while who why will with would you your yours""".split())


def tokenize(text: str) -> list:
    return [w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOPWORDS]


class BM25:
    """Keyword scores (Module 5 toolkit, bm25_scores), fitted once on the passages."""

    def __init__(self, texts, k1=1.5, b=0.75):
        self.k1, self.b = k1, b
        self.docs = [tokenize(t) for t in texts]
        self.avgdl = sum(len(d) for d in self.docs) / max(len(self.docs), 1)
        self.df = Counter(w for d in self.docs for w in set(d))
        self.n = len(self.docs)

    def scores(self, query: str) -> np.ndarray:
        out = []
        for d in self.docs:
            tf, s = Counter(d), 0.0
            for q in tokenize(query):
                if q not in tf:
                    continue
                idf = math.log(1 + (self.n - self.df[q] + 0.5) / (self.df[q] + 0.5))
                s += idf * tf[q] * (self.k1 + 1) / (
                    tf[q] + self.k1 * (1 - self.b + self.b * len(d) / self.avgdl))
            out.append(s)
        return np.array(out)


def rrf(rankings, k=60) -> list:
    """Reciprocal rank fusion (Module 5): score = sum of 1 / (60 + rank)."""
    scores = Counter()
    for ranking in rankings:
        for rank, i in enumerate(ranking, start=1):
            scores[i] += 1 / (k + rank)
    return [i for i, _ in scores.most_common()]


def load_documents(path=ROOT / "data" / "documentation.json") -> list:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def chunk_documents(documents, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP) -> list:
    """Setup Guide step 04's splitting, with the article's ID, title and topic kept."""
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = []
    for doc in documents:
        for text in splitter.split_text(doc["content"]):
            chunks.append({"doc_id": doc["doc_id"], "title": doc["title"],
                           "category": doc["category"], "text": text})
    return chunks


def default_embedder():
    """The same model as the document store (Setup Guide step 04)."""
    from langchain_community.embeddings import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(model_name=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"))


def _unit(vectors) -> np.ndarray:
    v = np.asarray(vectors, dtype=float)
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)


class Retriever:
    def __init__(self, chunks, embedder, vectors=None, mode=SEARCH_MODE,
                 min_similarity=MIN_SIMILARITY, top_k=TOP_K, pool=40):
        if not chunks:
            raise ValueError("no passages to search")
        self.chunks, self.embedder, self.mode = chunks, embedder, mode
        self.min_similarity, self.top_k, self.pool = min_similarity, top_k, pool
        if vectors is None:
            vectors = embedder.embed_documents([c["text"] for c in chunks])
        self.vectors = _unit(vectors)
        self.bm25 = BM25([c["text"] for c in chunks])
        self._cache = {}

    def _embed(self, query: str) -> np.ndarray:
        if query not in self._cache:   # the same ticket text is embedded only once
            self._cache[query] = _unit(self.embedder.embed_query(query))
        return self._cache[query]

    @classmethod
    def from_store(cls, **kwargs):
        """Load the passages and their vectors from the Chroma store built by setup."""
        from langchain_community.vectorstores import Chroma
        embedder = default_embedder()
        path = (ROOT / os.getenv("CHROMA_PATH", "./storage/chroma")).resolve()
        store = Chroma(collection_name="cloudserve_docs", persist_directory=str(path),
                       embedding_function=embedder)
        got = store.get(include=["documents", "metadatas", "embeddings"])
        chunks = [{"doc_id": m["doc_id"], "title": m["title"], "category": m.get("category", ""),
                   "text": t} for t, m in zip(got["documents"], got["metadatas"])]
        if not chunks:
            raise RuntimeError("the document store is empty: run python scripts/setup_vector_store.py")
        return cls(chunks, embedder, vectors=got["embeddings"], **kwargs)

    def best_similarity(self, query: str) -> float:
        if not query.strip():
            return -1.0
        return float((self.vectors @ self._embed(query)).max())

    def search(self, query: str) -> list:
        """Ranked passages, or an empty list when nothing is relevant enough."""
        if not query or not query.strip():
            return []
        sims = self.vectors @ self._embed(query)
        if sims.max() < self.min_similarity:
            return []                                   # abstain: escalate instead
        by_meaning = [int(i) for i in np.argsort(-sims)[: self.pool]]
        keyword = self.bm25.scores(query)
        if self.mode == "vector":
            order = by_meaning
        else:
            by_keyword = [int(i) for i in np.argsort(-keyword)[: self.pool] if keyword[i] > 0]
            order = rrf([by_meaning, by_keyword])
        # One passage per article (its best), so the top results are different
        # articles rather than the same article twice (found on day two).
        best_per_article, seen = [], set()
        for i in order:
            if self.chunks[i]["doc_id"] not in seen:
                seen.add(self.chunks[i]["doc_id"])
                best_per_article.append(i)
        return [Passage(doc_id=self.chunks[i]["doc_id"], title=self.chunks[i]["title"],
                        category=self.chunks[i]["category"], text=self.chunks[i]["text"],
                        similarity=round(float(sims[i]), 4), keyword=round(float(keyword[i]), 4),
                        rank=r)
                for r, i in enumerate(best_per_article[: self.top_k], start=1)]


# ---- 11 Nov: type-aware search for non-fluent tickets (off unless TYPE_AWARE_SEARCH=on) ----
# Found in the 500 development tickets (PR-01 v1.4 run): 4 of the 6 should-be-automatic non-fluent tickets that were lost
# are one question ("point me at right starting place... console has more in it than I expect"). Its fluent version
# finds "First deployment: a walkthrough"; the non-fluent version found login articles or nothing. The classifier still
# gets its type right (onboarding), so its type is used to make sure one article of that kind is among those read.
# Governance Framework: "Systems built on retrieval tend to perform noticeably worse on tickets written in non-fluent
# English, because the retrieval step depends on the phrasing matching the documentation."
# Article categories for each ticket type, from the development labels (which articles each type's tickets expect).
TYPE_CATEGORIES = {
    "account_access": ("account",), "api_key_issue": ("authentication", "security"), "api_usage_question": ("api",),
    "authentication_failure": ("authentication",), "billing_query": ("billing",), "configuration_help": ("deployment", "account"),
    "data_export": ("data",), "data_residency": ("data",), "database_issue": ("performance", "data"),
    "deployment_failure": ("deployment",), "integration_help": ("integration",), "onboarding": ("onboarding",),
    "performance_degradation": ("performance",), "quota_or_overage": ("billing", "api"), "rate_limit": ("api",),
    "rollback_request": ("deployment",), "sso_configuration": ("authentication",), "webhook_issue": ("api",),
}
TYPE_FLOOR = float(os.getenv("TYPE_AWARE_MIN_SIMILARITY", "0.25"))   # the added article must still be somewhat related
FILLER = re.compile(r"(please do the needful|kindly check and revert|please tell what to do|please help fast|"
                    r"waiting for (your|ur) (reply|response)|sorry for my english|this is urgent|thank(s| you)|"
                    r"\bpls\b|\bplease\b|\bkindly\b)", re.I)


def type_aware() -> bool:
    return os.getenv("TYPE_AWARE_SEARCH", "on") == "on"   # on by default from 12 Nov


def strip_filler(text: str) -> str:
    """The question without politeness and waiting phrases, which pull the search towards the wrong articles."""
    return re.sub(r"\s{2,}", " ", FILLER.sub(" ", text or "")).strip()


def search_typed(retriever, text, intent) -> list:
    """Search on the question without filler; then, if none of the articles the writer reads (the top 3) is of the
    kind the ticket's type calls for, put the best article of that kind third (or first, if search found nothing).
    Every guardrail still runs: an added article that does not fit the situation is blocked like any other."""
    query = strip_filler(text) or text
    found = retriever.search(query)
    cats = TYPE_CATEGORIES.get(intent)
    if not cats:
        return found
    top3 = list(dict.fromkeys(p.doc_id for p in found))[:3]
    if any(p.category in cats for p in found if p.doc_id in top3):
        return found
    sims = retriever.vectors @ retriever._embed(query)
    pick = [i for i in np.argsort(-sims) if retriever.chunks[i]["category"] in cats]
    if not pick or sims[pick[0]] < TYPE_FLOOR:
        return found
    i = int(pick[0])
    c = retriever.chunks[i]
    added = Passage(doc_id=c["doc_id"], title=c["title"], category=c["category"], text=c["text"],
                    similarity=round(float(sims[i]), 4), keyword=0.0, rank=0)
    rest = [p for p in found if p.doc_id != c["doc_id"]]
    out = rest[:2] + [added] + rest[2:]
    return [Passage(**{**p.__dict__, "rank": r}) for r, p in enumerate(out[: retriever.top_k], start=1)]


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "How do I revert to an earlier revision?"
    retriever = Retriever.from_store()
    results = retriever.search(question)
    print(f"query: {question}")
    print(f"mode: {retriever.mode}, threshold: {retriever.min_similarity}, "
          f"best similarity: {retriever.best_similarity(question):.3f}\n")
    if not results:
        print("nothing relevant enough: this ticket would be escalated")
    for p in results:
        print(f"{p.rank}. {p.doc_id} | {p.title} | similarity {p.similarity:.3f} | keyword {p.keyword:.2f}")
        print(f"   {p.text[:140]}...")
