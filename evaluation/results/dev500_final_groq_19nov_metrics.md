# Metrics report: development_tickets.json

- **Run:** run-20261119T183631-572adc · 2026-11-20T04:45:41+00:00 · 500 tickets
- **System version:** commit 0364036 · prompts PR-01 v1.7, PR-02 v1.0 · writer openai/gpt-oss-20b (backup openai/gpt-oss-120b) via Groq direct (free tier) · checker qwen/qwen3.8-27b · classifier logistic regression on all-MiniLM-L6-v2 embeddings, C=10 (D-018) · threshold 0.85 · reply cache off (fresh run) · experiment: trim on, writer reads 3 articles, narrowed safety rules on, type-aware search on, question rules on, learned decisions on, plan rule on
- **Answer key in the file:** yes, used only to mark this report

## Volume

| Processed | Answered automatically | Escalated | Blocked by guardrails |
|---|---|---|---|
| 500 | 330 (66.0%) | 158 (31.6%) | 12 (2.4%) |

## Business

| First contact resolution | Escalation rate | Mean response time | Median response time |
|---|---|---|---|
| 66.0% | 34.0% | 72.0 s | 2.7 s |

First contact resolution counts only tickets closed with no person involved; "Draft ready" hand-overs count as escalations (FR-07).

**Repeat contacts:** 1 of 500 tickets were the same customer asking about the same type within 7 days of an automatic reply in this run; 1 of them went to a person with the earlier reply attached (FR-14). Baseline (the history block, when people handled these tickets): 108 of 500 (21.6%).

## Technical

- **Latency:** median 2.7 s, 95th percentile 307.1 s (target: under 3 s for 95%, NFR-01)
- **Response time without rate-limit waits:** median 2.1 s, 95th percentile 7.2 s; time spent waiting on rate limits: 34733 s in total, on 240 of 500 tickets (17 Nov: kept apart, as the course team asked)
- **Model calls:** 1279 in total (retries included), 2.56 per ticket
- **Reply cache (D-025):** 0 of 379 replies and 0 of 358 checks reused, with no model call
- **Tokens:** writer 332,625 in + 39,319 out (1,414 per reply written); checker 163,243 in + 12,748 out; total 547,935 (1,096 per ticket)
- **Decisions logged:** 2237 rows; 500 final outcomes for 500 tickets -> reconciles (A8)
- **Guardrail activations:** grounding_model 12
- **Private data detections:** 0 (every one blocked, none sent)
- **Labels:** sent 330, Needs a specialist 154, Draft ready: check and send 16

## Marked against the answer key

- **Must-not tickets answered automatically:** 0 of 87 (target 0)
- **Answered automatically when the answer key says a person:** 72 of 330 automatic replies
- **Should-be-automatic tickets answered automatically:** 258 of 311 (83.0%)
- **First contact resolution that agrees with the answer key** (answered by the system, and the answer key also says to answer it; 17 Nov 2026: not called "correct", because the answer key can be wrong too): 51.6%
- **Retrieval hit rate** (an expected article in the top 5): 351 of 357 (98.3%)
- **Citation accuracy** (automatic replies citing an expected article): 252 of 271 (93.0%; target 95%)
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

Resolution rate = answered automatically. Quality score = of the automatic replies the answer key names an article for, the share that cite one of those articles (17 Nov: replies with no article in the answer key are left out, as they could never pass). Groups under 10 tickets are shown but not compared.

| Group | Value | Tickets | Resolution rate | Quality score | Must-not answered |
|---|---|---|---|---|---|
| tier | business | 164 | 67.1% | 85 of 94 (90.4%) | 0 |
| tier | enterprise | 83 | 67.5% | 47 of 49 (95.9%) | 0 |
| tier | standard | 253 | 64.8% | 120 of 128 (93.8%) | 0 |
| region | asia_pacific | 119 | 64.7% | 56 of 59 (94.9%) | 0 |
| region | europe | 151 | 68.9% | 83 of 91 (91.2%) | 0 |
| region | latin_america | 60 | 61.7% | 27 of 29 (93.1%) | 0 |
| region | north_america | 170 | 65.9% | 86 of 92 (93.5%) | 0 |
| language_fluency | fluent | 380 | 67.9% | 194 of 207 (93.7%) | 0 |
| language_fluency | non_fluent | 120 | 60.0% | 58 of 64 (90.6%) | 0 |
| channel | chat | 155 | 63.9% | 80 of 85 (94.1%) | 0 |
| channel | docs_comment | 78 | 69.2% | 33 of 36 (91.7%) | 0 |
| channel | email | 212 | 66.0% | 111 of 120 (92.5%) | 0 |
| channel | forum | 55 | 67.3% | 28 of 30 (93.3%) | 0 |

Run time: 609.5 minutes.
