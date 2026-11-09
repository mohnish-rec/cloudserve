# Metrics report: dev_part_3.json

- **Run:** run-20261108T151055-ff32a1 · 2026-11-08T17:59:46+00:00 · 100 tickets
- **System version:** commit 6390615 · prompts PR-01 v1.2, PR-02 v1.0 · writer openai/gpt-oss-20b (backup openai/gpt-oss-120b) · checker qwen/qwen3.8-27b · classifier logistic regression on all-MiniLM-L6-v2 embeddings, C=10 (D-018) · threshold 0.85
- **Answer key in the file:** yes, used only to mark this report

## Volume

| Processed | Answered automatically | Escalated | Blocked by guardrails |
|---|---|---|---|
| 100 | 50 (50.0%) | 34 (34.0%) | 16 (16.0%) |

## Business

| First contact resolution | Escalation rate | Mean response time | Median response time |
|---|---|---|---|
| 50.0% | 50.0% | 100.3 s | 3.8 s |

First contact resolution counts only tickets closed with no person involved; "Draft ready" hand-overs count as escalations (FR-07).

## Technical

- **Latency:** median 3.8 s, 95th percentile 371.6 s (target: under 3 s for 95%, NFR-01)
- **Model calls:** 275 in total (retries included), 2.75 per ticket
- **Tokens:** writer 89,259 in + 14,183 out (1,544 per reply written); checker 33,299 in + 2,954 out; total 139,695 (1,397 per ticket)
- **Decisions logged:** 433 rows; 100 final outcomes for 100 tickets -> reconciles (A8)
- **Guardrail activations:** grounding_words 9, grounding_model 7
- **Private data detections:** 0 (every one blocked, none sent)
- **Labels:** Needs a specialist 50, sent 50

## Marked against the answer key

- **Must-not tickets answered automatically:** 0 of 22 (target 0)
- **Answered automatically when the answer key says a person:** 17 of 50 automatic replies
- **Should-be-automatic tickets answered automatically:** 33 of 58 (56.9%)
- **Correct first contact resolution** (answered, and the answer key agrees): 33.0%
- **Retrieval hit rate** (an expected article in the top 5): 67 of 71 (94.4%)
- **Citation accuracy** (automatic replies citing an expected article): 35 of 38 (92.1%; target 95%)
- **Type accuracy:** 100.0%

### Classification precision and recall per type

```
                         precision    recall  f1-score   support

         account_access      1.000     1.000     1.000         2
          api_key_issue      1.000     1.000     1.000         3
     api_usage_question      1.000     1.000     1.000         5
 authentication_failure      1.000     1.000     1.000         5
          billing_query      1.000     1.000     1.000         4
     compliance_request      1.000     1.000     1.000         8
     configuration_help      1.000     1.000     1.000         3
            data_export      1.000     1.000     1.000         3
         data_residency      1.000     1.000     1.000         5
         database_issue      1.000     1.000     1.000         3
     deployment_failure      1.000     1.000     1.000         4
        feature_request      1.000     1.000     1.000         5
       integration_help      1.000     1.000     1.000         7
             onboarding      1.000     1.000     1.000         9
performance_degradation      1.000     1.000     1.000        10
       quota_or_overage      1.000     1.000     1.000         3
             rate_limit      1.000     1.000     1.000         5
       rollback_request      1.000     1.000     1.000         1
      security_incident      1.000     1.000     1.000         7
      sso_configuration      1.000     1.000     1.000         2
        unclear_request      1.000     1.000     1.000         2
          webhook_issue      1.000     1.000     1.000         4

               accuracy                          1.000       100
              macro avg      1.000     1.000     1.000       100
           weighted avg      1.000     1.000     1.000       100

```

Confusion matrix (rows = true type, columns = predicted, sorted type order):

```
[[ 2  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  3  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  5  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  5  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  4  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  8  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  3  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  3  0  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  5  0  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  3  0  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  4  0  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  5  0  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  7  0  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  9  0  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0 10  0  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  3  0  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  5  0  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  1  0  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  7  0  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  2  0  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  2  0]
 [ 0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  4]]
```

### Calibration (Evaluation Framework)

| Band | Tickets | Stated confidence | Observed accuracy | Gap |
|---|---|---|---|---|
| 0.8-1.0 | 100 | 100.0% | 100.0% | -0.0 points |

### Results by customer group (NFR-06: under 5 points between groups)

Resolution rate = answered automatically. Quality score = share of automatic replies that cite an expected article and passed every guardrail. Groups under 10 tickets are shown but not compared.

| Group | Value | Tickets | Resolution rate | Quality score | Must-not answered |
|---|---|---|---|---|---|
| tier | business | 30 | 60.0% | 77.8% | 0 |
| tier | enterprise | 21 | 42.9% | 66.7% | 0 |
| tier | standard | 49 | 46.9% | 65.2% | 0 |
| region | asia_pacific | 25 | 36.0% | 66.7% | 0 |
| region | europe | 34 | 50.0% | 82.4% | 0 |
| region | latin_america | 6 | 50.0% | 66.7% | 0 |
| region | north_america | 35 | 60.0% | 61.9% | 0 |
| language_fluency | fluent | 76 | 52.6% | 65.0% | 0 |
| language_fluency | non_fluent | 24 | 41.7% | 90.0% | 0 |
| channel | chat | 28 | 53.6% | 73.3% | 0 |
| channel | docs_comment | 16 | 56.2% | 66.7% | 0 |
| channel | email | 39 | 43.6% | 64.7% | 0 |
| channel | forum | 17 | 52.9% | 77.8% | 0 |

Run time: 169.4 minutes.
