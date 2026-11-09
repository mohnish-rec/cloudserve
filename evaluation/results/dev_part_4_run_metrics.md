# Metrics report: dev_part_4.json

- **Run:** run-20261108T180313-64d8eb · 2026-11-08T23:51:09+00:00 · 100 tickets
- **System version:** commit 6390615 · prompts PR-01 v1.2, PR-02 v1.0 · writer openai/gpt-oss-20b (backup openai/gpt-oss-120b) · checker qwen/qwen3.8-27b · classifier logistic regression on all-MiniLM-L6-v2 embeddings, C=10 (D-018) · threshold 0.85
- **Answer key in the file:** yes, used only to mark this report

## Volume

| Processed | Answered automatically | Escalated | Blocked by guardrails |
|---|---|---|---|
| 100 | 54 (54.0%) | 23 (23.0%) | 23 (23.0%) |

## Business

| First contact resolution | Escalation rate | Mean response time | Median response time |
|---|---|---|---|
| 54.0% | 46.0% | 207.3 s | 259.8 s |

First contact resolution counts only tickets closed with no person involved; "Draft ready" hand-overs count as escalations (FR-07).

## Technical

- **Latency:** median 259.8 s, 95th percentile 400.7 s (target: under 3 s for 95%, NFR-01)
- **Model calls:** 480 in total (retries included), 4.80 per ticket
- **Tokens:** writer 102,647 in + 18,137 out (1,569 per reply written); checker 35,215 in + 3,063 out; total 159,062 (1,591 per ticket)
- **Decisions logged:** 454 rows; 100 final outcomes for 100 tickets -> reconciles (A8)
- **Guardrail activations:** grounding_model 12, grounding_words 11
- **Private data detections:** 0 (every one blocked, none sent)
- **Labels:** sent 54, Needs a specialist 46

## Marked against the answer key

- **Must-not tickets answered automatically:** 0 of 15 (target 0)
- **Answered automatically when the answer key says a person:** 11 of 54 automatic replies
- **Should-be-automatic tickets answered automatically:** 43 of 68 (63.2%)
- **Correct first contact resolution** (answered, and the answer key agrees): 43.0%
- **Retrieval hit rate** (an expected article in the top 5): 77 of 77 (100.0%)
- **Citation accuracy** (automatic replies citing an expected article): 45 of 46 (97.8%; target 95%)
- **Type accuracy:** 100.0%

### Classification precision and recall per type

```
                         precision    recall  f1-score   support

         account_access      1.000     1.000     1.000         5
          api_key_issue      1.000     1.000     1.000         6
     api_usage_question      1.000     1.000     1.000         5
 authentication_failure      1.000     1.000     1.000         2
     compliance_request      1.000     1.000     1.000         4
     configuration_help      1.000     1.000     1.000         2
            data_export      1.000     1.000     1.000         8
         data_residency      1.000     1.000     1.000         6
         database_issue      1.000     1.000     1.000         8
     deployment_failure      1.000     1.000     1.000         3
        feature_request      1.000     1.000     1.000         5
       integration_help      1.000     1.000     1.000         3
             onboarding      1.000     1.000     1.000         3
performance_degradation      1.000     1.000     1.000         4
       quota_or_overage      1.000     1.000     1.000         8
             rate_limit      1.000     1.000     1.000         1
       rollback_request      1.000     1.000     1.000         8
      security_incident      1.000     1.000     1.000         3
      sso_configuration      1.000     1.000     1.000         7
        unclear_request      1.000     1.000     1.000         3
          webhook_issue      1.000     1.000     1.000         6

               accuracy                          1.000       100
              macro avg      1.000     1.000     1.000       100
           weighted avg      1.000     1.000     1.000       100

```

Confusion matrix (rows = true type, columns = predicted, sorted type order):

```
[[5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 6 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 4 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 8 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 6 0 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 8 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 3 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 5 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 3 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 3 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 4 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 0 8 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 8 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 3 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 7 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 3 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 6]]
```

### Calibration (Evaluation Framework)

| Band | Tickets | Stated confidence | Observed accuracy | Gap |
|---|---|---|---|---|
| 0.8-1.0 | 100 | 100.0% | 100.0% | -0.0 points |

### Results by customer group (NFR-06: under 5 points between groups)

Resolution rate = answered automatically. Quality score = share of automatic replies that cite an expected article and passed every guardrail. Groups under 10 tickets are shown but not compared.

| Group | Value | Tickets | Resolution rate | Quality score | Must-not answered |
|---|---|---|---|---|---|
| tier | business | 31 | 58.1% | 88.9% | 0 |
| tier | enterprise | 19 | 57.9% | 72.7% | 0 |
| tier | standard | 50 | 50.0% | 84.0% | 0 |
| region | asia_pacific | 24 | 37.5% | 66.7% | 0 |
| region | europe | 28 | 57.1% | 87.5% | 0 |
| region | latin_america | 11 | 63.6% | 85.7% | 0 |
| region | north_america | 37 | 59.5% | 86.4% | 0 |
| language_fluency | fluent | 79 | 54.4% | 88.4% | 0 |
| language_fluency | non_fluent | 21 | 52.4% | 63.6% | 0 |
| channel | chat | 37 | 64.9% | 83.3% | 0 |
| channel | docs_comment | 13 | 38.5% | 60.0% | 0 |
| channel | email | 44 | 50.0% | 86.4% | 0 |
| channel | forum | 6 | 50.0% | 100.0% | 0 |

Run time: 349.2 minutes.
