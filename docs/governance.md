# Governance

The six sections of the Governance Framework ("What must be true before this could speak to a real customer"), filled
in with **facts about the system as built**, with evidence. The judgements (how likely, how bad, who is accountable, the
declaration) were decided by Mohnish Grover on 20 Nov 2026.
Drafted 17 Nov 2026 with Claude (Anthropic), completed 20 Nov 2026. The fairness audit (section 3) uses the final run of
the 500 development tickets on Groq's free tier (19-20 Nov 2026); some evidence in the other sections comes from earlier
development runs, named where it is used.

---

## 1. Decision logging

Every step of every ticket is written to `storage/decisions.db` (`src/logging_store.py`, `src/run_evaluation.py`).

| The framework's minimum record | Our log | |
|---|---|---|
| decision_id, timestamp, ticket_id, stage | `decision_id`, `created_at`, `ticket_id`, `stage` (classification, routing, generation, validation, outcome) | ✅ |
| input_summary | `input_summary` (channel, length, plan, region, fluency; no personal details) | ✅ |
| model name and version | `model`, `provider` | ✅ |
| prediction and confidence | `prediction`, `confidence` | ✅ |
| alternatives | `alternatives` (the runner-up types with their confidence) | ✅ |
| sources_used with scores | `sources_used` (article, rank, score, the passage) | ✅ |
| threshold_applied | `threshold` | ✅ |
| action_taken | `action_taken` (auto_respond, escalate, block) | ✅ |
| reason, human readable | `reason` (e.g. "Sent to a person (Draft ready: check and send) because article DOC-AUTH-003 applies to Business and Enterprise plans and this customer is on standard plan (plan rule).") | ✅ |
| guardrail_results | `guardrails` (each of the six: pass or fail, with detail) | ✅ |
| prompt_version | `prompt_version` (e.g. PR-01 v1.7, PR-02 v1.0) | ✅ |
| requirement_ids | `requirement_ids` (e.g. FR-03, FR-07) | ✅ |
| Added | `run_id`, `label`, `latency_ms` | |

**Coverage check:** every metrics report counts the logged outcomes against the tickets processed, e.g.
"Decisions logged: 354 rows; 80 final outcomes for 80 tickets -> reconciles (A8)".

---

## 2. Risk register

Likelihood, impact and owner decided by Mohnish Grover, 20 Nov 2026 (suggested by Claude (Anthropic) from the run results). Mohnish Grover, who built the system, owns the risks controlled by the code until handover; CloudServe people own the rest. The mitigation column lists only controls that exist in the code.

