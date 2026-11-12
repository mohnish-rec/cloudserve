# Metrics report: validation_tickets.json

- **Run:** run-20261112T045033-7da05e · 2026-11-12T04:58:09+00:00 · 80 tickets
- **System version:** commit 4d48f21 · prompts PR-01 v1.7, PR-02 v1.0 · writer openai/gpt-oss-20b (backup openai/gpt-oss-120b) via Groq direct (free tier) · checker qwen/qwen3.8-27b · classifier logistic regression on all-MiniLM-L6-v2 embeddings, C=10 (D-018) · threshold 0.85 · reply cache off (fresh run) · experiment: trim on, writer reads 3 articles, narrowed safety rules on, type-aware search on, question rules on
- **Answer key in the file:** yes, used only to mark this report

## Volume

| Processed | Answered automatically | Escalated | Blocked by guardrails |
|---|---|---|---|
| 80 | 53 (66.2%) | 24 (30.0%) | 3 (3.8%) |

## Business

| First contact resolution | Escalation rate | Mean response time | Median response time |
|---|---|---|---|
| 66.2% | 33.8% | 5.0 s | 4.6 s |

First contact resolution counts only tickets closed with no person involved; "Draft ready" hand-overs count as escalations (FR-07).

## Technical

- **Latency:** median 4.6 s, 95th percentile 10.5 s (target: under 3 s for 95%, NFR-01)
- **Model calls:** 141 in total (retries included), 1.76 per ticket
- **Reply cache (D-025):** 0 of 57 replies and 0 of 54 checks reused, with no model call
- **Tokens:** writer 64,697 in + 7,045 out (1,407 per reply written); checker 32,016 in + 2,528 out; total 106,286 (1,329 per ticket)
- **Decisions logged:** 353 rows; 80 final outcomes for 80 tickets -> reconciles (A8)
- **Guardrail activations:** tone_and_scope 2, grounding_model 1
- **Private data detections:** 0 (every one blocked, none sent)
- **Labels:** sent 53, Needs a specialist 27

## Marked against the answer key

- **Must-not tickets answered automatically:** 0 of 14 (target 0)
- **Answered automatically when the answer key says a person:** 15 of 53 automatic replies
- **Should-be-automatic tickets answered automatically:** 38 of 48 (79.2%)
- **Correct first contact resolution** (answered, and the answer key agrees): 47.5%
- **Retrieval hit rate** (an expected article in the top 5): 52 of 53 (98.1%)
- **Citation accuracy** (automatic replies citing an expected article): 38 of 39 (97.4%; target 95%)
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
| tier | business | 30 | 80.0% | 75.0% | 0 |
| tier | enterprise | 8 | 62.5% | 100.0% | 0 |
| tier | standard | 42 | 57.1% | 62.5% | 0 |
| region | asia_pacific | 21 | 66.7% | 78.6% | 0 |
| region | europe | 25 | 72.0% | 72.2% | 0 |
| region | latin_america | 7 | 28.6% | 100.0% | 0 |
| region | north_america | 27 | 70.4% | 63.2% | 0 |
| language_fluency | fluent | 61 | 70.5% | 79.1% | 0 |
| language_fluency | non_fluent | 19 | 52.6% | 40.0% | 0 |
| channel | chat | 22 | 72.7% | 68.8% | 0 |
| channel | docs_comment | 16 | 56.2% | 66.7% | 0 |
| channel | email | 31 | 71.0% | 72.7% | 0 |
| channel | forum | 11 | 54.5% | 83.3% | 0 |

Run time: 7.9 minutes.
