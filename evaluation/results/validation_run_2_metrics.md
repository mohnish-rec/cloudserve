# Metrics report: validation_tickets.json

- **Run:** run-20261109T115648-938217 · 2026-11-09T15:50:03+00:00 · 80 tickets
- **System version:** commit 24a8e7f · prompts PR-01 v1.2, PR-02 v1.0 · writer openai/gpt-oss-20b (backup openai/gpt-oss-120b) · checker qwen/qwen3.8-27b · classifier logistic regression on all-MiniLM-L6-v2 embeddings, C=10 (D-018) · threshold 0.85
- **Answer key in the file:** yes, used only to mark this report

## Volume

| Processed | Answered automatically | Escalated | Blocked by guardrails |
|---|---|---|---|
| 80 | 43 (53.8%) | 32 (40.0%) | 5 (6.2%) |

## Business

| First contact resolution | Escalation rate | Mean response time | Median response time |
|---|---|---|---|
| 53.8% | 46.2% | 173.8 s | 176.0 s |

First contact resolution counts only tickets closed with no person involved; "Draft ready" hand-overs count as escalations (FR-07).

## Technical

- **Latency:** median 176.0 s, 95th percentile 414.3 s (target: under 3 s for 95%, NFR-01)
- **Model calls:** 316 in total (retries included), 3.95 per ticket
- **Tokens:** writer 65,198 in + 10,604 out (1,547 per reply written); checker 26,242 in + 2,337 out; total 104,381 (1,305 per ticket)
- **Decisions logged:** 337 rows; 80 final outcomes for 80 tickets -> reconciles (A8)
- **Guardrail activations:** grounding_model 4, grounding_words 1
- **Private data detections:** 0 (every one blocked, none sent)
- **Labels:** sent 43, Needs a specialist 37

## Marked against the answer key

- **Must-not tickets answered automatically:** 0 of 14 (target 0)
- **Answered automatically when the answer key says a person:** 13 of 43 automatic replies
- **Should-be-automatic tickets answered automatically:** 30 of 48 (62.5%)
- **Correct first contact resolution** (answered, and the answer key agrees): 37.5%
- **Retrieval hit rate** (an expected article in the top 5): 52 of 53 (98.1%)
- **Citation accuracy** (automatic replies citing an expected article): 30 of 31 (96.8%; target 95%)
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
| tier | business | 30 | 70.0% | 71.4% | 0 |
| tier | enterprise | 8 | 50.0% | 100.0% | 0 |
| tier | standard | 42 | 42.9% | 61.1% | 0 |
| region | asia_pacific | 21 | 52.4% | 90.9% | 0 |
| region | europe | 25 | 60.0% | 66.7% | 0 |
| region | latin_america | 7 | 28.6% | 100.0% | 0 |
| region | north_america | 27 | 55.6% | 53.3% | 0 |
| language_fluency | fluent | 61 | 52.5% | 78.1% | 0 |
| language_fluency | non_fluent | 19 | 57.9% | 45.5% | 0 |
| channel | chat | 22 | 59.1% | 69.2% | 0 |
| channel | docs_comment | 16 | 56.2% | 66.7% | 0 |
| channel | email | 31 | 48.4% | 66.7% | 0 |
| channel | forum | 11 | 54.5% | 83.3% | 0 |

Run time: 234.3 minutes.
