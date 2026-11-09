# Metrics report: dev_part_1.json

- **Run:** run-20261108T031855-ae702a · 2026-11-08T03:41:31+00:00 · 100 tickets
- **System version:** commit 6390615 · prompts PR-01 v1.2, PR-02 v1.0 · writer openai/gpt-oss-20b (backup openai/gpt-oss-120b) · checker qwen/qwen3.8-27b · classifier logistic regression on all-MiniLM-L6-v2 embeddings, C=10 (D-018) · threshold 0.85
- **Answer key in the file:** yes, used only to mark this report

## Volume

| Processed | Answered automatically | Escalated | Blocked by guardrails |
|---|---|---|---|
| 100 | 64 (64.0%) | 20 (20.0%) | 16 (16.0%) |

## Business

| First contact resolution | Escalation rate | Mean response time | Median response time |
|---|---|---|---|
| 64.0% | 36.0% | 12.7 s | 2.4 s |

First contact resolution counts only tickets closed with no person involved; "Draft ready" hand-overs count as escalations (FR-07).

## Technical

- **Latency:** median 2.4 s, 95th percentile 44.3 s (target: under 3 s for 95%, NFR-01)
- **Model calls:** 151 in total, 1.51 per ticket
- **Decisions logged:** 460 rows; 100 final outcomes for 100 tickets -> reconciles (A8)
- **Guardrail activations:** grounding_words 9, grounding_model 7
- **Private data detections:** 0 (every one blocked, none sent)
- **Labels:** sent 64, Needs a specialist 36

## Marked against the answer key

- **Must-not tickets answered automatically:** 0 of 12 (target 0)
- **Answered automatically when the answer key says a person:** 18 of 64 automatic replies
- **Should-be-automatic tickets answered automatically:** 46 of 65 (70.8%)
- **Correct first contact resolution** (answered, and the answer key agrees): 46.0%
- **Retrieval hit rate** (an expected article in the top 5): 70 of 72 (97.2%)
- **Citation accuracy** (automatic replies citing an expected article): 42 of 47 (89.4%; target 95%)
- **Type accuracy:** 100.0%

### Classification precision and recall per type

```
                         precision    recall  f1-score   support

         account_access      1.000     1.000     1.000         6
          api_key_issue      1.000     1.000     1.000         3
     api_usage_question      1.000     1.000     1.000         5
 authentication_failure      1.000     1.000     1.000         5
          billing_query      1.000     1.000     1.000         6
     compliance_request      1.000     1.000     1.000         4
     configuration_help      1.000     1.000     1.000         4
            data_export      1.000     1.000     1.000         5
         data_residency      1.000     1.000     1.000         3
         database_issue      1.000     1.000     1.000         5
     deployment_failure      1.000     1.000     1.000        10
        feature_request      1.000     1.000     1.000         3
       integration_help      1.000     1.000     1.000         6
             onboarding      1.000     1.000     1.000         1
performance_degradation      1.000     1.000     1.000         4
       quota_or_overage      1.000     1.000     1.000         6
             rate_limit      1.000     1.000     1.000         3
       rollback_request      1.000     1.000     1.000         8
      security_incident      1.000     1.000     1.000         4
      sso_configuration      1.000     1.000     1.000         5
        unclear_request      1.000     1.000     1.000         1
          webhook_issue      1.000     1.000     1.000         3

               accuracy                          1.000       100
              macro avg      1.000     1.000     1.000       100
           weighted avg      1.000     1.000     1.000       100

```

Confusion matrix (rows = true type, columns = predicted, sorted type order):

```
[[ 6  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  3  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  5  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  5  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  6  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  4  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  4  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  5  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  3  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  5  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0 10  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  3  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  6  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  1  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  4  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  6  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  3  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  8  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  4  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  5  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  3]]
```

### Calibration (Evaluation Framework)

| Band | Tickets | Stated confidence | Observed accuracy | Gap |
|---|---|---|---|---|
| 0.8-1.0 | 100 | 100.0% | 100.0% | -0.0 points |

### Results by customer group (NFR-06: under 5 points between groups)

Resolution rate = answered automatically. Quality score = share of automatic replies that cite an expected article and passed every guardrail. Groups under 10 tickets are shown but not compared.

| Group | Value | Tickets | Resolution rate | Quality score | Must-not answered |
|---|---|---|---|---|---|
| tier | business | 35 | 68.6% | 66.7% | 0 |
| tier | enterprise | 14 | 42.9% | 100.0% | 0 |
| tier | standard | 51 | 66.7% | 58.8% | 0 |
| region | asia_pacific | 27 | 63.0% | 76.5% | 0 |
| region | europe | 28 | 67.9% | 57.9% | 0 |
| region | latin_america | 16 | 75.0% | 75.0% | 0 |
| region | north_america | 29 | 55.2% | 56.2% | 0 |
| language_fluency | fluent | 76 | 64.5% | 65.3% | 0 |
| language_fluency | non_fluent | 24 | 62.5% | 66.7% | 0 |
| channel | chat | 32 | 62.5% | 80.0% | 0 |
| channel | docs_comment | 13 | 30.8% | 25.0% | 0 |
| channel | email | 46 | 69.6% | 62.5% | 0 |
| channel | forum | 9 | 88.9% | 62.5% | 0 |

Run time: 23.3 minutes.
