# Metrics report: development_tickets.json

- **Run:** run-20261117T152328-15ff53 · 2026-11-17T15:52:44+00:00 · 500 tickets
- **System version:** commit 0a1fd5b · prompts PR-01 v1.7, PR-02 v1.0 · writer openai/gpt-oss-20b (backup openai/gpt-oss-120b) via OpenRouter (paid, sandbox) · checker qwen/qwen3.8-27b · classifier logistic regression on all-MiniLM-L6-v2 embeddings, C=10 (D-018) · threshold 0.85 · reply cache refresh (fresh answers, nothing stored was read; new answers stored) · experiment: trim on, writer reads 3 articles, narrowed safety rules on, type-aware search on, question rules on, learned decisions on, plan rule on
- **Answer key in the file:** yes, used only to mark this report

## Volume

| Processed | Answered automatically | Escalated | Blocked by guardrails |
|---|---|---|---|
| 500 | 340 (68.0%) | 159 (31.8%) | 1 (0.2%) |

## Business

| First contact resolution | Escalation rate | Mean response time | Median response time |
|---|---|---|---|
| 68.0% | 32.0% | 2.7 s | 2.3 s |

First contact resolution counts only tickets closed with no person involved; "Draft ready" hand-overs count as escalations (FR-07).

**Repeat contacts:** 1 of 500 tickets were the same customer asking about the same type within 7 days of an automatic reply in this run; 1 of them went to a person with the earlier reply attached (FR-14). Baseline (the history block, when people handled these tickets): 108 of 500 (21.6%).

## Technical

- **Latency:** median 2.3 s, 95th percentile 6.3 s (target: under 3 s for 95%, NFR-01)
- **Response time without rate-limit waits:** median 2.3 s, 95th percentile 6.3 s; time spent waiting on rate limits: 7 s in total, on 7 of 500 tickets (17 Nov: kept apart, as the course team asked)
- **Model calls:** 512 in total (retries included), 1.02 per ticket
- **Reply cache (D-025):** 0 of 379 replies and 0 of 357 checks reused, with no model call
- **Tokens:** writer 332,625 in + 36,637 out (1,404 per reply written); checker 165,917 in + 13,171 out; total 548,350 (1,097 per ticket)
- **Decisions logged:** 2236 rows; 500 final outcomes for 500 tickets -> reconciles (A8)
- **Guardrail activations:** grounding_model 1
- **Private data detections:** 0 (every one blocked, none sent)
- **Labels:** sent 340, Needs a specialist 144, Draft ready: check and send 16

## Marked against the answer key

- **Must-not tickets answered automatically:** 0 of 87 (target 0)
- **Answered automatically when the answer key says a person:** 75 of 340 automatic replies
- **Should-be-automatic tickets answered automatically:** 265 of 311 (85.2%)
- **Correct first contact resolution** (answered, and the answer key agrees): 53.0%
- **Retrieval hit rate** (an expected article in the top 5): 351 of 357 (98.3%)
- **Citation accuracy** (automatic replies citing an expected article): 259 of 278 (93.2%; target 95%)
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
| tier | business | 164 | 68.9% | 87 of 96 (90.6%) | 0 |
| tier | enterprise | 83 | 68.7% | 47 of 49 (95.9%) | 0 |
| tier | standard | 253 | 67.2% | 125 of 133 (94.0%) | 0 |
| region | asia_pacific | 119 | 66.4% | 58 of 61 (95.1%) | 0 |
| region | europe | 151 | 70.9% | 84 of 92 (91.3%) | 0 |
| region | latin_america | 60 | 68.3% | 30 of 32 (93.8%) | 0 |
| region | north_america | 170 | 66.5% | 87 of 93 (93.5%) | 0 |
| language_fluency | fluent | 380 | 69.2% | 199 of 212 (93.9%) | 0 |
| language_fluency | non_fluent | 120 | 64.2% | 60 of 66 (90.9%) | 0 |
| channel | chat | 155 | 66.5% | 83 of 88 (94.3%) | 0 |
| channel | docs_comment | 78 | 70.5% | 34 of 37 (91.9%) | 0 |
| channel | email | 212 | 67.9% | 113 of 122 (92.6%) | 0 |
| channel | forum | 55 | 69.1% | 29 of 31 (93.5%) | 0 |

Run time: 29.5 minutes.