| ID | Risk | Likelihood | Impact | Mitigation in our design (with evidence) | Owner |
|---|---|---|---|---|---|
| R-01 | The system answers confidently and incorrectly | Low | High | Answers only at 85% classifier confidence or more (D-019); replies are copied word for word from the articles, never written by the AI (PR-01 v1.7); two grounding checks, the second by a model from another family (D-020); the follow-up rule sends a repeat question to a person; every reply says it is automatic and invites a reply. Evidence: 0 forbidden claims in sent replies (`scripts/reference_check.py`); citation accuracy 93.4% (development), 97.7% (validation look) | Mohnish Grover (until handover) |
| R-02 | Private data appears in an outbound response | Low | High | The private_data guardrail blocks any reply with names, addresses, keys or account numbers (never redacts and sends); replies are article text, which holds no customer data; the customer's name is never given to the AI. Evidence: 0 detections in every run | Mohnish Grover (until handover) |
| R-03 | A customer's input is treated as an instruction | Medium | High | The ticket sits between marks and is declared data (PR-01); the instruction_integrity guardrail blocks attempts and the agent gets no reply text; red-team tickets kept as tests (`data/red_team/`, `scripts/red_team.py`, D-021) | Mohnish Grover (until handover) |
| R-04 | Some customer groups receive worse answers | Medium | Medium | The system never reads plan, region or fluency to decide (except the plan rule, by the article's own "Applies to" line); type-aware search for non-fluent English; fairness measured every run, and inside each question (section 3). Known limitation: a misleading subject affects non-fluent replies more (`docs/known_limitations.md`, 1) | Marcus Adeyemi, Head of Customer Support |
| R-05 | The documentation the system relies on goes stale | Medium | Medium | Replies copy the current article text at the moment of answering; the article index is rebuilt from `documentation.json` by one command (`scripts/setup_vector_store.py`); every article in the data was reviewed 0 days ago. Not built: an age check on articles | Ines Varga, Technical Writer |
| R-06 | The model provider becomes unavailable | High on the free tier | Low (tickets go to a person) | Retries with backoff, then a backup model (gpt-oss-120b); after 3 tickets in a row with the provider down, the rest go straight to a person; a reply that cannot be checked is never sent (fail closed). Evidence: DEV-0062 went to a person when the reply was cut off (15 Nov) | Mohnish Grover (until handover) |
| R-07 | Latency degrades under load | High on the free tier | Medium | Tickets for a person need no AI call (median 0.3 s); the dashboard shows the 95th percentile against the 3-second target. Known limitation: 95th percentile above 3 s, especially on the free tier (`docs/known_limitations.md`, 6) | Mohnish Grover (until handover) |
| R-08 | Costs rise unexpectedly with volume | Low | Low | About one AI call per ticket (1.02 per ticket on the paid test run of 17 Nov; 2.56 on the free tier, counting the retries its limit caused); tokens counted in every metrics report; the reply cache for development runs (D-025); free tier only for the final runs | Marcus Adeyemi, Head of Customer Support |
| R-09 | A misleading subject line pulls in the wrong article | Medium | Medium | The final grounding check blocks a reply whose article does not fit (DEV-0170, VAL-0023, VAL-0029). Two fixes tested and rejected (`docs/known_limitations.md`, 1) | Mohnish Grover (until handover) |
| R-10 | A new kind of question that needs a person is answered automatically | Medium | High | The fixed safety rules and person-only types still apply; the follow-up rule catches a reply that did not help. Known limitation: the learned decisions cannot recognise a question never seen (`docs/known_limitations.md`, 4) | Daniel Okonkwo, Tier Two Support Engineer |

---

## 3. Fairness audit

These figures come from the final run of the 500 development tickets on Groq's free tier, 19-20 Nov 2026
(`evaluation/results/dev500_final_groq_19nov.json`, commit 0364036). "Answered" is the share of tickets the system
answered by itself. "Right article" is the share of those answers that used the article the labels expect (the
metrics report's quality score). "Behind the best" is how many points each group is behind the best group of its kind
(answered / right article). Groups under 10 tickets are not compared. The explanations were drafted by Claude
(Anthropic) from the run results and approved by Mohnish Grover (20 Nov 2026).

| Group | Tickets | Answered | Right article | Behind the best | Why |
|---|---|---|---|---|---|
| Enterprise customers | 83 | 67.5% | 95.9% (47 of 49) | best / best | |
| Business customers | 164 | 67.1% | 90.4% (85 of 94) | 0.4 / 5.5 | 9 of the 19 answers that used a different article from the labels are in this group |
| Standard customers | 253 | 64.8% | 93.8% (120 of 128) | 2.7 / 2.1 | The plan rule sends 16 Standard tickets to a person, because the article is only for Business and Enterprise plans |
| Asia Pacific customers | 119 | 64.7% | 94.9% (56 of 59) | 4.2 / best | |
| Europe customers | 151 | 68.9% | 91.2% (83 of 91) | best / 3.7 | |
| Latin America customers | 60 | 61.7% | 93.1% (27 of 29) | 7.2 / 1.8 | More data location questions, which always go to a person (7 of 60); the plan rule (3); 2 lost to the free tier's limit; 2 where the check said the article did not fit |
| North America customers | 170 | 65.9% | 93.5% (86 of 92) | 3.0 / 1.4 | |
| Tickets in fluent English | 380 | 67.9% | 93.7% (194 of 207) | best / best | |
| Tickets in non-fluent English | 120 | 60.0% | 90.6% (58 of 64) | 7.9 / 3.1 | 5 lost to the free tier's limit; more data location questions (9 of 120); the plan rule (5); search finds the right article a little less often (95% against 99%) |
| Chat | 155 | 63.9% | 94.1% | 5.3 / best | More data location questions (12 of 155); the plan rule (8) |
| Documentation comments | 78 | 69.2% | 91.7% | best / 2.4 | |
| Email | 212 | 66.0% | 92.5% | 3.2 / 1.6 | |
| Forum | 55 | 67.3% | 93.3% | 1.9 / 0.8 | |
| Short tickets (28 words or fewer) | 273 | 66.3% | 93.4% | best / best | |
| Long tickets (over 28 words) | 227 | 65.6% | 92.5% | 0.7 / 0.9 | |

**Why some groups are behind**

Region (7.2 points), language fluency (7.9) and channel (5.3) are more than 5 points apart. There are four reasons:

1. **Data location questions always go to a person** (Daniel's rule). Latin America, non-fluent and chat customers ask
   these questions more often, so they get fewer automatic answers.
2. **The plan rule.** When the article is only for Business and Enterprise plans, a Standard customer's reply goes to a
   person with a draft. This is why Standard is behind the other plans, but plans are still less than 5 points apart
   (2.7). It also adds a little to the region, language and chat gaps.
3. **The free tier's limit.** 8 times, the free tier refused the safety check on a reply, so the reply was not sent
   and the ticket went to a person. 5 of those 8 were non-fluent tickets. On the paid test run, which had no limit, the
   gaps were 4.5 (region) and 5.0 (language).
4. **Search is a little weaker on non-fluent English** (the right article was found for 95.4% of non-fluent tickets
   against 99.3% of fluent ones), as the Governance Framework warns.

When the same question is asked, every group gets the same decision almost every time (53 of 67 questions with no
difference at all), so the gaps come mostly from which questions each group asks. The groups are also small: in Latin
America, 4 tickets change the result by about 7 points. Nothing in the system was changed because of these results.

Validation (80 tickets, final free-tier run of 19 Nov): 36.7 points apart by plan, 13.2 by region and 17.9 by language.
With 30-40 tickets per group, one ticket moves a group by 2-4 points.

---

## 4. Guardrails (as built, on every reply, `src/guardrails.py`)

| Guardrail | What it checks | What happens when it fires |
|---|---|---|
| private_data | Names, addresses, keys, account numbers, anything identifying a customer | Block and escalate; the agent gets no reply text (never redacted and sent) |
| grounding_words | Every sentence's words and numbers appear in its article | Block and escalate; or the sentence is removed and the whole reply checked again |
| grounding_model | A second model (Qwen, another family) checks the article fits the situation and each sentence is supported | Block and escalate, with the unsupported part flagged |
| instruction_integrity | The ticket has not tried to instruct the system; the reply holds none of our instructions | Block, escalate; the input is in the decision log for review; the agent gets no reply text |
| tone_and_scope | No commitments about refunds, credits or dates; within support; within the length limit | Block |
| confidence_floor | The classifier was confident enough and the writer was sure; a missing confidence counts as low | Escalate |

All fail closed: if a check itself errors, the reply is blocked.

---

## 5. Incident response

Who does each step and how long it should take: decided by Mohnish Grover, 20 Nov 2026. What the system offers at each step:

| Step | What to do (with what the system provides) | Who does it | How long |
|---|---|---|---|
| 1. Detect | Watch the Grafana dashboard: a jump in one guardrail, a fall in the share answered automatically, the 95th percentile over 3 s, or confidence scores shifting lower (drift). A customer's complaint about a reply | Any support agent (Tier One, for example Sofia Restrepo), from the dashboard or a complaint | As soon as it is seen |
| 2. Contain | Turn on the kill switch (below): every new ticket goes to a person | Whoever detects it, if authorised to use the kill switch (below) | Within 15 minutes |
| 3. Assess | Find the affected tickets in the decision log (`storage/decisions.db`) by run, stage, guardrail or reason; each row has the prompt version and the articles used | Mohnish Grover with Daniel Okonkwo | Same day |
| 4. Notify | Tell the support lead and, if customers received a wrong reply, contact them | Marcus Adeyemi | Within one working day |
| 5. Remediate | Fix the cause (a rule, an article, the prompt version via `PR01_FILE`), run the tests and a development run, then turn the kill switch off | Mohnish Grover (with Ines Varga if an article is wrong) | Before the kill switch is turned off |
| 6. Review | Add the failing ticket to the tests (as with the red-team tickets) and record the decision in `docs/decision_log.md` | Mohnish Grover | Within a week |

### The kill switch

| Question | Answer |
|---|---|
| What is the mechanism? | An empty file called `storage/kill_switch` (or the setting `KILL_SWITCH=on`). While it exists, every ticket goes to a person with the reason "the kill switch is on, so all automatic replies are stopped". No deployment or restart is needed |
| Who is authorised to use it? | Any support agent (Tier One or Tier Two, for example Sofia Restrepo or Daniel Okonkwo), Marcus Adeyemi (Head of Customer Support), or Mohnish Grover. Any one of them alone, with no approval needed: the switch only sends tickets to a person, so it cannot do harm. (Approved by Mohnish Grover, 20 Nov 2026.) |
| How long until it takes effect? | From the next ticket: the switch is checked for every ticket at the routing step, in the unattended run and in the API. `GET /health` shows whether it is on |
| What happens to tickets in flight? | A ticket already past the routing step finishes as decided; every ticket after it goes to a person. No ticket is dropped |
| How is it tested? | Automatic tests in `tests/test_route.py`; by hand: create the file, send DEMO-1 through the API, see it go to a person, delete the file |

---

## 6. The declaration

Completed 20 Nov 2026. Wording drafted by Claude (Anthropic) from the project records; approved by Mohnish Grover.

| Statement | Our position |
|---|---|
| This system must never ... | send a customer a reply that is not copied from Ines's articles and checked, send private data, or answer a ticket that must go to a person (security, compliance, data location, leaked keys). |
| The mechanism that enforces that is ... | code, not the model: the safety rules run before any model is used; the model only chooses which article parts answer, and the code copies them word for word; five guardrails check every reply and block it if any check fails or cannot run; and a kill switch stops all automatic replies at once. |
| The most likely way it could still cause harm is ... | a reply copied correctly from an article that looks right but does not fit the customer's situation, for example when a misleading subject line pulls in a different article, or when one of my question groups is asked in words the system has not seen. |
| We would not deploy this without first ... | running it on a model plan without the free tier's limit, checking the customer groups again on real tickets until they are less than 5 points apart, and agreeing with Daniel which data location questions can be answered from Ines's articles. (Drafted by Claude (Anthropic); approved by Mohnish Grover, 20 Nov 2026.) |
