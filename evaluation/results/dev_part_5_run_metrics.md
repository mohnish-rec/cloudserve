# Metrics report: dev_part_5.json

- **Run:** run-20261109T002212-863aae · 2026-11-09T05:54:28+00:00 · 100 tickets
- **System version:** commit 6390615 · prompts PR-01 v1.2, PR-02 v1.0 · writer openai/gpt-oss-20b (backup openai/gpt-oss-120b) · checker qwen/qwen3.8-27b · classifier logistic regression on all-MiniLM-L6-v2 embeddings, C=10 (D-018) · threshold 0.85
- **Answer key in the file:** yes, used only to mark this report

## Volume

| Processed | Answered automatically | Escalated | Blocked by guardrails |
|---|---|---|---|
| 100 | 53 (53.0%) | 27 (27.0%) | 20 (20.0%) |

## Business

| First contact resolution | Escalation rate | Mean response time | Median response time |
|---|---|---|---|
| 53.0% | 47.0% | 198.0 s | 245.1 s |

First contact resolution counts only tickets closed with no person involved; "Draft ready" hand-overs count as escalations (FR-07).

## Technical

- **Latency:** median 245.1 s, 95th percentile 393.4 s (target: under 3 s for 95%, NFR-01)
- **Model calls:** 445 in total (retries included), 4.45 per ticket
- **Tokens:** writer 97,945 in + 16,786 out (1,550 per reply written); checker 33,904 in + 2,964 out; total 151,599 (1,516 per ticket)
- **Decisions logged:** 447 rows; 100 final outcomes for 100 tickets -> reconciles (A8)
- **Guardrail activations:** grounding_words 14, grounding_model 6
- **Private data detections:** 0 (every one blocked, none sent)
- **Labels:** sent 53, Needs a specialist 47

## Marked against the answer key

- **Must-not tickets answered automatically:** 0 of 14 (target 0)
- **Answered automatically when the answer key says a person:** 13 of 53 automatic replies
- **Should-be-automatic tickets answered automatically:** 40 of 68 (58.8%)
- **Correct first contact resolution** (answered, and the answer key agrees): 40.0%
- **Retrieval hit rate** (an expected article in the top 5): 73 of 74 (98.6%)
- **Citation accuracy** (automatic replies citing an expected article): 39 of 41 (95.1%; target 95%)
- **Type accuracy:** 100.0%

### Classification precision and recall per type

```
                         precision    recall  f1-score   support

         account_access      1.000     1.000     1.000         5
          api_key_issue      1.000     1.000     1.000         2
     api_usage_question      1.000     1.000     1.000         5
 authentication_failure      1.000     1.000     1.000         3
          billing_query      1.000     1.000     1.000         9
     compliance_request      1.000     1.000     1.000         2
     configuration_help      1.000     1.000     1.000         4
            data_export      1.000     1.000     1.000         9
         data_residency      1.000     1.000     1.000         8
         database_issue      1.000     1.000     1.000         4
     deployment_failure      1.000     1.000     1.000         5
        feature_request      1.000     1.000     1.000         2
       integration_help      1.000     1.000     1.000         2
             onboarding      1.000     1.000     1.000         7
performance_degradation      1.000     1.000     1.000         3
       quota_or_overage      1.000     1.000     1.000         3
             rate_limit      1.000     1.000     1.000         2
       rollback_request      1.000     1.000     1.000         5
      security_incident      1.000     1.000     1.000         4
      sso_configuration      1.000     1.000     1.000         7
        unclear_request      1.000     1.000     1.000         6
          webhook_issue      1.000     1.000     1.000         3

               accuracy                          1.000       100
              macro avg      1.000     1.000     1.000       100
           weighted avg      1.000     1.000     1.000       100

```

Confusion matrix (rows = true type, columns = predicted, sorted type order):

```
[[5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 3 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 9 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 4 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 9 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 8 0 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 4 0 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 5 0 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 2 0 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 2 0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 7 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 0 3 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 3 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 2 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 5 0 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 4 0 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 7 0 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 6 0]
 [0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 3]]
```

### Calibration (Evaluation Framework)

| Band | Tickets | Stated confidence | Observed accuracy | Gap |
|---|---|---|---|---|
| 0.8-1.0 | 100 | 100.0% | 100.0% | -0.0 points |

### Results by customer group (NFR-06: under 5 points between groups)

Resolution rate = answered automatically. Quality score = share of automatic replies that cite an expected article and passed every guardrail. Groups under 10 tickets are shown but not compared.

| Group | Value | Tickets | Resolution rate | Quality score | Must-not answered |
|---|---|---|---|---|---|
| tier | business | 38 | 50.0% | 73.7% | 0 |
| tier | enterprise | 13 | 61.5% | 75.0% | 0 |
| tier | standard | 49 | 53.1% | 73.1% | 0 |
| region | asia_pacific | 29 | 58.6% | 76.5% | 0 |
| region | europe | 29 | 51.7% | 73.3% | 0 |
| region | latin_america | 13 | 53.8% | 71.4% | 0 |
| region | north_america | 29 | 48.3% | 71.4% | 0 |
| language_fluency | fluent | 77 | 57.1% | 68.2% | 0 |
| language_fluency | non_fluent | 23 | 39.1% | 100.0% | 0 |
| channel | chat | 27 | 40.7% | 81.8% | 0 |
| channel | docs_comment | 19 | 47.4% | 55.6% | 0 |
| channel | email | 47 | 59.6% | 75.0% | 0 |
| channel | forum | 7 | 71.4% | 80.0% | 0 |

Run time: 333.1 minutes.
