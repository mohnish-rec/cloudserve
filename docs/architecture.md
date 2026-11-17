# Architecture

How the CloudServe support system is designed, and why. Each choice traces to a requirement in the PRD (product requirements document) version 2 and to the course module it comes from. Written 7 November 2026, before the build; rewritten 17 November 2026 to match the system as built (the earlier text is in Git history). Every file is explained in `docs/code_guide.md`.

## 1. Why the system exists: the translation ladder (Module 1)

| Layer | CloudServe |
|---|---|
| L1 Business outcome | First reply within the two-hour agreement; first-contact resolution from 43.8% to 60% or more; without adding staff |
| L2 Decision changed | For each ticket: answer it now from an article, or hand it to the right person with the work already done |
| L3 Metric | First-contact resolution, escalation rate, first-reply time, repeat contacts, fairness gap between customer groups |
| L4 Signal | The ticket's type and urgency with a calibrated confidence; whether an article answers it; whether it is a risky type |
| L5 Model task | Classify the ticket; find the article; write a cited reply or a hand-over; check it before release |

Downward check: an answer that is classified, grounded in an article and checked is what lets a ticket close without a person (L1). Upward check: a perfect L4 signal changes L2 for about 70% of tickets (the safe ceiling in the workbook, Section 2).

## 2. Boundaries (Module 1)

- **We own:** reading tickets, classifying, searching the 29 articles, writing replies and hand-overs, guardrails, routing, the decision log, the metrics report.
- **We assume:** the articles are correct and current; agents read hand-overs; the hidden tickets resemble the development tickets (PRD section 7).
- **Not ours:** sending email, account changes, refunds, live channel connections, writing articles (PRD section 6).

## 3. The pipeline (as built)

```
tickets file (python -m src.run_evaluation, or python -m evaluation.harness) / one ticket (API, python -m src.api)
  -> 1 Ingest        raw kept + cleaned copy + data-quality checks; never crashes            (FR-01, A2)
  -> 2 Classify      type (22) and urgency, confidence 0-1, alternatives                     (FR-02, A3)
  -> 3 Rules         a person must handle it? fixed safety rules and person-only types;
                     Mohnish Grover's four "person" decisions; follow-up within 7 days;
                     the learned decisions model (can only send to a person)                 (FR-03)
  -> 4 Search        400-character passages, meaning + keyword search merged (RRF),
                     relevance floor 0.35, top 5; also uses the ticket's type                 (FR-04, A4)
  -> 5 Route         answer only at 85% confidence or more, no rule fired, an article found;
                     reason in plain words; priority; kill switch                             (FR-06, FR-13, FR-16, A5)
  -> 6 Write         the main article copied word for word (prompt PR-01 v1.7), named         (FR-05, A6)
  -> 7 Check         six guardrails; an unsupported sentence is removed and the reply
                     checked again; any failure blocks (fail closed)                          (FR-09, A7)
  -> 8 Plan rule     an article for other plans is held for a person
  -> answered:  the reply + the automatic-reply notice                                        (FR-08)
     to a person: an acknowledgement to the customer; for the agent a summary (the ticket,
                  what it is about, the relevant articles, what the system was not sure
                  about) and, where useful, a draft reply                                     (FR-07)
  -> decision log (every step), results file, metrics report, live metrics                     (FR-10, FR-12, A8-A10)
```

The steps are joined as one LangGraph workflow (`src/workflow.py`, D-023). Every exit is either **answered** or **with
a person, with a reason**. Nothing is dropped and one bad ticket never stops the run (FR-11, A9, A11).

