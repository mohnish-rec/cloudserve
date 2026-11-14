# Fairness: a balanced sample and a like-for-like check

Run: dev500_message_only_SANDBOX_PAID.json. Development tickets only. Sample seed 42; sample fits the target sizes exactly: yes.

## 1. Gaps: all 500 tickets and the balanced sample of 120

| Group | Value | All 500: answered | Sample 120: answered |
|---|---|---|---|
| plan | business | 114 of 164 (69.5%) | 30 of 40 (75.0%) |
| plan | enterprise | 57 of 83 (68.7%) | 23 of 40 (57.5%) |
| plan | standard | 186 of 253 (73.5%) | 29 of 40 (72.5%) |
| region | asia_pacific | 82 of 119 (68.9%) | 19 of 30 (63.3%) |
| region | europe | 113 of 151 (74.8%) | 20 of 30 (66.7%) |
| region | latin_america | 44 of 60 (73.3%) | 23 of 30 (76.7%) |
| region | north_america | 118 of 170 (69.4%) | 20 of 30 (66.7%) |
| fluency | fluent | 275 of 380 (72.4%) | 40 of 60 (66.7%) |
| fluency | non_fluent | 82 of 120 (68.3%) | 42 of 60 (70.0%) |

| Gap (points, target under 5) | All 500 | Sample 120 | Same question mix (inside each question, 3b) |
|---|---|---|---|
| plan | 4.8 | 17.5 | 0.1 |
| region | 5.9 | 13.3 | 1.0 |
| fluency | 4.0 | 3.3 | 0.7 |

## 2. Own percentage first: of each group's tickets that should be answered, the share answered

| Group | Value | Should be answered (his decisions) | Answered | Own % | Should be answered (answer key) | Answered | Own % |
|---|---|---|---|---|---|---|---|
| plan | business | 115 | 114 | 99.1% | 106 | 93 | 87.7% |
| plan | enterprise | 57 | 57 | 100.0% | 51 | 45 | 88.2% |
| plan | standard | 187 | 186 | 99.5% | 154 | 139 | 90.3% |
| region | asia_pacific | 84 | 82 | 97.6% | 64 | 59 | 92.2% |
| region | europe | 113 | 113 | 100.0% | 103 | 94 | 91.3% |
| region | latin_america | 44 | 44 | 100.0% | 39 | 33 | 84.6% |
| region | north_america | 118 | 118 | 100.0% | 105 | 91 | 86.7% |
| fluency | fluent | 277 | 275 | 99.3% | 231 | 208 | 90.0% |
| fluency | non_fluent | 82 | 82 | 100.0% | 80 | 69 | 86.2% |

| Gap (points, target under 5; groups of 10 or more) | By his decisions | By the answer key |
|---|---|---|
| plan | 0.9 | 2.5 |
| region | 2.4 | 7.6 |
| fluency | 0.7 | 3.8 |

## 3a. Inside each ticket type: types where groups got different rates

| Group | Type | Answered per group | Gap |
|---|---|---|---|
| plan | authentication_failure | business 3/5; enterprise 2/5; standard 6/10 | 20 |
| plan | billing_query | business 6/7; enterprise 3/3; standard 14/14 | 14 |
| plan | database_issue | business 5/8; enterprise 3/6; standard 9/12 | 25 |
| plan | onboarding | business 8/8; enterprise 2/2; standard 11/12 | 8 |
| plan | quota_or_overage | business 6/8; enterprise 0/2; standard 10/13 | 77 |
| plan | (every other type) | same rate for every group | 0 (17 types) |
| region | authentication_failure | asia_pacific 1/2; europe 7/11; latin_america 0/1; north_america 3/6 | 64 |
| region | billing_query | asia_pacific 7/8; europe 10/10; latin_america 0/0; north_america 6/6 | 12 |
| region | database_issue | asia_pacific 5/9; europe 5/7; latin_america 2/3; north_america 5/7 | 16 |
| region | onboarding | asia_pacific 5/6; europe 5/5; latin_america 3/3; north_america 8/8 | 17 |
| region | quota_or_overage | asia_pacific 4/4; europe 9/11; latin_america 3/3; north_america 0/5 | 100 |
| region | (every other type) | same rate for every group | 0 (17 types) |
| fluency | authentication_failure | fluent 11/17; non_fluent 0/3 | 65 |
| fluency | billing_query | fluent 17/18; non_fluent 6/6 | 6 |
| fluency | database_issue | fluent 14/18; non_fluent 3/8 | 40 |
| fluency | onboarding | fluent 11/12; non_fluent 10/10 | 8 |
| fluency | quota_or_overage | fluent 12/19; non_fluent 4/4 | 37 |
| fluency | (every other type) | same rate for every group | 0 (17 types) |

