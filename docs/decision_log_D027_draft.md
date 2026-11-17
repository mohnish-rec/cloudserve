# Decision log D-027 onward: DRAFT for Mohnish Grover to check

Drafted 17 Nov 2026 with Claude (Anthropic). Every "Why" is Mohnish Grover's own words, quoted, with the date; facts
and evidence are from the files named. Nothing here is final until Mohnish has checked it; then it moves into
`docs/decision_log.md` and this file is deleted. Items marked **[open]** still need his decision.

## Corrections to earlier entries (the log must match what happened)

- **D-024 (no paid provider, even for development test runs) was later changed, the same day.** The paid code was
  removed from the real project on 9 Nov 2026, but a separate copy of the project (the sandbox, never pushed) was set
  up that afternoon to send replies through OpenRouter's paid service (sandbox commit "Sandbox: OpenRouter writer
  setting, prompt and model switches", 9 Nov 14:40). The first paid run was all 500 development tickets, 9 Nov 23:22
  to 10 Nov 01:13 (`sandbox_dev500_run1.json`). From then on most development runs, and validation runs 3 to 9 and
  11 to 13, ran in the sandbox (`evaluation/results/validation_looks.md`). Reportable runs stay on Groq's free tier
  in the real project. Disclosed to the course team in Mohnish Grover's message (question 6); their answer, 17 Nov:
  "Using a paid service during development is acceptable, provided your final submission follows the project
  requirements and you clearly document its usage." His words, 14 Nov 2026, on running the 500-ticket tests in the
  sandbox: "why are we not running the test in sandbox instead? the paid key is in the sandbox".
  Why the sandbox was set up (his words, 17 Nov 2026): "reason to setup the sandbox was to speed up the development
  because free tier was taking 8-10 hours".
- **D-025 (cache never on validation runs):** on 15 Nov 2026 one validation look read the development cache without
  storing anything (`--read-cache`), to test whether development results carry over; see D-036.