**What the system does not do** (CloudServe's own support tool would): send the email or chat message, put the
ticket in the agents' queue, change accounts, issue refunds. The system returns the reply or the handover, and the
support tool delivers it (through the API, `POST /tickets`).

## 4. The Generative Four and the Sustaining Three (Module 1)

| Lever | Decision | How (as built) |
|---|---|---|
| Retrieval | Current, not stale | The 29 supplied articles are searched for every ticket. (Every article was reviewed 0 days ago in the data, so no age check is needed.) |
| Context | Specific to this ticket | The ticket's text, type, urgency and channel; the customer's name is never used |
| Memory | Within limits | Within one run: the same input gets the same answer (A5), and the same customer asking again within 7 days goes to a person (follow-up rule) |
| Feedback | Reviewed by people, not self-learning | The system never changes itself while running. Its only learned decisions were trained once, offline, on Mohnish Grover's own decisions for the 500 development tickets, never on the answer key or on past handling (Daniel: learning from current practice would "scale up a mistake") |
| Guardrails | Prevent | Fixed safety rules before any AI call; six guardrails after it |
| Orchestration | Coordinate and record | One LangGraph workflow; every step logged with the ticket ID |
| Recovery | Fail to a person, never to silence | Retries with backoff, a backup model, then a person; after 3 tickets in a row with the AI service down, the rest go straight to a person; the kill switch |

## 5. Data pipeline card (Module 3)

| Question | Answer |
|---|---|
| Source to destination | Tickets file -> decision log, results file, metrics report |
| ETL or ELT | **ELT** (extract, load, transform): each ticket is kept raw as received and a cleaned copy is made |
| Pipeline or orchestration | Per ticket: orchestration (each step depends on the one before). Across tickets: a pipeline (one bad ticket never stops the others) |
| Load | The whole input file each run; tickets processed in the order received; every run has its own run ID |
| Idempotency | Re-running the same file gives the same decisions under a new run ID; nothing is overwritten |
| Failure handling | Temporary errors (rate limits, server errors, timeouts): retry with backoff and jitter. Permanent errors: no retry. Both end with a person and the reason |
| Quarantine | A ticket that fails the data-quality checks goes to a person with its reasons |
| Monitoring | Prometheus and Grafana: tickets per hour by channel and outcome, answered vs escalated, latency, guardrail activations, confidence distribution |

## 6. Classifier (Module 4)

- all-MiniLM-L6-v2 embeddings with logistic regression (C = 10), chosen over a TF-IDF (term frequency-inverse document frequency) baseline (D-016, D-018).
- Trained only on the 500 development tickets, with groups kept together so the same message is never on both sides of a test.
- Confidence checked with the Evaluation Framework's calibration table; the 85% threshold set from development data (D-019).

## 7. Retrieval and writing (Modules 2 and 5)

- **Search:** 400-character passages; meaning and keyword (BM25, Best Matching 25) search merged by reciprocal rank fusion; relevance floor 0.35 (D-017). A ticket whose type calls for a kind of article the search missed gets the best one of that kind third (type-aware search, for non-fluent English).
- **Writing:** the writer reads the whole of the top 3 articles and chooses which to answer from; the code copies the main article word for word (every step, note and common cause, without the symptoms list) and the steps of a second article if needed. Help articles are never reworded ("Never change Ines's words"). Prompt PR-01 v1.7; versions and reasons in `prompts/README.md`.
- **Injection defence:** the ticket is placed between marks and declared to be data; instructions in it are never followed; a guardrail checks for them.
- **Structured output:** JSON (JavaScript Object Notation) checked in code; anything unreadable goes to a person.
- **Consistency and cost:** within a run, the same input gets the same answer; a reply cache stores AI answers for development runs only (D-025).

## 8. Guardrails (Module 5, Governance Framework)

| Guardrail | Checks | When it fires |
|---|---|---|
| private_data | Names, addresses, keys, account numbers, anything identifying a customer | Block; the agent gets no reply text |
| grounding_words | Every sentence's words and numbers are in its article | Block (or remove the sentence and check again) |
| grounding_model | A second model from another family (Qwen, PR-02) checks the article fits the situation and each sentence is supported; a sentence copied exactly from its article is always supported | Block, with the unsupported part flagged |
| instruction_integrity | The ticket has not tried to instruct the system, and the reply holds none of our instructions | Block; the agent gets no reply text |
| tone_and_scope | No promises about refunds, credits or dates; within support; within the length limit | Block |
| confidence_floor | The classifier was confident enough and the writer was sure | Block |

All guardrails **fail closed**: if a check errors, the reply is blocked. The red-team tickets (`data/red_team/`) are kept as regression tests.

## 9. Interfaces, orchestration and deployment (Module 7)

- One orchestrated workflow with one writing model, not a crew of agents; LangGraph (D-023).
- FastAPI (`src/api.py`): `POST /tickets` (one ticket in, the decision and reply or handover out), `GET /health`, `GET /healthz` (alive) and `GET /readyz` (models, article index and key in place) (FR-17); `/docs` to try a ticket in the browser.
- Unattended run: `python -m src.run_evaluation <input> <output>` or `python -m evaluation.harness --input <file> --output <folder>`.
- Monitoring: Prometheus reads the metrics; the Grafana dashboard (`monitoring/grafana_dashboard.json`) shows the Setup Guide's five panels.
- CI: GitHub runs every test on every push. Pinned requirements; the key only in `.env`.

## 10. How the system is judged (Module 1, eval first)

Gates: type precision 85%+; calibration within 5 points; unsupported claims 5% or fewer; citation accuracy 95%+; zero private data; zero automatic replies to must-not tickets; fairness gap under 5 points (also measured inside each question); the same decision for the same input. Also measured: latency at the median and 95th percentile, first contact resolution, escalation rate. Known limitations are listed in `docs/known_limitations.md`.

## 11. Architecture decisions

In full in `docs/decision_log.md`: D-016 (a trained classifier decides the type), D-017 (passages and hybrid search), D-018 (embeddings with logistic regression), D-019 (the 85% threshold), D-020 (grounding checked twice), D-021 (red-team findings), D-023 (LangGraph), D-025 (reply cache), D-026 (validation closed until the final run). Decisions from 13 Nov onward (the walkthrough of the 500 development tickets, the plan rule, the handover summary) are being added from D-027.
