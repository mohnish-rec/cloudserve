# Metrics report: development_tickets.json

- **Run:** run-20261112T050310-e02f00 · 2026-11-12T15:19:17+00:00 · 500 tickets
- **System version:** commit 4d48f21 · prompts PR-01 v1.7, PR-02 v1.0 · writer openai/gpt-oss-20b (backup openai/gpt-oss-120b) via Groq direct (free tier) · checker qwen/qwen3.8-27b · classifier logistic regression on all-MiniLM-L6-v2 embeddings, C=10 (D-018) · threshold 0.85 · reply cache off (fresh run) · experiment: trim on, writer reads 3 articles, narrowed safety rules on, type-aware search on, question rules on
- **Answer key in the file:** yes, used only to mark this report

## Volume

| Processed | Answered automatically | Escalated | Blocked by guardrails |
|---|---|---|---|
| 500 | 352 (70.4%) | 132 (26.4%) | 16 (3.2%) |

## Business

| First contact resolution | Escalation rate | Mean response time | Median response time |
|---|---|---|---|
| 70.4% | 29.6% | 72.9 s | 2.0 s |

First contact resolution counts only tickets closed with no person involved; "Draft ready" hand-overs count as escalations (FR-07).

## Technical

- **Latency:** median 2.0 s, 95th percentile 306.5 s (target: under 3 s for 95%, NFR-01)
- **Model calls:** 1290 in total (retries included), 2.58 per ticket
- **Reply cache (D-025):** 0 of 369 replies and 0 of 357 checks reused, with no model call
- **Tokens:** writer 327,494 in + 37,661 out (1,410 per reply written); checker 164,993 in + 12,989 out; total 543,137 (1,086 per ticket)
- **Decisions logged:** 2237 rows; 500 final outcomes for 500 tickets -> reconciles (A8)
- **Guardrail activations:** tone_and_scope 10, grounding_model 5, confidence_floor 1
- **Private data detections:** 0 (every one blocked, none sent)
- **Labels:** sent 352, Needs a specialist 148

## Marked against the answer key

- **Must-not tickets answered automatically:** 0 of 87 (target 0)
- **Answered automatically when the answer key says a person:** 83 of 352 automatic replies
- **Should-be-automatic tickets answered automatically:** 269 of 311 (86.5%)
- **Correct first contact resolution** (answered, and the answer key agrees): 53.8%
- **Retrieval hit rate** (an expected article in the top 5): 351 of 357 (98.3%)
- **Citation accuracy** (automatic replies citing an expected article): 260 of 282 (92.2%; target 95%)
- **Type accuracy:** 100.0%

### Classification precision and recall per type

```
                         precision    recall  f1-score   support

         account_access      1.000     1.000     1.000        22
          api_key_issue      1.000     1.000     1.000        18
     api_usage_question      1.000     1.000     1.000        24
 authentication_failure      1.000     1.000     1.000        20
          billing_query      1.000     1.000     1.000        24
     compliance_request      1.000     1.000     1.000        26
     configuration_help      1.000     1.000     1.000        17
            data_export      1.000     1.000     1.000        29
         data_residency      1.000     1.000     1.000        29
         database_issue      1.000     1.000     1.000        26
     deployment_failure      1.000     1.000     1.000        27
        feature_request      1.000     1.000     1.000        20
       integration_help      1.000     1.000     1.000        21
             onboarding      1.000     1.000     1.000        22
performance_degradation      1.000     1.000     1.000        23
       quota_or_overage      1.000     1.000     1.000        23
             rate_limit      1.000     1.000     1.000        13
       rollback_request      1.000     1.000     1.000        28
      security_incident      1.000     1.000     1.000        26
      sso_configuration      1.000     1.000     1.000        26
        unclear_request      1.000     1.000     1.000        15
          webhook_issue      1.000     1.000     1.000        21

               accuracy                          1.000       500
              macro avg      1.000     1.000     1.000       500
           weighted avg      1.000     1.000     1.000       500

```

Confusion matrix (rows = true type, columns = predicted, sorted type order):

```
[[22  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0 18  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0 24  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0 20  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0 24  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0 26  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0 17  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0 29  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0 29  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0 26  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0 27  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0 20  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0 21  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0 22  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0 23  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0 23  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0 13  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0 28  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0 26  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0 26  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0 15  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0 21]]
```

### Calibration (Evaluation Framework)

| Band | Tickets | Stated confidence | Observed accuracy | Gap |
|---|---|---|---|---|
| 0.8-1.0 | 500 | 100.0% | 100.0% | -0.0 points |

### Results by customer group (NFR-06: under 5 points between groups)

Resolution rate = answered automatically. Quality score = share of automatic replies that cite an expected article and passed every guardrail. Groups under 10 tickets are shown but not compared.

| Group | Value | Tickets | Resolution rate | Quality score | Must-not answered |
|---|---|---|---|---|---|
| tier | business | 164 | 70.1% | 74.8% | 0 |
| tier | enterprise | 83 | 69.9% | 75.9% | 0 |
| tier | standard | 253 | 70.8% | 72.6% | 0 |
| region | asia_pacific | 119 | 67.2% | 68.8% | 0 |
| region | europe | 151 | 74.8% | 76.1% | 0 |
| region | latin_america | 60 | 68.3% | 73.2% | 0 |
| region | north_america | 170 | 69.4% | 75.4% | 0 |
| language_fluency | fluent | 380 | 71.1% | 73.3% | 0 |
| language_fluency | non_fluent | 120 | 68.3% | 75.6% | 0 |
| channel | chat | 155 | 72.3% | 76.8% | 0 |
| channel | docs_comment | 78 | 71.8% | 62.5% | 0 |
| channel | email | 212 | 67.9% | 75.0% | 0 |
| channel | forum | 55 | 72.7% | 77.5% | 0 |

Run time: 616.4 minutes.
