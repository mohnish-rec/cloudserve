# Metrics report: demo_tickets.json

- **Run:** run-20261117T145708-bc6364 · 2026-11-17T14:57:31+00:00 · 7 tickets
- **System version:** commit 235a31d · prompts PR-01 v1.7, PR-02 v1.0 · writer openai/gpt-oss-20b (backup openai/gpt-oss-120b) via Groq direct (free tier) · checker qwen/qwen3.8-27b · classifier logistic regression on all-MiniLM-L6-v2 embeddings, C=10 (D-018) · threshold 0.85 · reply cache off (fresh run) · experiment: trim on, writer reads 3 articles, narrowed safety rules on, type-aware search on, question rules on, learned decisions on, plan rule on
- **Answer key in the file:** no: accuracy figures not available

## Volume

| Processed | Answered automatically | Escalated | Blocked by guardrails |
|---|---|---|---|
| 7 | 4 (57.1%) | 2 (28.6%) | 1 (14.3%) |

## Business

| First contact resolution | Escalation rate | Mean response time | Median response time |
|---|---|---|---|
| 57.1% | 42.9% | 2.4 s | 2.8 s |

First contact resolution counts only tickets closed with no person involved; "Draft ready" hand-overs count as escalations (FR-07).

**Repeat contacts:** 0 of 7 tickets were the same customer asking about the same type within 7 days of an automatic reply in this run; 0 of them went to a person with the earlier reply attached (FR-14).

## Technical

- **Latency:** median 2.8 s, 95th percentile 3.4 s (target: under 3 s for 95%, NFR-01)
- **Response time without rate-limit waits:** median 2.8 s, 95th percentile 3.4 s; time spent waiting on rate limits: 0 s in total, on 0 of 7 tickets (17 Nov: kept apart, as the course team asked)
- **Model calls:** 11 in total (retries included), 1.57 per ticket
- **Reply cache (D-025):** 0 of 6 replies and 0 of 5 checks reused, with no model call
- **Tokens:** writer 7,654 in + 721 out (1,396 per reply written); checker 3,448 in + 259 out; total 12,082 (1,726 per ticket)
- **Decisions logged:** 33 rows; 7 final outcomes for 7 tickets -> reconciles (A8)
- **Guardrail activations:** instruction_integrity 1
- **Private data detections:** 0 (every one blocked, none sent)
- **Labels:** sent 4, Needs a specialist 2, Draft ready: check and send 1

Run time: 0.7 minutes.
