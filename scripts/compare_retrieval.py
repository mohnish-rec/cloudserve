"""Decision D-017: compare chunk sizes and search modes on the development tickets.

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
Setup Guide step 04: "Try at least two configurations, measure the difference in
retrieval quality, and record which you chose and why."

Uses the development tickets only (tuning on validation tickets is not allowed).
Labels are read here only to measure; the system itself never reads them.
For every answerable ticket, did the expected article appear in the top 5
(hit rate), and how high (MRR, mean reciprocal rank)? Also: how similar is the
best match for tickets the articles do NOT answer, to set the threshold.

Run: python scripts/compare_retrieval.py
Writes: evaluation/results/retrieval_comparison.md
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.ingest import load_tickets  # noqa: E402
from src.retrieve import Retriever, chunk_documents, default_embedder, load_documents  # noqa: E402

CONFIGS = [(400, 80), (800, 120), (1500, 200)]   # (chunk size, overlap) in characters
MODES = ["vector", "hybrid"]
THRESHOLDS = [0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]
UNRELATED = ["What is the capital of France?", "Can you recommend a good pasta recipe?",
             "Who won the football match last night?"]

path = ROOT / "data" / "development_tickets.json"
tickets = load_tickets(path)
labels = {t["ticket_id"]: t["labels"] for t in json.loads(path.read_text(encoding="utf-8"))}
fluency = {t.ticket_id: t.language_fluency for t in tickets}
answerable = [t for t in tickets if labels[t.ticket_id]["answerable_from_docs"]
              and labels[t.ticket_id]["expected_doc_ids"]]
not_answerable = [t for t in tickets if not labels[t.ticket_id]["answerable_from_docs"]]

embedder = default_embedder()
documents = load_documents()
lines = ["# Retrieval comparison (decision D-017)", "",
         f"Development tickets: {len(answerable)} answerable with an expected article, "
         f"{len(not_answerable)} not answerable. Top 5 passages per ticket.", "",
         "| Chunk size / overlap | Passages | Mode | Hit rate @5 | MRR | Hit rate @5, non-fluent |",
         "|---|---|---|---|---|---|"]
best_sims = {}
for size, overlap in CONFIGS:
    chunks = chunk_documents(documents, size, overlap)
    vectors = embedder.embed_documents([c["text"] for c in chunks])
    for mode in MODES:
        r = Retriever(chunks, embedder, vectors=vectors, mode=mode, min_similarity=-1.0)
        hits, rr, nf_hits, nf_n = 0, 0.0, 0, 0
        for t in answerable:
            expected = set(labels[t.ticket_id]["expected_doc_ids"])
            ranked = [p.doc_id for p in r.search(t.text)]
            rank = next((i for i, d in enumerate(ranked, 1) if d in expected), None)
            hits += rank is not None
            rr += 1 / rank if rank else 0
            if fluency[t.ticket_id] == "non_fluent":
                nf_n += 1
                nf_hits += rank is not None
        n = len(answerable)
        lines.append(f"| {size} / {overlap} | {len(chunks)} | {mode} | {hits / n:.1%} | "
                     f"{rr / n:.3f} | {nf_hits / max(nf_n, 1):.1%} (n={nf_n}) |")
        print(lines[-1])
    best_sims[(size, overlap)] = (
        [r.best_similarity(t.text) for t in answerable],
        [r.best_similarity(t.text) for t in not_answerable],
        [r.best_similarity(q) for q in UNRELATED])

lines += ["", "## Relevance threshold", "",
          "Share of answerable tickets that keep their results, and share of unanswerable tickets "
          "that return nothing, at each threshold (cosine similarity of the best passage).", "",
          "| Chunk size | Threshold | Answerable kept | Unanswerable returning nothing |", "|---|---|---|---|"]
for (size, overlap), (ans, notans, unrel) in best_sims.items():
    for th in THRESHOLDS:
        lines.append(f"| {size} | {th:.2f} | {np.mean(np.array(ans) >= th):.1%} | "
                     f"{np.mean(np.array(notans) < th):.1%} |")
    lines.append(f"| {size} | unrelated questions' best similarity | "
                 f"{', '.join(f'{s:.2f}' for s in unrel)} | |")
out = ROOT / "evaluation" / "results" / "retrieval_comparison.md"
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"\nwritten: {out.relative_to(ROOT)}")
