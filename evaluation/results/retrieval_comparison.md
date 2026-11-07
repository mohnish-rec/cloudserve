# Retrieval comparison (decision D-017)

Development tickets: 357 answerable with an expected article, 143 not answerable. Top 5 passages per ticket.

| Chunk size / overlap | Passages | Mode | Hit rate @5 | MRR | Hit rate @5, non-fluent |
|---|---|---|---|---|---|
| 400 / 80 | 141 | vector | 97.8% | 0.925 | 94.3% (n=87) |
| 400 / 80 | 141 | hybrid | 98.0% | 0.935 | 94.3% (n=87) |
| 800 / 120 | 59 | vector | 96.9% | 0.913 | 94.3% (n=87) |
| 800 / 120 | 59 | hybrid | 97.8% | 0.924 | 94.3% (n=87) |
| 1500 / 200 | 29 | vector | 96.9% | 0.917 | 95.4% (n=87) |
| 1500 / 200 | 29 | hybrid | 96.9% | 0.926 | 95.4% (n=87) |

## Relevance threshold

Share of answerable tickets that keep their results, and share of unanswerable tickets that return nothing, at each threshold (cosine similarity of the best passage).

| Chunk size | Threshold | Answerable kept | Unanswerable returning nothing |
|---|---|---|---|
| 400 | 0.20 | 100.0% | 0.0% |
| 400 | 0.25 | 100.0% | 2.8% |
| 400 | 0.30 | 99.7% | 4.2% |
| 400 | 0.35 | 99.7% | 11.2% |
| 400 | 0.40 | 99.4% | 12.6% |
| 400 | 0.45 | 98.9% | 18.2% |
| 400 | 0.50 | 92.2% | 21.7% |
| 400 | unrelated questions' best similarity | 0.11, 0.13, 0.15 | |
| 800 | 0.20 | 100.0% | 3.5% |
| 800 | 0.25 | 99.7% | 6.3% |
| 800 | 0.30 | 99.4% | 11.2% |
| 800 | 0.35 | 98.6% | 13.3% |
| 800 | 0.40 | 97.5% | 14.7% |
| 800 | 0.45 | 95.5% | 17.5% |
| 800 | 0.50 | 86.0% | 25.2% |
| 800 | unrelated questions' best similarity | 0.09, 0.13, 0.09 | |
| 1500 | 0.20 | 100.0% | 4.9% |
| 1500 | 0.25 | 99.7% | 10.5% |
| 1500 | 0.30 | 99.4% | 11.2% |
| 1500 | 0.35 | 98.3% | 13.3% |
| 1500 | 0.40 | 97.2% | 17.5% |
| 1500 | 0.45 | 89.1% | 24.5% |
| 1500 | 0.50 | 79.6% | 37.8% |
| 1500 | unrelated questions' best similarity | 0.07, 0.10, 0.09 | |
