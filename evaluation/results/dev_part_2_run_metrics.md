# Metrics report: dev_part_2.json

- **Run:** run-20261108T034908-fda0fb · 2026-11-08T08:50:19+00:00 · 100 tickets
- **System version:** commit 6390615 · prompts PR-01 v1.2, PR-02 v1.0 · writer openai/gpt-oss-20b (backup openai/gpt-oss-120b) · checker qwen/qwen3.8-27b · classifier logistic regression on all-MiniLM-L6-v2 embeddings, C=10 (D-018) · threshold 0.85
- **Answer key in the file:** yes, used only to mark this report

## Volume

| Processed | Answered automatically | Escalated | Blocked by guardrails |
|---|---|---|---|
| 100 | 51 (51.0%) | 35 (35.0%) | 14 (14.0%) |

## Business

| First contact resolution | Escalation rate | Mean response time | Median response time |
|---|---|---|---|
| 51.0% | 49.0% | 179.5 s | 158.8 s |

First contact resolution counts only tickets closed with no person involved; "Draft ready" hand-overs count as escalations (FR-07).

## Technical

- **Latency:** median 158.8 s, 95th percentile 412.0 s (target: under 3 s for 95%, NFR-01)
- **Model calls:** 394 in total, 3.94 per ticket
- **Decisions logged:** 431 rows; 100 final outcomes for 100 tickets -> reconciles (A8)
- **Guardrail activations:** grounding_model 7, grounding_words 7
- **Private data detections:** 0 (every one blocked, none sent)
- **Labels:** sent 51, Needs a specialist 49

## Marked against the answer key

- **Must-not tickets answered automatically:** 0 of 24 (target 0)
- **Answered automatically when the answer key says a person:** 14 of 51 automatic replies
- **Should-be-automatic tickets answered automatically:** 37 of 52 (71.2%)
- **Correct first contact resolution** (answered, and the answer key agrees): 37.0%
- **Retrieval hit rate** (an expected article in the top 5): 62 of 63 (98.4%)
- **Citation accuracy** (automatic replies citing an expected article): 40 of 40 (100.0%; target 95%)
- **Type accuracy:** 100.0%

### Classification precision and recall per type

```
                         precision    recall  f1-score   support

         account_access      1.000     1.000     1.000         4
          api_key_issue      1.000     1.000     1.000         4
     api_usage_question      1.000     1.000     1.000         4
 authentication_failure      1.000     1.000     1.000         5
          billing_query      1.000     1.000     1.000         5
     compliance_request      1.000     1.000     1.000         8
     configuration_help      1.000     1.000     1.000         4
            data_export      1.000     1.000     1.000         4
         data_residency      1.000     1.000     1.000         7
         database_issue      1.000     1.000     1.000         6
     deployment_failure      1.000     1.000     1.000         5
        feature_request      1.000     1.000     1.000         5
       integration_help      1.000     1.000     1.000         3
             onboarding      1.000     1.000     1.000         2
performance_degradation      1.000     1.000     1.000         2
       quota_or_overage      1.000     1.000     1.000         3
             rate_limit      1.000     1.000     1.000         2
       rollback_request      1.000     1.000     1.000         6
      security_incident      1.000     1.000     1.000         8
      sso_configuration      1.000     1.000     1.000         5
        unclear_request      1.000     1.000     1.000         3
          webhook_issue      1.000     1.000     1.000         5

               accuracy                          1.000       100
              macro avg      1.000     1.000     1.000       100
           weighted avg      1.000     1.000     1.000       100

```

Confusion matrix (rows = true type, columns = predicted, sorted type order):

```
[[4 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 4 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 4 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 8 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 4 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 4 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 7 0 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 6 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 5 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 5 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 3 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 2 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 0 2 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 3 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 2 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 6 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 8 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 5 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 3 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 5]]
```

### Calibration (Evaluation Framework)

| Band | Tickets | Stated confidence | Observed accuracy | Gap |
|---|---|---|---|---|
| 0.8-1.0 | 100 | 100.0% | 100.0% | -0.0 points |

### Results by customer group (NFR-06: under 5 points between groups)

Resolution rate = answered automatically. Quality score = share of automatic replies that cite an expected article and passed every guardrail. Groups under 10 tickets are shown but not compared.

| Group | Value | Tickets | Resolution rate | Quality score | Must-not answered |
|---|---|---|---|---|---|
| tier | business | 30 | 56.7% | 88.2% | 0 |
| tier | enterprise | 16 | 62.5% | 70.0% | 0 |
| tier | standard | 54 | 44.4% | 75.0% | 0 |
| region | asia_pacific | 14 | 42.9% | 83.3% | 0 |
| region | europe | 32 | 56.2% | 83.3% | 0 |
| region | latin_america | 14 | 28.6% | 0.0% | 0 |
| region | north_america | 40 | 57.5% | 87.0% | 0 |
| language_fluency | fluent | 72 | 50.0% | 75.0% | 0 |
| language_fluency | non_fluent | 28 | 53.6% | 86.7% | 0 |
| channel | chat | 31 | 45.2% | 71.4% | 0 |
| channel | docs_comment | 17 | 58.8% | 60.0% | 0 |
| channel | email | 36 | 50.0% | 88.9% | 0 |
| channel | forum | 16 | 56.2% | 88.9% | 0 |

Run time: 301.5 minutes.
