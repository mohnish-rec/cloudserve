# Metrics report: dev_word_blocked.json

- **Run:** run-20261109T093003-4c58a5 · 2026-11-09T11:51:16+00:00 · 50 tickets
- **System version:** commit 6390615 · prompts PR-01 v1.2, PR-02 v1.0 · writer openai/gpt-oss-20b (backup openai/gpt-oss-120b) · checker qwen/qwen3.8-27b · classifier logistic regression on all-MiniLM-L6-v2 embeddings, C=10 (D-018) · threshold 0.85
- **Answer key in the file:** yes, used only to mark this report

## Volume

| Processed | Answered automatically | Escalated | Blocked by guardrails |
|---|---|---|---|
| 50 | 42 (84.0%) | 0 (0.0%) | 8 (16.0%) |

## Business

| First contact resolution | Escalation rate | Mean response time | Median response time |
|---|---|---|---|
| 84.0% | 16.0% | 168.0 s | 115.3 s |

First contact resolution counts only tickets closed with no person involved; "Draft ready" hand-overs count as escalations (FR-07).

## Technical

- **Latency:** median 115.3 s, 95th percentile 385.7 s (target: under 3 s for 95%, NFR-01)
- **Model calls:** 216 in total (retries included), 4.32 per ticket
- **Tokens:** writer 64,992 in + 12,162 out (1,543 per reply written); checker 24,808 in + 2,127 out; total 104,089 (2,082 per ticket)
- **Decisions logged:** 250 rows; 50 final outcomes for 50 tickets -> reconciles (A8)
- **Guardrail activations:** grounding_words 8
- **Private data detections:** 0 (every one blocked, none sent)
- **Labels:** sent 42, Needs a specialist 8

## Marked against the answer key

- **Must-not tickets answered automatically:** 0 of 0 (target 0)
- **Answered automatically when the answer key says a person:** 9 of 42 automatic replies
- **Should-be-automatic tickets answered automatically:** 33 of 38 (86.8%)
- **Correct first contact resolution** (answered, and the answer key agrees): 66.0%
- **Retrieval hit rate** (an expected article in the top 5): 40 of 40 (100.0%)
- **Citation accuracy** (automatic replies citing an expected article): 29 of 35 (82.9%; target 95%)
- **Type accuracy:** 100.0%

### Classification precision and recall per type

```
                    precision    recall  f1-score   support

    account_access      1.000     1.000     1.000         1
api_usage_question      1.000     1.000     1.000        22
configuration_help      1.000     1.000     1.000         1
       data_export      1.000     1.000     1.000         5
    database_issue      1.000     1.000     1.000        12
  integration_help      1.000     1.000     1.000         1
        onboarding      1.000     1.000     1.000         8

          accuracy                          1.000        50
         macro avg      1.000     1.000     1.000        50
      weighted avg      1.000     1.000     1.000        50

```

Confusion matrix (rows = true type, columns = predicted, sorted type order):

```
[[ 1  0  0  0  0  0  0]
 [ 0 22  0  0  0  0  0]
 [ 0  0  1  0  0  0  0]
 [ 0  0  0  5  0  0  0]
 [ 0  0  0  0 12  0  0]
 [ 0  0  0  0  0  1  0]
 [ 0  0  0  0  0  0  8]]
```

### Calibration (Evaluation Framework)

| Band | Tickets | Stated confidence | Observed accuracy | Gap |
|---|---|---|---|---|
| 0.8-1.0 | 50 | 100.0% | 100.0% | -0.0 points |

### Results by customer group (NFR-06: under 5 points between groups)

Resolution rate = answered automatically. Quality score = share of automatic replies that cite an expected article and passed every guardrail. Groups under 10 tickets are shown but not compared.

| Group | Value | Tickets | Resolution rate | Quality score | Must-not answered |
|---|---|---|---|---|---|
| tier | business | 10 | 80.0% | 75.0% | 0 |
| tier | enterprise | 11 | 72.7% | 75.0% | 0 |
| tier | standard | 29 | 89.7% | 65.4% | 0 |
| region | asia_pacific | 11 | 72.7% | 37.5% | 0 |
| region | europe | 18 | 88.9% | 81.2% | 0 |
| region | latin_america | 6 | 100.0% | 83.3% | 0 |
| region | north_america | 15 | 80.0% | 66.7% | 0 |
| language_fluency | fluent | 37 | 86.5% | 75.0% | 0 |
| language_fluency | non_fluent | 13 | 76.9% | 50.0% | 0 |
| channel | chat | 16 | 68.8% | 45.5% | 0 |
| channel | docs_comment | 12 | 91.7% | 81.8% | 0 |
| channel | email | 19 | 89.5% | 76.5% | 0 |
| channel | forum | 3 | 100.0% | 66.7% | 0 |

Run time: 142.5 minutes.
