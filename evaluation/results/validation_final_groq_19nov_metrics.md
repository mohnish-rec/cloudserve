# Metrics report: validation_tickets.json

- **Run:** run-20261119T182708-10f116 · 2026-11-19T18:34:48+00:00 · 80 tickets
- **System version:** commit 9861605 · prompts PR-01 v1.7, PR-02 v1.0 · writer openai/gpt-oss-20b (backup openai/gpt-oss-120b) via Groq direct (free tier) · checker qwen/qwen3.8-27b · classifier logistic regression on all-MiniLM-L6-v2 embeddings, C=10 (D-018) · threshold 0.85 · reply cache off (fresh run) · experiment: trim on, writer reads 3 articles, narrowed safety rules on, type-aware search on, question rules on, learned decisions on, plan rule on
- **Answer key in the file:** yes, used only to mark this report

## Volume

| Processed | Answered automatically | Escalated | Blocked by guardrails |
|---|---|---|---|
| 80 | 53 (66.2%) | 24 (30.0%) | 3 (3.8%) |

## Business

| First contact resolution | Escalation rate | Mean response time | Median response time |
|---|---|---|---|
| 66.2% | 33.8% | 4.9 s | 5.8 s |

First contact resolution counts only tickets closed with no person involved; "Draft ready" hand-overs count as escalations (FR-07).

**Repeat contacts:** 1 of 80 tickets were the same customer asking about the same type within 7 days of an automatic reply in this run; 1 of them went to a person with the earlier reply attached (FR-14). Baseline (the history block, when people handled these tickets): 17 of 80 (21.2%).

## Technical

- **Latency:** median 5.8 s, 95th percentile 10.1 s (target: under 3 s for 95%, NFR-01)
- **Response time without rate-limit waits:** median 2.8 s, 95th percentile 3.4 s; time spent waiting on rate limits: 229 s in total, on 45 of 80 tickets (17 Nov: kept apart, as the course team asked)
- **Model calls:** 152 in total (retries included), 1.90 per ticket
- **Reply cache (D-025):** 0 of 59 replies and 0 of 57 checks reused, with no model call
- **Tokens:** writer 67,321 in + 8,149 out (1,424 per reply written); checker 35,299 in + 2,863 out; total 113,632 (1,420 per ticket)
- **Decisions logged:** 356 rows; 80 final outcomes for 80 tickets -> reconciles (A8)
- **Guardrail activations:** grounding_model 3
- **Private data detections:** 0 (every one blocked, none sent)
- **Labels:** sent 53, Needs a specialist 26, Draft ready: check and send 1

## Marked against the answer key

- **Must-not tickets answered automatically:** 0 of 14 (target 0)
- **Answered automatically when the answer key says a person:** 12 of 53 automatic replies
- **Should-be-automatic tickets answered automatically:** 41 of 48 (85.4%)
- **First contact resolution that agrees with the answer key** (answered by the system, and the answer key also says to answer it; 17 Nov 2026: not called "correct", because the answer key can be wrong too): 51.2%
- **Retrieval hit rate** (an expected article in the top 5): 52 of 53 (98.1%)
- **Citation accuracy** (automatic replies citing an expected article): 41 of 42 (97.6%; target 95%)
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

Resolution rate = answered automatically. Quality score = of the automatic replies the answer key names an article for, the share that cite one of those articles (17 Nov: replies with no article in the answer key are left out, as they could never pass). Groups under 10 tickets are shown but not compared.

| Group | Value | Tickets | Resolution rate | Quality score | Must-not answered |
|---|---|---|---|---|---|
| tier | business | 30 | 86.7% | 20 of 20 (100.0%) | 0 |
| tier | enterprise | 8 | 75.0% | 6 of 6 (100.0%) | 0 |
| tier | standard | 42 | 50.0% | 15 of 16 (93.8%) | 0 |
| region | asia_pacific | 21 | 76.2% | 14 of 14 (100.0%) | 0 |
| region | europe | 25 | 72.0% | 13 of 14 (92.9%) | 0 |
| region | latin_america | 7 | 28.6% | 2 of 2 (100.0%) | 0 |
| region | north_america | 27 | 63.0% | 12 of 12 (100.0%) | 0 |
| language_fluency | fluent | 61 | 70.5% | 35 of 36 (97.2%) | 0 |
| language_fluency | non_fluent | 19 | 52.6% | 6 of 6 (100.0%) | 0 |
| channel | chat | 22 | 72.7% | 11 of 12 (91.7%) | 0 |
| channel | docs_comment | 16 | 62.5% | 7 of 7 (100.0%) | 0 |
| channel | email | 31 | 64.5% | 16 of 16 (100.0%) | 0 |
| channel | forum | 11 | 63.6% | 7 of 7 (100.0%) | 0 |

Run time: 8.0 minutes.
