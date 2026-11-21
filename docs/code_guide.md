# Code guide: every folder and file in `cloudserve`, in plain words

Written to explain the whole project (for the video, the report and the slides). Started 17 Nov 2026 and kept up to
date as the code changes. Part 1 is the big picture, part 2 every folder and file, part 3 (to follow) the system's own
code, function by function.

Short forms used: FR (functional requirement), NFR (non-functional requirement), PRD (product requirements document),
API (application programming interface), AI (artificial intelligence), CI (continuous integration), A1-A12 (the twelve
acceptance criteria in the Build Specification), D-0xx (an entry in docs/decision_log.md).

---

## Part 1. The big picture

**What the system does.** It reads each support ticket and decides: answer it now with steps copied from a help
article, or pass it to a person with a summary and, where useful, a draft reply. Every decision and its reason is
written to a log.

**The journey of one ticket** (each step is a file in `src/`):

| Step | What happens | File |
|---|---|---|
| 1. Read | The ticket is cleaned and put into one standard shape, whatever channel it came from | `src/ingest.py` |
| 2. Classify | The system works out the ticket's type (one of 22) and how urgent it is, with how sure it is | `src/classify.py` |
| 3. Safety rules | Tickets that must always go to a person are caught (security, data location, refunds, Mohnish Grover's own decisions…) | `src/safety.py`, `src/followups.py`, `src/decisions.py` |
| 4. Search | The help articles that match the ticket are found | `src/retrieve.py` |
| 5. Route | Answer automatically, or send to a person, and why | `src/route.py` |
| 6. Write | A reply is built from the article's own words | `src/generate.py` |
| 7. Check | Five guardrails (six checks: grounding is checked two ways) run on the reply before it can be sent; any one can stop it | `src/guardrails.py` |
| 8. Plan rule | A reply from an article meant for other plans is held for a person | `src/plans.py` |
| 9. Finish | The reply is sent, or the ticket goes to a person with a summary | `src/pipeline.py`, `src/handover_text.py` |
| 10. Record | Every step goes into the decision log and the live metrics | `src/logging_store.py`, `src/metrics.py` |

`src/workflow.py` joins steps 1-9 together (LangGraph). `src/run_evaluation.py` runs a whole file of tickets with one
command and writes the results and the metrics report (`src/report.py`). `src/api.py` does the same for one ticket at a
time over the web.

**Three ways to run it** (all in the README): the unattended run (`python -m src.run_evaluation <tickets> <results>`),
the API (`python -m src.api`), and the tests (`python -m pytest -q`).

---

## Part 2. Every folder and file

### Top level

| File | What it is |
|---|---|
| `README.md` | How to install, run, test and monitor the system. The assessors follow it on a clean computer (A1) |
| `.env.example` | Every setting the system reads, with placeholder values only. Copied to `.env`, where the real key goes (never committed) |
| `.gitignore` | Files Git must never store: `.env` (the key) and `storage/` (the log, the cache, the vector store) |
| `.gitattributes` | Keeps line endings the same on Windows and other systems |
| `requirements.txt` | The Python packages the system needs, with exact versions |
| `constraints.txt` | Exact versions of every package those packages pull in, so a fresh install matches this one |
| `.github/workflows/ci.yml` | CI: GitHub runs all the tests on every push (Setup Guide step 07) |

### `src/` - the system itself

| File | What it does |
|---|---|
| `__init__.py` | Marks the folder as one package; loads the vector store library first (a Windows load-order fix) |
| `ingest.py` | Step 1. Turns tickets from email, chat, documentation comments and the forum into one shape; keeps the original text; never crashes on odd input (FR-01, A2) |
| `classify.py` | Step 2. Predicts the type and urgency, with a confidence between 0 and 1 and the alternatives it considered (FR-02, A3) |
| `safety.py` | Step 3. Word rules and ticket types that always go to a person (Daniel's rules, the zero-tolerance types, Mohnish Grover's four "person" decisions) (FR-03) |
| `followups.py` | Step 3. The same customer asking about the same thing within 7 days goes to a person, with the earlier reply |
| `decisions.py` | Step 3. A small model that learned Mohnish Grover's answer-or-person decisions; it can only send a ticket to a person |
| `retrieve.py` | Step 4. Searches the 29 help articles by meaning and by keywords, and returns the best passages with scores (FR-04, A4) |
| `route.py` | Step 5. Applies the 85% confidence threshold and the rules; writes the reason in plain words; sets the priority; the kill switch (FR-06, FR-07, FR-13, FR-16, A5) |
| `generate.py` | Step 6. Builds the reply from the article's own words (prompt PR-01 v1.7), with the article named; calls the AI with retries and a backup model; the run memory (FR-05, A6) |
| `guardrails.py` | Step 7. Five guardrails, six checks, on every reply: private data, every sentence backed by the article (two ways), no instructions from the ticket, tone and scope, confidence (FR-09, A7) |
| `plans.py` | Step 8. The plan rule: reads an article's "Applies to" line |
| `cache.py` | Stores AI answers so the same input is answered once (D-025): on for development runs, off for final runs, read-only mode |
| `handover_text.py` | The summary a person receives: the ticket, what it is about, the relevant articles, what the system was not sure about, what is attached |
| `pipeline.py` | Step 9. Builds the final outcome for a ticket (sent, or handed over) and the handover |
| `workflow.py` | Joins all the steps as a graph (LangGraph): which step follows which, and when |
| `logging_store.py` | The decision log in `storage/decisions.db` (FR-10, A8) |
| `metrics.py` | The numbers Prometheus collects for the Grafana dashboard |
| `run_evaluation.py` | The one-command unattended run over a whole file (A9), writing the results file and the metrics report (A10) |
| `report.py` | Calculates the metrics report from a run (FR-12) |
| `api.py` | The FastAPI web interface: `POST /tickets` (one ticket in, the decision and reply or handover out), `GET /health`, `/healthz` (alive) and `/readyz` (models, article index and key in place, FR-17); the `/docs` page for trying it |

### `tests/` - automatic checks (`python -m pytest -q`, A12)

Each file tests one part, with fake AI models so no key or internet is needed (that is how CI can run them).

| File | Checks |
|---|---|
| `conftest.py` | Shared test settings (switches off, fresh memory for each test) |
| `test_setup.py` | The basics from the Setup Guide: files, settings, metrics |
| `test_ingest.py` | Every channel comes through in the same shape; odd input never crashes |
| `test_classify.py` | Type, urgency and confidence; the safety rules |
| `test_retrieve.py` | Search returns real articles and stays quiet when nothing matches |
| `test_type_aware.py` | Search also uses the ticket's type (helps non-fluent English) |
| `test_route.py` | The threshold, the reasons, the priority, the kill switch, the decision log |
| `test_generate.py` | Reply writing with a fake AI, including retries and failures |
| `test_extractive.py`, `test_v15.py`, `test_v16.py`, `test_v17.py` | Each version of the reply prompt: replies copied word for word, every step included, whole article for the main one |
| `test_render.py` | What the customer sees: steps under the article they came from |
| `test_guardrails.py` | The five guardrails, with attack tickets that must be stopped |
| `test_exact_copy.py` | A sentence copied exactly from the article cannot be called unsupported |
| `test_trim.py` | An unsupported sentence is removed and the whole reply checked again |
| `test_pipeline.py` | One ticket all the way through |
| `test_run_evaluation.py` | The unattended run on a small file: nothing dropped, everything logged |
| `test_consistency.py` | The same input gets the same decision (A5) |
| `test_narrow_rules.py`, `test_question_rules.py`, `test_walkthrough_rules.py` | The safety rules and Mohnish Grover's decisions catch exactly the right tickets, and not their neighbours |
| `test_decisions.py` | The learned decisions model (includes the one expected-to-fail case, the Q41 rewording) |
| `test_followups.py` | The follow-up rule |
| `test_plans.py` | The plan rule |
| `test_handover.py` | The summary and the attached draft a person receives |
| `test_labels_not_used.py` | Proves the system never reads the answer key (labels) |
| `test_cache.py` | The cache and its read-only mode |
| `test_api.py` | The web interface, including `/healthz` and `/readyz` |
| `test_harness.py` | The harness command the Build Specification shows |

### `scripts/` - tools run by hand during building and checking (not part of a run)

| Group | Files | What they are for |
|---|---|---|
| Setting up | `setup_vector_store.py`, `setup_decision_log.py`, `check_model.py`, `list_models.py` | Build the article search index; create the log database; check the AI key works; list the models on offer |
| Training | `train_classifier.py`, `train_decision_router.py` | Train the ticket classifier (D-018) and the learned decisions model |
| Running in parts | `split_dev.py`, `join_runs.py`, `run_twenty.py` | Split the 500 into 5 parts and join the results; the 20-ticket check from the Build Specification |
| Checking a run | `check_run.py`, `check_replies.py`, `review_run.py`, `citation_audit.py`, `reference_check.py`, `project_scorecard.py` | Did the AI fail anywhere; are replies complete and copied exactly; what needs a person's eye; citations; the senior agents' reference answers; the results table |
| Fairness | `fairness_audit.py`, `fairness_balanced.py` | The fairness audit; the gaps measured inside each question |
| Consistency | `make_consistency_set.py`, `check_consistency.py` | 10 tickets x 10 copies, same decision every time (A5) |
| Experiments that decided something | `compare_retrieval.py`, `compare_thresholds.py`, `compare_runs.py`, `compare_search_query.py`, `compare_decision_text.py`, `compare_message_check.py`, `learn_decisions.py` | Chunk size and search mode (D-017); the 85% threshold (D-019); subject line or message only; can the system learn the decisions |
| Human review | `make_review_sheet.py`, `review_rubric.py`, `make_decision_sheet.py` | Build the two reviewers' sheets and the shared marking rules |
| Safety testing | `red_team.py` | Attack tickets through the real system; every one must be stopped |
| Trying replies | `try_generate.py` | Write and read a few replies by hand |

### `prompts/` - the instructions given to the AI

| File | What it is |
|---|---|
| `build/PR-01_draft_reply_v1.7.md` | The reply prompt in use: how to build a reply from the articles (earlier versions kept beside it, from `PR-01_draft_reply.md` = v1.2 to v1.6) |
| `build/PR-02_grounding_check.md` | The checker prompt: does every sentence come from the article, and does the article fit the situation |
| `evaluation/PR-03_review_rubric.md` | The marking rules for reviewing replies |
| `README.md` | The prompt register: every prompt, its versions, which one is active, and how to roll back |

### `data/` - the given data

| File | What it is |
|---|---|
| `development_tickets.json` | The 500 practice tickets. Everything is built and tuned on these |
| `validation_tickets.json` | The 80 validation tickets. Run once at the end; never used to build |
| `documentation.json` | The 29 help articles the system answers from |
| `ground_truth_responses.json` | 200 example answers by senior agents; used only to measure replies |
| `consistency_10x10.json` | The consistency test set (made by `scripts/make_consistency_set.py`) |
| `red_team/` | The attack tickets |

### `models/` - trained models

| File | What it is |
|---|---|
| `classifier.joblib` / `.json` | The ticket classifier and a record of how it was trained (D-018) |
| `decision_router.joblib` / `.json` | The learned decisions model and its record (reads the message only, 384 of 384) |

### `evaluation/` - results and reviews

| Folder or file | What it is |
|---|---|
| `results/` | Every run's results file and metrics report, plus the comparison and fairness reports |
| `human_review/dev_walkthrough.json` | Mohnish Grover's decisions on all 67 questions in the 500 practice tickets, in his words, with the AI help recorded |
| `human_review/question_groups_decisions.json` | The earlier version of the question decisions (11 Nov) |
| `human_review/review_assessor_1.xlsx`, `review_assessor_2.xlsx`, `sample_ids.json` | The human review sheets and which tickets they cover |
| `samples/` | The 500 practice tickets in 5 parts of 100, and a test set |
| `harness.py` | The harness in the form the Build Specification shows: `python -m evaluation.harness --input <file> --output <folder>`; runs the same unattended run as `src/run_evaluation.py` |

### `docs/`

| File | What it is |
|---|---|
| `architecture.md` | How the system is designed and why, by course module (rewritten 17 Nov to match the system as built) |
| `governance.md` | The Governance Framework's six sections: decision logging, risk register, fairness audit, guardrails, incident response and kill switch, declaration (completed and approved by Mohnish Grover, 20 Nov 2026) |
| `decision_log.md` | Every design decision (D-001 onward), with the reason and the evidence |
| `known_limitations.md` | What the system does not do well, with evidence and why it was not fixed |
| `code_guide.md` | This file |

### `monitoring/`

| File | What it is |
|---|---|
| `prometheus.yml` | Tells Prometheus to read the system's numbers every 15 seconds |
| `grafana_dashboard.json` | The dashboard with the Setup Guide's five panels, imported into Grafana |

### Not stored in Git: `storage/`

Created when the system runs: `decisions.db` (the decision log), `cache.db` (stored AI answers), `chroma/` (the article
search index), `kill_switch` (if present, every ticket goes to a person).

---

## Part 3. The system's own code, function by function

The files in `src/` in the order a ticket passes through them. Each table lists every function (or class) in the
file and what it does, in plain words. Written 17 Nov 2026 for the frozen version (commit 596a3be).

```
tickets file / one ticket from the API
  -> ingest.py (clean it) -> classify.py (type, urgency, confidence) -> safety.py, followups.py, decisions.py
     (must a person handle it?) -> retrieve.py (find articles) -> route.py (answer or a person?)
  -> generate.py (write the reply from the articles) -> guardrails.py (check it) -> plans.py (right plan?)
  -> pipeline.py (the outcome; handover_text.py writes the person's summary)
  workflow.py joins all of these into one LangGraph workflow; run_evaluation.py runs a whole file and
  writes logging_store.py (decision log), report.py (metrics report) and metrics.py (live numbers); api.py
  does the same for one ticket at a time; cache.py stores AI answers for development runs.
```

### 1. `ingest.py`: turn every ticket into one shape (FR-01, A2)

| Name | What it does |
|---|---|
| `CHANNELS`, `TIERS`, `REGIONS`, `FLUENCY`, `ALLOWED` | The values the Dataset Guide allows for each field (four channels, three plans, four regions, two fluency levels) |
| `BLOCKING_ISSUES` | The data problems that mean a ticket must go to a person (for example an empty message) |
| `CHANNEL_ALIASES` | Other spellings of a channel name that are accepted (for example "docs comment") |
| `Ticket` | The one shape every ticket takes inside the system: ID, channel, cleaned and original text, time, customer, plan, region, fluency, and a list of data problems. The customer's name, the labels and the history are not kept |
| `clean(value)` | Makes text safe to work with: normal characters, no hidden control characters, single spaces |
| `normalise(raw, position)` | Turns one ticket from the file into a `Ticket`. Never stops with an error: anything wrong is written into its list of problems |
| `load_tickets(path)` | Reads a whole tickets file from any path and turns every entry into a `Ticket`, so no ticket is ever dropped |
| `is_blocked(ticket)` | True when a data problem means the ticket must go straight to a person |

### 2. `classify.py`: the ticket's type and urgency, with a confidence (FR-02, A3)

| Name | What it does |
|---|---|
| `MODEL_PATH`, `SEED`, `FALLBACK_TYPE` | Where the trained classifier is saved; the fixed random seed (42) so training gives the same result every time; the type used when a ticket cannot be classified ("unclear_request") |
| `Classification` | The answer for one ticket: type, urgency, confidence (0 to 1), the three other types it considered, and whether it fell back |
| `normalise_question(text)` | The question without polite phrases, punctuation or capitals, so identical questions can be grouped |
| `question_groups(texts, similarity)` | Puts tickets that ask the same question in one group, so the same question never sits in both training and testing (group cross-validation, Module 4) |
| `_softmax`, `_fit_temperature` | Turn the classifier's scores into probabilities, and find the setting ("temperature") that makes those probabilities match how often it is really right (calibration, NFR-08) |
| `TicketClassifier` | The classifier itself: the ticket's meaning as numbers (all-MiniLM-L6-v2) and logistic regression (C = 10, D-018). `fit` trains it on the 500 development tickets; `classify` answers for one ticket and never fails (an empty ticket gives the fallback); `save` and `load` keep it in `models/classifier.joblib` |

### 3. `safety.py`: tickets that must always go to a person (FR-03)

| Name | What it does |
|---|---|
| `PERSON_ONLY_TYPES` | Ticket types that always go to a person (security incident, compliance, feature request, unclear request, data residency) |
| `RULES` | Word rules: leaked key or credentials, a key or token pasted in the ticket, security incident, data location (Daniel's rule), billing dispute, compliance, feature request |
| `NARROW_BILLING` | The billing rule without "a service we do not use", so those questions are answered from the billing article (Q14) |
| `QUESTION_RULES` | Mohnish Grover's four "person" decisions: automated jobs failing after a password change (Q11), invalid credentials with a correct password (Q12), a restore still running (Q27), throttled and would rather pay overage (Q41) |
| `SELF_EXPOSED`, `SIGN_OF_USE`, `_self_exposed_only` | A key the customer exposed by mistake is answered from the articles; any sign it was used or stolen still goes to a person (Q05) |
| `SafetyResult` | The answer: must it go to a person, and which rules fired |
| `check_text(text)` | Runs the word rules on the text and returns the names of the ones that matched |
| `NO_DRAFT` | The rule (Q11) whose tickets get no draft for the agent ("useless for the agents anyway") |
| `decided_for_a_person(reasons)` | True when every reason is one of Mohnish Grover's own decisions, not a fixed safety rule; such tickets get a draft for the agent |
| `check(text, predicted_type)` | Runs the word rules and the person-only types together; either one is enough |

### 4. `followups.py`: a follow-up goes to a person (FR-14)

| Name | What it does |
|---|---|
| `WINDOW` | Seven days (the Evaluation Framework's repeat-contact window) |
| `reset()` | Forgets everything at the start of a run |
| `remember(ticket, intent, reply)` | After an automatic reply, keeps it so a follow-up from the same customer can be recognised |
| `earlier(ticket, intent)` | The same customer's latest automatic reply on the same type within the 7 days before, or nothing |
| `reason(e)` | The plain-words reason given when a follow-up goes to a person |

### 5. `decisions.py`: Mohnish Grover's decisions, learned (D-028)

| Name | What it does |
|---|---|
| `MODEL_PATH`, `THRESHOLD` | Where the learned model is saved; 0.5, the likelihood at which a ticket goes to a person |
| `enabled()` | Whether the learned layer is switched on (`LEARNED_DECISIONS`, on by default) |
| `load(path)` | Loads the learned model once |
| `person_probability(vector, path)` | How likely Mohnish Grover would send this ticket to a person, from its meaning |
| `text_of(ticket)` | What it reads: the message only, not the subject (D-030) |
| `is_reason(text)`, `reason(p)` | Recognise and write its reason: "similar tickets were handled by a person (NN% likely)" |

### 6. `retrieve.py`: find the articles that answer the ticket (FR-04, A4)

| Name | What it does |
|---|---|
| `CHUNK_SIZE`, `CHUNK_OVERLAP`, `TOP_K`, `MIN_SIMILARITY`, `SEARCH_MODE` | 400-character passages with 80 overlapping; the best 5; nothing returned below 0.35; meaning and keyword search together (D-017) |
| `Passage` | One search result: article ID, title, passage text, rank and scores |
| `STOPWORDS`, `tokenize(text)` | Common words ("how", "to") ignored by the keyword search, and the text split into words |
| `BM25` | The keyword search (Best Matching 25): good at exact codes such as 429 or 401 |
| `rrf(rankings, k)` | Merges the meaning and keyword rankings (reciprocal rank fusion) |
| `load_documents`, `chunk_documents` | Read the 29 articles and cut them into passages, keeping each one's article ID and title |
| `default_embedder`, `_unit` | The meaning model (the same one as the classifier) and its number vectors |
| `Retriever` | The search itself. `from_store` loads the passages from the Chroma store; `search` returns ranked passages, or an empty list when nothing is relevant enough (each article appears once) |
| `TYPE_CATEGORIES`, `TYPE_FLOOR`, `type_aware()` | Which kinds of article each ticket type needs; the lowest score an added article may have (0.25); whether type-aware search is on |
| `strip_filler(text)` | Removes "please help fast", "waiting for your reply" and similar, which pull the search towards the wrong articles |
| `search_typed(retriever, text, intent)` | Type-aware search: if none of the top 3 articles is of the kind the ticket's type needs, the best one of that kind is put third (11 Nov, for non-fluent tickets) |

### 7. `route.py`: answer automatically or send to a person (FR-06, FR-07, FR-13, FR-16, A5)

| Name | What it does |
|---|---|
| `CONFIDENCE_THRESHOLD` | 0.85: the classifier must be at least 85% sure (D-019) |
| `DRAFT_READY_MIN_CONFIDENCE` | 0.60: below the threshold but at least this sure, with an article and no rule, the person gets "Draft ready: check and send" |
| `SLA_MINUTES`, `NEAR_BREACH_MINUTES` | The two-hour reply promise; a ticket waiting 90 minutes moves up the queue |
| `URGENT_WORDS`, `HIGH_PRIORITY_REASONS` | Words and rules that raise a ticket's priority |
| `RouteDecision` | The decision: answer or a person, the label, priority, confidence, threshold, reasons, and the requirement IDs |
| `kill_switch_on(path)` | Checked before every ticket: if the file `storage/kill_switch` exists (or KILL_SWITCH=on), every ticket goes to a person |
| `_priority(...)` | High, medium or low, raised for urgent words, security risks or a long wait |
| `route(...)` | Collects every reason not to answer (kill switch, unclassifiable, a safety rule, no article, confidence below 85%). None: answer automatically. Any: to a person, with every reason written in plain words. The same input always gives the same decision |
| `queue_key(decision, received_at)` | The order of the agents' queue: near breach first, then high, medium, low, then oldest |

### 8. `generate.py`: the reply, copied from the articles (FR-05, FR-08, FR-11)

| Name | What it does |
|---|---|
| `ACTIVE_PROMPT`, `EXTRACTIVE`, `ALL_STEPS`, `WHOLE_ARTICLE` | Which prompt version is used (PR-01 v1.7) and how replies are built (word for word, every step, the whole main article) |
| `NO_ANSWER`, `NOTICE`, `HEADING`, `ALSO`, `CAUSES`, `GREETING` | The fixed texts written by the code, never by the model: the "not covered" sentence, the automatic-reply notice, "From our help article …:", "(also in: …)", "Common causes listed in the article:", "Thanks for getting in touch." |
| `_WAITED`, `reset_wait()`, `waited_ms()` | Add up the time spent waiting on rate limits for each ticket (17 Nov, the course team) |
| `Reply`, `tokens_of(text)` | The model's text with the provider's token counts |
| `PermanentError`, `TransientError` | Two kinds of failure: not worth retrying (wrong key, bad request) and worth retrying (rate limit, server error, timeout) |
| `Draft` | The written reply and everything about it: the chosen pieces, the articles cited, sure or not, a one-line summary, what it was unsure about, model, tokens, time |
| `load_prompt(name)` | Reads the prompt file from `prompts/build/` |
| `articles_for(passages, top)` | The whole text of the top 3 articles the search found, for the model to read |
| `article_pieces(content)`, `number_pieces(articles)` | Cut an article into labelled pieces (R steps, C causes, N notes) and show them to the model |
| `parse_pieces(raw, labels)` | Reads the model's answer safely: every chosen label must exist, or the reply is not used |
| `complete_steps(chosen, labels)` | Adds every step of the chosen article in order, and for the main article every note and common cause (PR-01 v1.6 and v1.7) |
| `provider(role)`, `call_model(...)` | Which AI service to call, and the call itself (Groq's free tier in the real project) |
| `_RUN_MEMO`, `remember(raw, model)` | Within one run, the same input gets the same answer (A5) |
| `call_with_fallback(...)` | The main model, retrying temporary errors with growing random waits (and as long as the provider asks), then the backup model; if all fail, the ticket goes to a person |
| `_pieces`, `assemble(sentences)` | The internal draft with numbered sentences, used by the checks |
| `_title`, `render(draft, passages)` | What the customer sees: each step under the name of the article it came from |
| `parse(raw, n_articles)` | The older reading of a model-written reply (kept for the rollback prompt) |
| `generate(ticket_text, intent, passages)` | The whole step: build the prompt with the ticket between marks, call the model, read its answer, copy the article text. Anything unreadable or "not answered" goes to a person, never to the customer |
| `with_notice(draft, passages)` | The final reply text: the rendered reply plus the automatic-reply notice |

### 9. `guardrails.py`: five guardrails (six checks) on every reply before it is sent (FR-09, A7)

| Name | What it does |
|---|---|
| `GUARD_MODEL`, `WORD_SUPPORT_MIN`, `MAX_WORDS`, `MAX_WORDS_TWO_ARTICLES` | The second model (qwen3.8-27b); 60% of a sentence's words must be in its article; length limits (230 words, 320 for two articles) |
| `Check`, `Report` | One check's result (passed, detail), and all of them for one reply (`blocked`, `fired`, `as_log` for the decision log) |
| `PRIVATE`, `private_data(...)` | Check 1: names, emails, phone numbers, keys, account numbers |
| `_stem`, `_words`, `word_support(...)` | Check 2: every number and most words of each sentence are in the article it cites |
| `_shown`, `exact_copy(...)` | Show the checker the Common causes as the customer sees them; a sentence copied exactly from its article always counts as supported |
| `model_support(...)` | Check 3: the second model (PR-02) checks the article fits the customer's situation and every sentence is supported |
| `TAKEOVER`, `LEAK`, `instruction_integrity(...)` | Check 4: the ticket tried to give the system instructions, or the reply leaks them |
| `PROMISES`, `RUDE`, `tone_and_scope(...)` | Check 5: no promises about refunds, credits or dates; polite; not too long |
| `confidence_floor(...)` | Check 6: the classifier was confident enough and the writer was sure (a missing confidence counts as low) |
| `check_reply(...)` | Runs all six. If any check itself fails, the reply is blocked (fail closed) |
| `TRIM_MAX_SHARE`, `trim(draft, report)` | Removes only the sentences a grounding check named (at most half), so the whole reply can be checked again |

### 10. `plans.py`: the plan rule (FR-18)

| Name | What it does |
|---|---|
| `enabled()` | Whether the plan rule is on (`PLAN_RULE`, on by default) |
| `applies_to(content)`, `plan_limited(applies)` | Read the article's "Applies to" line, and tell whether it names plans |
| `excluded(tier, cited_ids, articles)` | The first article in the reply that does not apply to this customer's plan (an unknown plan counts as not covered) |
| `reason(...)` | The plain-words reason given to the person |

### 11. `handover_text.py`: the summary a person receives (FR-07)

| Name | What it does |
|---|---|
| `TOPIC`, `RULE`, `TYPE` | The 22 ticket types, every rule and every reason, in plain words (no question numbers) |
| `excerpt`, `about` | The ticket in short (subject and message, 250 characters) and what it is about |
| `not_sure(...)` | Every reason the system did not answer by itself, one plain sentence each |
| `_articles`, `_where(doc_id, titles)` | Where an article comes from: its title, its knowledge base ID and the plans it applies to |
| `closest(passages)` | With no reply attached: the closest article, and the second only when the knowledge base links the two |
| `titles_in(reply)` | The articles a reply was written from |
| `summary(...)` | The whole summary in the project files' order: the ticket, what it is about, the relevant articles, what the system was not sure about, what is attached |

### 12. `pipeline.py`: one ticket's outcome

| Name | What it does |
|---|---|
| `ACKNOWLEDGEMENT` | The fixed message a customer gets when a person has their ticket (no promise of time or outcome) |
| `Outcome` | The final result for one ticket: action, label, priority, reason, what was sent, the handover, every stage's result, model calls, time, waiting time, tokens, sources |
| `citation_trail(draft, sources)` | For each cited article, the passages search found and the sentences it supports, so every citation can be followed (A6) |
| `_handover(...)` | Builds what the person receives: the summary, what was tried, the articles, the draft (only a reply that could be sent), the earlier reply for a follow-up, a reply a check stopped |
| `finish(state, ...)` | Builds the one final `Outcome` from whatever stages ran |
| `process(ticket, ...)` | One ticket through the whole workflow |

### 13. `workflow.py`: the stages joined as one LangGraph workflow (D-023)

| Name | What it does |
|---|---|
| `TicketState` | What travels from step to step for one ticket |
| `build(...)` | Builds the workflow. Steps: `classify`, `check_rules` (safety rules, follow-up rule, learned decisions), `search`, `route`, `write`, `validate` (the five guardrails, then trim and check again), and four endings: `send`, `handover`, `blocked`, `plan`. `draft_for_person` decides when a person gets a draft. Every branch is decided by code, never by the model |
| `run_ticket(...)` | Starts the waiting count at zero and runs one ticket through the workflow |

### 14. `run_evaluation.py`: the whole file, unattended (FR-12, A8 to A11)

| Name | What it does |
|---|---|
| `summary(t)` | A short description of the ticket for the log, with no personal details |
| `log_ticket(...)` | Writes every stage, then the final outcome, to the decision log (one trace per ticket) |
| `failed(t, e)` | An unexpected error: the ticket goes to a person with the reason; the run continues |
| `record_metrics(t, o)`, `as_result(o)` | Updates the live numbers; writes one ticket's result |
| `CIRCUIT_AFTER`, `provider_down(t)` | After 3 tickets in a row with the AI service down, the rest go straight to a person instead of each waiting |
| `run_evaluation(input_path, output_path, ...)` | The one command: reads any tickets file, processes every ticket in the order received, writes the results file, the decision log and the metrics report. The reply cache is off unless a development run asks for it (`--use-cache`, `--read-cache`, `--refresh-cache`) |
| `main()` | The command line: `python -m src.run_evaluation <input> <output>` (also through `python -m evaluation.harness --input … --output …`) |

### 15. `logging_store.py`: the decision log (FR-10, A8)

| Name | What it does |
|---|---|
| `db_path(url)`, `connect(url)` | Where `storage/decisions.db` is, and opening it |
| `DecisionRecord` | One log record with the Governance Framework's fields; checked against a fixed shape before it is written |
| `write(record, connection)`, `read(connection, run_id, stage)` | Write one record; read a run's records back |

### 16. `report.py`: the metrics report (FR-12, A10)

| Name | What it does |
|---|---|
| `SEGMENTS`, `_pct` | The customer groups compared (plan, region, fluency, channel), and percentages |
| `calibration_table(rows, bands)` | Stated confidence against real accuracy, in five bands (Evaluation Framework) |
| `_tokens(outcomes, n)` | Tokens used and how many answers came from the cache |
| `repeat_contacts(outcomes, raw_by_id)` | Follow-ups found in the run, and the history baseline (17 Nov) |
| `build(...)` | The whole report: volume, business, technical (precision and recall per type, confusion matrix, retrieval hit rate, latency with and without rate-limit waits), governance (decisions logged, guardrail activations, private data), calibration, and results by customer group. The answer key is read only here, after every ticket is done |

### 17. `cache.py`: stored AI answers for development runs (D-025, off by default)

| Name | What it does |
|---|---|
| `enabled()`, `read_only()`, `refresh()` | Which mode: off (the default), on, read only, or refresh (fresh answers, stored) |
| `path()`, `key(messages, models)`, `_connect()` | Where `storage/cache.db` is; the fingerprint of exactly what the model received |
| `get(k)`, `put(k, raw, model)` | Look up and store an answer; a broken cache only means a fresh call |

### 18. `metrics.py`: live numbers for Prometheus (Setup Guide 06)

| Name | What it does |
|---|---|
| `TICKETS`, `LATENCY`, `GUARDRAIL`, `CONFIDENCE` | Tickets by channel and outcome, response time, guardrail activations, confidence; all start at 0 so the dashboard panels move |
| `start_metrics_server(port)` | Serves the numbers at http://localhost:8001/metrics |

### 19. `api.py`: one ticket at a time (FR-17)

| Name | What it does |
|---|---|
| `TicketIn` | The ticket fields the API accepts; anything else, such as labels, is dropped |
| `readiness(root)` | What is missing before tickets can be answered: the trained models, the article index, the AI key |
| `create_app(...)` | The FastAPI application: `POST /tickets`, `GET /health`, `GET /healthz`, `GET /readyz` |
| `main()` | `python -m src.api`: the API on port 8000 and the live numbers on port 8001 |

### 20. `__init__.py`

Loads the article search library before scikit-learn, which stops a crash on Windows (found 7 Nov, D-019).
