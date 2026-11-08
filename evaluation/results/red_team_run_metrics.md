# Metrics report: red_team_tickets.json

- **Run:** run-20261108T022347-3c5215 · 2026-11-08T02:25:09+00:00 · 14 tickets
- **System version:** commit 6455fdd · prompts PR-01 v1.2, PR-02 v1.0 · writer openai/gpt-oss-20b (backup openai/gpt-oss-120b) · checker qwen/qwen3.8-27b · classifier logistic regression on all-MiniLM-L6-v2 embeddings, C=10 (D-018) · threshold 0.85
- **Answer key in the file:** no: accuracy figures not available

## Volume

| Processed | Answered automatically | Escalated | Blocked by guardrails |
|---|---|---|---|
| 14 | 1 (7.1%) | 11 (78.6%) | 2 (14.3%) |

## Business

| First contact resolution | Escalation rate | Mean response time | Median response time |
|---|---|---|---|
| 7.1% | 92.9% | 5.4 s | 0.1 s |

First contact resolution counts only tickets closed with no person involved; "Draft ready" hand-overs count as escalations (FR-07).

## Technical

- **Latency:** median 0.1 s, 95th percentile 24.2 s (target: under 3 s for 95%, NFR-01)
- **Model calls:** 6 in total, 0.43 per ticket
- **Decisions logged:** 50 rows; 14 final outcomes for 14 tickets -> reconciles (A8)
- **Guardrail activations:** instruction_integrity 2
- **Private data detections:** 0 (every one blocked, none sent)
- **Labels:** Needs a specialist 13, sent 1

Run time: 2.0 minutes.
