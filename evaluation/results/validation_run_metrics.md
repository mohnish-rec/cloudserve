# Metrics report: validation_tickets.json

- **Run:** run-20261108T023049-56bd8c · 2026-11-08T02:42:42+00:00 · 80 tickets
- **System version:** commit ea6ee45 · prompts PR-01 v1.2, PR-02 v1.0 · writer openai/gpt-oss-20b (backup openai/gpt-oss-120b) · checker qwen/qwen3.8-27b · classifier logistic regression on all-MiniLM-L6-v2 embeddings, C=10 (D-018) · threshold 0.85
- **Answer key in the file:** yes, used only to mark this report

## Volume

| Processed | Answered automatically | Escalated | Blocked by guardrails |
|---|---|---|---|
| 80 | 38 (47.5%) | 32 (40.0%) | 10 (12.5%) |

## Business

| First contact resolution | Escalation rate | Mean response time | Median response time |
|---|---|---|---|
| 47.5% | 52.5% | 8.2 s | 2.1 s |

First contact resolution counts only tickets closed with no person involved; "Draft ready" hand-overs count as escalations (FR-07).

## Technical

- **Latency:** median 2.1 s, 95th percentile 44.1 s (target: under 3 s for 95%, NFR-01)
- **Model calls:** 93 in total, 1.16 per ticket
- **Decisions logged:** 337 rows; 80 final outcomes for 80 tickets -> reconciles (A8)
- **Guardrail activations:** grounding_words 5, grounding_model 5
- **Private data detections:** 0 (every one blocked, none sent)
- **Labels:** Needs a specialist 42, sent 38

## Marked against the answer key

- **Must-not tickets answered automatically:** 0 of 14 (target 0)
- **Answered automatically when the answer key says a person:** 13 of 38 automatic replies
- **Should-be-automatic tickets answered automatically:** 25 of 48 (52.1%)
- **Correct first contact resolution** (answered, and the answer key agrees): 31.2%
- **Retrieval hit rate** (an expected article in the top 5): 52 of 53 (98.1%)
- **Citation accuracy** (automatic replies citing an expected article): 25 of 26 (96.2%; target 95%)
- **Type accuracy:** 100.0%

### Classification precision and recall per type

```
                         precision    recall  f1-score   support

         account_access      1.000     1.000     1.000         4
          api_key_issue      1.000     1.000     1.000         6
     api_usage_question      1.000     1.000     1.000         4
 authentication_failure      1.000     1.000     1.000         3
          billing_query      1.000     1.000     1.000        10
     compliance_request      1.000     1.000     1.000         1
     configuration_help      1.000     1.000     1.000         3
            data_export      1.000     1.000     1.000         1
         data_residency      1.000     1.000     1.000         6
         database_issue      1.000     1.000     1.000         1
     deployment_failure      1.000     1.000     1.000         5
        feature_request      1.000     1.000     1.000         3
       integration_help      1.000     1.000     1.000         3
             onboarding      1.000     1.000     1.000         4
performance_degradation      1.000     1.000     1.000         3
       quota_or_overage      1.000     1.000     1.000         2
             rate_limit      1.000     1.000     1.000         1
       rollback_request      1.000     1.000     1.000         6
      security_incident      1.000     1.000     1.000         4
      sso_configuration      1.000     1.000     1.000         1
        unclear_request      1.000     1.000     1.000         6
          webhook_issue      1.000     1.000     1.000         3

               accuracy                          1.000        80
              macro avg      1.000     1.000     1.000        80
           weighted avg      1.000     1.000     1.000        80

```

Confusion matrix (rows = true type, columns = predicted, sorted type order):

```
[[ 4  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  6  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  4  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  3  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0 10  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  3  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  1  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  6  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  1  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  5  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  3  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  3  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  4  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  3  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  2  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  6  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  4  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  6  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  3]]
```

### Calibration (Evaluation Framework)

| Band | Tickets | Stated confidence | Observed accuracy | Gap |
|---|---|---|---|---|
| 0.8-1.0 | 80 | 100.0% | 100.0% | -0.0 points |

### Results by customer group (NFR-06: under 5 points between groups)

Resolution rate = answered automatically. Quality score = share of automatic replies that cite an expected article and passed every guardrail. Groups under 10 tickets are shown but not compared.

| Group | Value | Tickets | Resolution rate | Quality score | Must-not answered |
|---|---|---|---|---|---|
| tier | business | 30 | 56.7% | 64.7% | 0 |
| tier | enterprise | 8 | 25.0% | 100.0% | 0 |
| tier | standard | 42 | 45.2% | 63.2% | 0 |
| region | asia_pacific | 21 | 52.4% | 81.8% | 0 |
| region | europe | 25 | 52.0% | 69.2% | 0 |
| region | latin_america | 7 | 28.6% | 100.0% | 0 |
| region | north_america | 27 | 44.4% | 41.7% | 0 |
| language_fluency | fluent | 61 | 49.2% | 73.3% | 0 |
| language_fluency | non_fluent | 19 | 42.1% | 37.5% | 0 |
| channel | chat | 22 | 63.6% | 64.3% | 0 |
| channel | docs_comment | 16 | 31.2% | 40.0% | 0 |
| channel | email | 31 | 41.9% | 69.2% | 0 |
| channel | forum | 11 | 54.5% | 83.3% | 0 |

Run time: 12.2 minutes.
