# Metrics report: demo_tickets.json

- **Run:** run-20261117T210457-6e31f7 · 2026-11-17T21:05:10+00:00 · 7 tickets
- **System version:** commit 8310e58 · prompts PR-01 v1.7, PR-02 v1.0 · writer openai/gpt-oss-20b (backup openai/gpt-oss-120b) via Groq direct (free tier) · checker qwen/qwen3.8-27b · classifier logistic regression on all-MiniLM-L6-v2 embeddings, C=10 (D-018) · threshold 0.85 · reply cache off (fresh run) · experiment: trim on, writer reads 3 articles, narrowed safety rules on, type-aware search on, question rules on, learned decisions on, plan rule on
- **Answer key in the file:** no: accuracy figures not available

## Volume

| Processed | Answered automatically | Escalated | Blocked by guardrails |
|---|---|---|---|
| 7 | 0 (0.0%) | 7 (100.0%) | 0 (0.0%) |

## Business

| First contact resolution | Escalation rate | Mean response time | Median response time |
|---|---|---|---|
| 0.0% | 100.0% | 1.3 s | 1.7 s |

First contact resolution counts only tickets closed with no person involved; "Draft ready" hand-overs count as escalations (FR-07).

**Repeat contacts:** 0 of 7 tickets were the same customer asking about the same type within 7 days of an automatic reply in this run; 0 of them went to a person with the earlier reply attached (FR-14).

## Technical

- **Latency:** median 1.7 s, 95th percentile 1.8 s (target: under 3 s for 95%, NFR-01)
- **Response time without rate-limit waits:** median 1.7 s, 95th percentile 1.8 s; time spent waiting on rate limits: 0 s in total, on 0 of 7 tickets (17 Nov: kept apart, as the course team asked)
- **Model calls:** 0 in total (retries included), 0.00 per ticket
- **Reply cache (D-025):** 0 of 5 replies and 0 of 0 checks reused, with no model call
- **Tokens:** writer 0 in + 0 out (0 per reply written); checker 0 in + 0 out; total 0 (0 per ticket)
- **Decisions logged:** 24 rows; 7 final outcomes for 7 tickets -> reconciles (A8)
- **Guardrail activations:** none
- **Private data detections:** 0 (every one blocked, none sent)
- **Labels:** Needs a specialist 7

Run time: 1.0 minutes.
