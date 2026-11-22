# Metrics report: validation_tickets_20261122T024943.json

| Run | Date | Tickets | Run time | Labels in the file |
|---|---|---|---|---|
| run-20261122T025025-1c17ed | 2026-11-22T02:55:19+00:00 | 80 | 5.6 minutes | yes, used only to mark this report |

System: commit 0a1fd5b; writer openai/gpt-oss-20b (backup openai/gpt-oss-120b) via Groq direct (free tier); checker qwen/qwen3.8-27b; classifier logistic regression on all-MiniLM-L6-v2 embeddings, C=10 (D-018); threshold 0.85; prompts PR-01 v1.7, PR-02 v1.0; reply cache off (fresh run); switches: trim on, writer reads 3 articles, narrowed safety rules on, type-aware search on, question rules on, learned decisions on, plan rule on.

## Results against the targets

Every measure, baseline and target in the Evaluation Framework (the same targets as the Project Brief), in its three tiers. "Not measured" means a run cannot produce that figure; the sections after the tables say why each target was missed or not measured.

### Business outcomes

| Measure | Baseline | Target | This run | Met? |
|---|---|---|---|---|
| First contact resolution | 42% | 60% or better | 66.2% (53 of 80) | Yes |
| Mean time to first reply | 8 to 12 hours | Under 5 minutes | mean 3.0 s, median 3.9 s | Yes |
| Customer satisfaction (satisfaction proxy) | 3.2 / 5 | 4.0 or better | measured by two people reviewing replies, not by a run | Not measured |
| Escalation rate | 58% | 30% or lower | 33.8% (27 of 80) | **No** |
| Repeat contacts | Not measured (21.2% in the history fields) | Halved | 1 within 7 days of an automatic reply in this run, all sent to a person | Not measured |

### Technical performance

| Measure | Baseline | Target | This run | Met? |
|---|---|---|---|---|
| Classification precision | - | 85% or better, per class | 100.0% for every type | Yes |
| Hallucination rate | - | 5% or lower | measured by two people reviewing replies, not by a run | Not measured |
| Citation accuracy | - | 95% or better | 97.6% (41 of 42) | Yes |
| Latency, 95th percentile | - | Under 3 seconds | 5.2 s without rate-limit waits (5.2 s with them) | **No** |
| Availability | - | 99.5% or better | every ticket got a decision (80 of 80); 0 sent to a person because the model provider was unavailable | Not measured |

### Governance conditions

| Measure | Baseline | Target | This run | Met? |
|---|---|---|---|---|
| Private data in outbound text | - | Zero occurrences | 0 sent (0 detected and blocked) | Yes |
| Quality across customer groups | - | Under five percentage points of variation | plan 36.7 points, region 13.2 points, language fluency 17.9 points, channel 10.2 points | **No** |
| Decision logging | - | Complete coverage: logged decisions match processed tickets | 80 final outcomes logged for 80 tickets | Yes |
| Confidence calibration | - | Stated confidence within five points of observed accuracy | 0.0 points apart | Yes |
| What the system must never do: must-not tickets answered automatically | - | 0 | 0 of 14 | Yes |

## Why targets were missed

**Escalation rate.** 27 of 80 tickets (33.8%) went to a person; the table "Why tickets went to a person" below gives every reason. The fixed safety rules alone sent 20 (25.0%): must-not tickets and data location questions, which no confidence score can override. The labels themselves miss the target: followed exactly, they send 32 of 80 tickets (40.0%) to a person. Meeting it would mean answering tickets that must reach a person. Marcus said he "would rather it said nothing than said something wrong", so the safety rules stay and the miss is reported.

**Latency, 95th percentile.** Without the provider's rate-limit waits, the median reply took 3.9 s and the slowest 5% took 5.2 s. An answered ticket needs two model calls, the writer and the grounding check (1.30 calls per ticket in this run, retries included). The free tier made 0 of 80 tickets wait, 0 s in total; the latency requirement (NFR-01, non-functional requirement 1) reports latency with and without those waits, as the course team asked.

**Quality across customer groups.** The difference is in the share answered automatically, best group minus lowest. By plan: Business 86.7%, Standard 50.0% (36.7 points). A rule sent 45.2% of Standard tickets to a person, against 10.0% for Business. The labels followed exactly are 20.0 points apart. By region: Asia Pacific 76.2%, North America 63.0% (13.2 points). A rule sent 29.6% of North America tickets to a person, against 19.0% for Asia Pacific. The labels followed exactly are 19.5 points apart. By language fluency: fluent English 70.5%, non-fluent English 52.6% (17.9 points). A rule sent 42.1% of non-fluent English tickets to a person, against 26.2% for fluent English. The labels followed exactly are 23.5 points apart. By channel: chat 72.7%, documentation comments 62.5% (10.2 points). A rule sent 31.2% of documentation comments tickets to a person, against 22.7% for chat. The labels followed exactly are 17.7 points apart. The groups ask different mixes of questions, and some ask more of the questions that must go to a person; every group's replies go through the same checks. The groups compared have 11 to 61 tickets, so one ticket moves a group by up to 9.1 points.

## Why some measures are not measured

- **Customer satisfaction and hallucination rate:** there are no live customers, so the Evaluation Framework has people review a sample of at least fifty replies against a rubric, two assessors independently. That review is in the report, not in a run.
- **Repeat contacts:** "the same customer raising the same issue again within a week" needs customers writing back after launch. In a run, a repeat contact after an automatic reply is sent to a person (the follow-up rule, FR-14, functional requirement 14).
- **Availability:** 99.5% or better is a share of time, which needs the live service over weeks. In a run, every ticket gets a decision, and while the model provider fails, tickets go to a person (the circuit breaker, FR-11, functional requirement 11).