- **D-026 (validation closed):** validation was run 11 more times after D-026 (10-15 Nov 2026, mostly in the sandbox), all
  listed in `evaluation/results/validation_looks.md`. No rule or prompt in the system was changed because of them;
  the two rubric changes that came from validation replies (rubric v2's score descriptions, rubric v3) were removed
  on 17 Nov 2026 (Mohnish Grover: "remove 3"). His words, 14 Nov 2026: "no we
  don't decide on that we just have a look at the results".

## D-027 · Every development ticket decided question by question, in Mohnish Grover's words
- **Date:** 13-14 Nov 2026
- **Decision:** the 500 development tickets were grouped into 67 questions and each was decided (answer automatically
  or a person), with his words recorded in `evaluation/human_review/dev_walkthrough.json`; standing rules: "Never
  change Ines's words"; "If the answer is split across two articles, the reply should draw on both"; "If an
  automatic answer did not solve the problem, the follow-up goes to a person with a draft".
- **Why (his words):** "we have to train on the 500 development tickets dont forget that"; "I want it to work and
  should have zero risks".
- **AI help:** listed in the file's `ai_assistance` section; seven questions re-checked on 15 Nov (D-034).

## D-028 · Decisions are learned from his answers, not hard-coded per question
- **Date:** 14 Nov 2026
- **Decision:** a model (`src/decisions.py`) learns his answer-or-person decisions from the development tickets and can
  only send a ticket to a person; the safety rules stay underneath.
- **Why (his words):** "hardcoding is a wrong approach"; "I want us to have a system which answers how I have decided
  the answers"; "If it learns from our responses and acts later on new tickets precisely that will be better".
- **Evidence:** `scripts/learn_decisions.py`, `evaluation/results/learn_decisions.md`.

## D-029 · A follow-up goes to a person with the earlier reply
- **Date:** 14 Nov 2026
- **Decision:** the same customer, the same type, within 7 days of an automatic reply: to a person (`src/followups.py`).
- **Why (his words):** "If an automatic answer did not solve the problem, the follow-up goes to a person with a draft".

## D-030 · The learned decisions read the message only
- **Date:** 14 Nov 2026
- **Decision:** the learned decisions model reads the customer's message, not the subject line.
- **Why (his words):** "I thought we decided this earlier anyway that we see the message and not just the subject".
- **Evidence:** `scripts/compare_decision_text.py`: 384 of 384 on unseen wordings, 0 false alarms (was 375 of 384 and 8).

## D-031 · The Q25 reply is kept; the "message check" is not built
- **Date:** 14 Nov 2026
- **Decision:** a misleading subject can add an article to a reply (DEV-0374, DEV-0378); left as a known limitation.
- **Why (his words):** "lets keep how it was"; "keep that in the report".
- **Evidence:** `scripts/compare_message_check.py`: the fix removed a needed article from 10 tickets.

## D-032 · Fairness is measured inside each category first
- **Date:** 14 Nov 2026
- **Decision:** besides the raw gaps, each group's own percentage, the gaps inside each of the 67 questions, and a
  balanced sample of 120 (`scripts/fairness_balanced.py`).
- **Why (his words):** "the fairness should be measured among each category first don't you think as I don't know how
  it is possible to compare the fairness when the number of tickets are uneven in a set?"

## D-033 · The API and the monitoring dashboard, as the project files ask
- **Date:** 14 Nov 2026
- **Decision:** `src/api.py` (FastAPI) and `monitoring/grafana_dashboard.json` (the Setup Guide's five panels).
- **Why (his words):** "We have to do what is asked for in the project files so we go according to that".

## D-034 · Seven walkthrough questions decided again from the tickets and articles alone
- **Date:** 15 Nov 2026
- **Decision:** Q04, Q12, Q27, Q41, Q46, Q48, Q50, where he had asked Claude's view first, were re-checked; Q48 changed
  (D-035), the others kept, each with his words (Q27's reasoning drafted by Gemini and approved by him).
- **Why (his words):** "because you said that to me that a rate-limit increase needs a person anyway so I believed
  what you said" (Q41, the reason that started the re-check).

## D-035 · The plan rule
- **Date:** 15 Nov 2026
- **Decision:** a reply from an article that applies only to other plans goes to a person with the draft
  (`src/plans.py`).
- **Why (his words):** "It should be a general rule because if the standard plan customers cannot get their answers
  with it then it will be useless".
- **Evidence:** run `sandbox_dev500_plan_rule`: 16 of 16 Standard tickets to a person with a draft; all three
  fairness gaps under 5 points.

## D-036 · The reply cache: on for development runs, off for validation; a read-only test
- **Date:** 15 Nov 2026
- **Decision:** development runs use `--use-cache` (runs reproducible: 0 of 500 differences between two runs);
  validation and final runs stay without it; a read-only mode (`--read-cache`) reuses stored answers and stores none.
- **Why (his words):** "we dont need caching on validation tickets as we only them for testing and not training";
  "we are not tuning on the validation tickets we are testing if it replicates our development ticket results";
  "Make sure it is designed in a way where the cache is useful it takes it from there else it works without the cache
  for the tickets where its not reliable."
- **Settled 17 Nov 2026 by the course team's answer:** "You may include the implementation in your submission, but
  please keep it disabled for the hidden evaluation". The cache ships switched off by default (`src/cache.py`,
  `.env.example`: `REPLY_CACHE=off`); development runs turn it on with `--use-cache`.

## D-037 · What a person receives: a plain-words summary and, where useful, a draft
- **Date:** 16-17 Nov 2026
- **Decision:** every handover has a summary in the project files' order (the ticket, what it is about, the relevant
  articles with their knowledge base IDs, what the system was not sure about, what is attached); no question numbers
  in what an agent reads; drafts for the tickets sent to a person by his own decisions; "draft" only holds a reply
  that could be sent.
- **Why (his words):** "Better summary for sure"; "the agents don't know these questions, so why is the summary
  showing "q12"?"; "Okay so do the drafts for 25 tickets too and make the summaries as suggested in the project files,
  mention the documents too"; "write the summary as per that and should be easily undestandable"; "it still doesn't
  have where the article comes from".
- **17 Nov 2026 additions (his words):** no draft for Q11, "Don't make the draft as it will be useless for the agents
  anyway."; the second article is listed only when it makes sense, "How about including top 2 where the second one
  makes sense too" (built as: only when the knowledge base links the two articles); no suggested next step for the plan
  rule, "How can you suggest a next step without knowing the next step? ... Is it mentioned anywhere?" (no article
  states one).

## D-038 · Not built: the related-docs rule; kept: the expected-to-fail test
- **Date:** 17 Nov 2026
- **Decision:** replies are not limited to articles the knowledge base links together (tested: it would have let the
  Q25 case through and removed a needed article from 6 tickets); the test for Q41 in other words stays marked
  expected-to-fail and is explained in the README.
- **Why (his words):** "we dont need doc rule our system works fine"; "1 xfailed test is for what, as I can remember
  we will keep it".

## D-039 · The course team's answers applied (17 Nov 2026)
- **Decision:** the reply cache is off by default; the time spent waiting on rate limits is recorded apart from the
  time spent working on each ticket; the quality score counts only replies the answer key names an article for; the
  review rubric is for two human reviewers, with an AI check counted as extra only.
- **Why (the course team, 17 Nov 2026):** "keep it disabled for the hidden evaluation"; "Clearly separate the actual
  response time per ticket from delays caused by API rate limits."; "Make sure you calculate the fairness metrics
  correctly"; "an AI model cannot replace the second person."
- **Evidence:** tests `tests/test_cache.py` and `tests/test_generate.py` (346 passed, 1 xfailed).

## D-040 · Rubric v3 removed and rubric v2 cleaned of what came from validation (17 Nov 2026)
- **Decision:** rubric v3 removed; v4 is v2 with question C on v1's plain scale (the score descriptions added after
  VAL-0008 are taken out). Nothing in the system was changed by v2 or v3 (the last reply-prompt change came first).
- **Why (his words):** "get this out from the 2nd one: It gave 1 out of 5 to a reply that answers the question
  (VAL-0008) and any changes we made because of it. remove 3 and remove the changes from our system that were made
  because of it."
- **Evidence:** `prompts/evaluation/PR-03_review_rubric.md`; `evaluation/results/validation_looks.md`.

## D-041 · Demo tickets for the assessors and the repeat-contact figure (17 Nov 2026)
- **Decision:** `data/samples/demo_tickets.json` (one development ticket per channel, two for a person, one red-team
  ticket) with README commands; the metrics report counts repeat contacts and gives the history baseline.
- **Why:** Build Specification section 06, steps 13 and 14 ("One ticket from each channel is submitted"; "A ticket
  engineered to trigger a guardrail is submitted"); Evaluation Framework: repeat contacts "catches a system which
  closes tickets without actually solving anything". Mohnish Grover, 17 Nov: "do the 2 small builds yeah".
