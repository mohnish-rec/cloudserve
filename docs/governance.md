# Governance (draft for Mohnish Grover to complete)

The six sections of the Governance Framework ("What must be true before this could speak to a real customer"), filled
in with **facts about the system as built**, with evidence. Cells marked **[Mohnish to decide]** are judgements (how
likely, how bad, who is accountable, the declaration) and are left for Mohnish Grover's own words.
Drafted 17 Nov 2026 with Claude (Anthropic). Numbers are from the 500 development tickets (latest run:
`sandbox_dev500_cached`, 15 Nov 2026, paid route in the sandbox); the final validation run (Groq free tier) is added
when it has run.

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

Likelihood, impact and owner: **[Mohnish to decide]**. The mitigation column lists only controls that exist in the code.

| ID | Risk | Likelihood | Impact | Mitigation in our design (with evidence) | Owner |
|---|---|---|---|---|---|
| R-01 | The system answers confidently and incorrectly | | | Answers only at 85% classifier confidence or more (D-019); replies are copied word for word from the articles, never written by the AI (PR-01 v1.7); two grounding checks, the second by a model from another family (D-020); the follow-up rule sends a repeat question to a person; every reply says it is automatic and invites a reply. Evidence: 0 forbidden claims in sent replies (`scripts/reference_check.py`); citation accuracy 93.4% (development), 97.7% (validation look) | |
| R-02 | Private data appears in an outbound response | | | The private_data guardrail blocks any reply with names, addresses, keys or account numbers (never redacts and sends); replies are article text, which holds no customer data; the customer's name is never given to the AI. Evidence: 0 detections in every run | |
| R-03 | A customer's input is treated as an instruction | | | The ticket sits between marks and is declared data (PR-01); the instruction_integrity guardrail blocks attempts and the agent gets no reply text; red-team tickets kept as tests (`data/red_team/`, `scripts/red_team.py`, D-021) | |
| R-04 | Some customer groups receive worse answers | | | The system never reads plan, region or fluency to decide (except the plan rule, by the article's own "Applies to" line); type-aware search for non-fluent English; fairness measured every run, and inside each question (section 3). Known limitation: a misleading subject affects non-fluent replies more (`docs/known_limitations.md`, 1) | |
| R-05 | The documentation the system relies on goes stale | | | Replies copy the current article text at the moment of answering; the article index is rebuilt from `documentation.json` by one command (`scripts/setup_vector_store.py`); every article in the data was reviewed 0 days ago. Not built: an age check on articles | |
| R-06 | The model provider becomes unavailable | | | Retries with backoff, then a backup model (gpt-oss-120b); after 3 tickets in a row with the provider down, the rest go straight to a person; a reply that cannot be checked is never sent (fail closed). Evidence: DEV-0062 went to a person when the reply was cut off (15 Nov) | |
| R-07 | Latency degrades under load | | | Tickets for a person need no AI call (median 0.3 s); the dashboard shows the 95th percentile against the 3-second target. Known limitation: 95th percentile above 3 s, especially on the free tier (`docs/known_limitations.md`, 6) | |
| R-08 | Costs rise unexpectedly with volume | | | About one AI call per ticket (0.97 per ticket, development); tokens counted in every metrics report; the reply cache for development runs (D-025); free tier only for the final runs | |
| R-09 | A misleading subject line pulls in the wrong article | | | The final grounding check blocks a reply whose article does not fit (DEV-0170, VAL-0023, VAL-0029). Two fixes tested and rejected (`docs/known_limitations.md`, 1) | |
| R-10 | A new kind of question that needs a person is answered automatically | | | The fixed safety rules and person-only types still apply; the follow-up rule catches a reply that did not help. Known limitation: the learned decisions cannot recognise a question never seen (`docs/known_limitations.md`, 4) | |

---

## 3. Fairness audit

Resolution rate = answered automatically. Quality score = share of automatic replies that cite an expected article and
passed every guardrail (the metrics report's definition). Variation from best = points behind the best segment in the
same group (resolution / quality). The pack's tiers are enterprise, business and standard, so "small business" is shown
as both business and standard.

| Segment | Tickets | Resolution rate | Quality score | Variation from best | Explanation |
|---|---|---|---|---|---|
| Enterprise customers | 83 | 68.7% | 82.5% | -0.8 / best | [Mohnish to write; evidence below] |
| Business customers | 164 | 69.5% | 77.2% | best / -5.3 | |
| Standard customers | 253 | 67.2% | 73.5% | -2.3 / -9.0 | |
| Tickets in fluent English | 380 | 69.5% | 75.8% | best / -2.1 | |
| Tickets in non-fluent English | 120 | 64.2% | 77.9% | -5.3 / best | |
| Short tickets (28 words or fewer) | 273 | 68.9% | 78.2% | best / best | |
| Long tickets (over 28 words) | 227 | 67.4% | 73.9% | -1.5 / -4.3 | |

Evidence for the explanations (`evaluation/results/fairness_balanced.md`, `docs/known_limitations.md`):
- Inside each of the 67 questions, every ticket got the same decision whatever the group in 65; with the same mix of
  questions the gaps are 0.1 (plan), 1.0 (region), 0.7 (fluency) points, so the raw gaps come from which questions each
  group asked.
- Standard is lower since 15 Nov because of the plan rule: 16 Standard tickets used articles that apply to Business and
  Enterprise only and now go to a person with a draft.
- Non-fluent: a misleading subject outweighs a short message more often (limitation 1), the variation the framework
  says to expect.
- Validation (80 tickets) swings much more: 30-40 tickets per group, so one ticket moves a group by 2-4 points.

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

Who does each step and how long it should take: **[Mohnish to decide]**. What the system offers at each step:

| Step | What to do (with what the system provides) | Who does it | How long |
|---|---|---|---|
| 1. Detect | Watch the Grafana dashboard: a jump in one guardrail, a fall in the share answered automatically, the 95th percentile over 3 s, or confidence scores shifting lower (drift). A customer's complaint about a reply | | |
| 2. Contain | Turn on the kill switch (below): every new ticket goes to a person | | |
| 3. Assess | Find the affected tickets in the decision log (`storage/decisions.db`) by run, stage, guardrail or reason; each row has the prompt version and the articles used | | |
| 4. Notify | Tell the support lead and, if customers received a wrong reply, contact them | | |
| 5. Remediate | Fix the cause (a rule, an article, the prompt version via `PR01_FILE`), run the tests and a development run, then turn the kill switch off | | |
| 6. Review | Add the failing ticket to the tests (as with the red-team tickets) and record the decision in `docs/decision_log.md` | | |

### The kill switch

| Question | Answer |
|---|---|
| What is the mechanism? | An empty file called `storage/kill_switch` (or the setting `KILL_SWITCH=on`). While it exists, every ticket goes to a person with the reason "the kill switch is on, so all automatic replies are stopped". No deployment or restart is needed |
| Who is authorised to use it? | [Mohnish to decide] |
| How long until it takes effect? | From the next ticket: the switch is checked for every ticket at the routing step, in the unattended run and in the API. `GET /health` shows whether it is on |
| What happens to tickets in flight? | A ticket already past the routing step finishes as decided; every ticket after it goes to a person. No ticket is dropped |
| How is it tested? | Automatic tests in `tests/test_route.py`; by hand: create the file, send DEMO-1 through the API, see it go to a person, delete the file |

---

## 6. The declaration

To complete last, in Mohnish Grover's own words: **[Mohnish to decide]**

| Statement | Our position |
|---|---|
| This system must never ... | |
| The mechanism that enforces that is ... | |
| The most likely way it could still cause harm is ... | |
| We would not deploy this without first ... | |