## Volume

| | Tickets | Share |
|---|---|---|
| Tickets processed | 80 | 100% |
| Answered automatically | 53 | 66.2% |
| Escalated | 24 | 30.0% |
| Blocked by guardrails, then escalated | 3 | 3.8% |

## Business

| Measure | Result |
|---|---|
| First contact resolution | 66.2% |
| Escalation rate (escalated and blocked) | 33.8% |
| Mean response time | 3.0 s |
| Median response time | 3.9 s |

First contact resolution counts only tickets closed with no person involved; "Draft ready: check and send" handovers count as escalations.

### Why tickets went to a person

| Reason | Tickets | Share of all tickets | Why it goes to a person |
|---|---|---|---|
| Must-not ticket (security, compliance, feature request, unclear) | 14 | 17.5% | The labels and the Governance Framework say these must never get an automatic reply |
| Data location | 6 | 7.5% | Daniel: getting it wrong "is a compliance problem" |
| Grounding check: the article does not fit | 3 | 3.8% | The reply would not match the customer's situation |
| Mohnish Grover's four question groups | 2 | 2.5% | Decided in the walkthrough that these need a person |
| Repeat contact within 7 days | 1 | 1.2% | The earlier automatic reply did not solve it |
| Plan rule | 1 | 1.2% | The only article that answers is for other plans, so a person checks the draft |

**Repeat contacts:** 1 of 80 tickets was the same customer asking about the same type within 7 days of an automatic reply in this run; 1 of them went to a person with the earlier reply attached. Baseline (the history fields, when people handled these tickets): 17 of 80 (21.2%).

## Technical

| Latency | Median | 95th percentile |
|---|---|---|
| Without rate-limit waits | 3.9 s | 5.2 s |
| With rate-limit waits | 3.9 s | 5.2 s |

- **Time spent waiting for the rate limit:** 0 s on 0 of 80 tickets
- **Model calls:** 104 in total (retries included), 1.30 per ticket
- **Reply cache (off for validation and test runs):** 0 of 59 replies and 0 of 57 checks reused, with no model call
- **Tokens:** writer 67,321 in + 7,616 out (1,414 per reply written); checker 35,299 in + 2,862 out; total 113,098 (1,414 per ticket)
- **Retrieval hit rate (the right article in the top 5 found):** 52 of 53 (98.1%)
- **Citation accuracy:** 41 of 42 (97.6%)

### Classification precision and recall per class

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

Confusion matrix (rows = type in the labels, columns = type the system chose, in sorted type order):

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

## Governance

- **Decisions logged:** 356 rows; 80 final outcomes for 80 tickets -> reconciles
- **Guardrail activations:** grounding_model 3
- **Private data detections:** 0 (every one blocked, none sent)
- **Labels for a person:** Needs a specialist 26, Draft ready: check and send 1

### Results by customer group

Share answered automatically for each group; the condition is under five percentage points of variation between the groups of each kind. Groups under 10 tickets are shown but not compared. Right article = of the automatic replies the labels name an article for, the share that cite one of those articles.

| Kind | Group | Tickets | Answered automatically | Right article | Must-not answered |
|---|---|---|---|---|---|
| plan | Business | 30 | 86.7% | 20 of 20 (100.0%) | 0 |
| plan | Enterprise | 8 (not compared) | 75.0% | 6 of 6 (100.0%) | 0 |
| plan | Standard | 42 | 50.0% | 15 of 16 (93.8%) | 0 |
| **plan** | **difference** | | **36.7 points** | | |
| region | Asia Pacific | 21 | 76.2% | 14 of 14 (100.0%) | 0 |
| region | Europe | 25 | 72.0% | 13 of 14 (92.9%) | 0 |
| region | Latin America | 7 (not compared) | 28.6% | 2 of 2 (100.0%) | 0 |
| region | North America | 27 | 63.0% | 12 of 12 (100.0%) | 0 |
| **region** | **difference** | | **13.2 points** | | |
| language fluency | fluent English | 61 | 70.5% | 35 of 36 (97.2%) | 0 |
| language fluency | non-fluent English | 19 | 52.6% | 6 of 6 (100.0%) | 0 |
| **language fluency** | **difference** | | **17.9 points** | | |
| channel | chat | 22 | 72.7% | 11 of 12 (91.7%) | 0 |
| channel | documentation comments | 16 | 62.5% | 7 of 7 (100.0%) | 0 |
| channel | email | 31 | 64.5% | 16 of 16 (100.0%) | 0 |
| channel | forum | 11 | 63.6% | 7 of 7 (100.0%) | 0 |
| **channel** | **difference** | | **10.2 points** | | |

### Calibration: stated confidence against observed accuracy

| Band | Tickets | Stated confidence | Observed accuracy | Gap |
|---|---|---|---|---|
| 0.8-1.0 | 80 | 100.0% | 100.0% | 0.0 points |

### The labels followed exactly, compared with the system

| Measure | Result |
|---|---|
| Must-not tickets answered automatically (0) | 0 of 14 |
| Tickets the labels would answer that the system answered | 41 of 48 (85.4%) |
| Tickets the labels send to a person that the system answered | 12 |
| Sent to a person by the labels followed exactly | 32 of 80 (40.0%) |
| Ticket type right | 100.0% |

The labels are someone's decisions, not the truth: they can be wrong too.

Run time: 5.6 minutes.