A type holds several questions, and he decided some of them differently, so a gap inside a type is which question each customer asked. His questions are the right category (3b).

## 3b. Inside each of his questions: questions where groups got different decisions

Every question below had at least one ticket answered and at least one sent to a person.

| Question | Tickets | Answered | Not answered (ticket: plan, region, fluency: why) |
|---|---|---|---|
| Q14 Invoice charges for a service we do not use | 11 | 10 | DEV-0073: business, asia_pacific, fluent: Sent to a person (Needs a specialist) because a safety rule says a person must handle it ( |
| Q34 New account, where do I start? | 9 | 8 | DEV-0170: standard, asia_pacific, fluent: Reply blocked by a guardrail and sent to a person (Needs a specialist): grounding_model: t |

Questions where every ticket got the same decision, whatever the group: **65 of 67**.

Must-not tickets answered in the sample: 0.

Sample: DEV-0002, DEV-0004, DEV-0009, DEV-0018, DEV-0029, DEV-0033, DEV-0034, DEV-0041, DEV-0043, DEV-0045, DEV-0048, DEV-0053, DEV-0058, DEV-0060, DEV-0068, DEV-0079, DEV-0082, DEV-0084, DEV-0089, DEV-0094, DEV-0096, DEV-0101, DEV-0105, DEV-0110, DEV-0112, DEV-0113, DEV-0115, DEV-0116, DEV-0120, DEV-0132, DEV-0136, DEV-0144, DEV-0154, DEV-0156, DEV-0161, DEV-0162, DEV-0165, DEV-0169, DEV-0174, DEV-0175, DEV-0178, DEV-0181, DEV-0185, DEV-0190, DEV-0195, DEV-0206, DEV-0209, DEV-0211, DEV-0212, DEV-0215, DEV-0228, DEV-0229, DEV-0232, DEV-0238, DEV-0240, DEV-0245, DEV-0250, DEV-0252, DEV-0257, DEV-0267, DEV-0269, DEV-0273, DEV-0275, DEV-0276, DEV-0281, DEV-0282, DEV-0284, DEV-0286, DEV-0289, DEV-0298, DEV-0299, DEV-0300, DEV-0303, DEV-0305, DEV-0316, DEV-0317, DEV-0335, DEV-0337, DEV-0338, DEV-0342, DEV-0344, DEV-0351, DEV-0357, DEV-0358, DEV-0359, DEV-0362, DEV-0370, DEV-0376, DEV-0380, DEV-0386, DEV-0394, DEV-0396, DEV-0397, DEV-0398, DEV-0406, DEV-0408, DEV-0419, DEV-0420, DEV-0421, DEV-0424, DEV-0431, DEV-0432, DEV-0433, DEV-0434, DEV-0443, DEV-0444, DEV-0446, DEV-0452, DEV-0456, DEV-0458, DEV-0459, DEV-0466, DEV-0467, DEV-0469, DEV-0475, DEV-0479, DEV-0485, DEV-0492, DEV-0494, DEV-0500
