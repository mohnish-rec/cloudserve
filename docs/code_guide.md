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
| 7. Check | Six checks run on the reply before it can be sent; any one can stop it | `src/guardrails.py` |
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
| `guardrails.py` | Step 7. Six checks on every reply: private data, every sentence backed by the article (two ways), no instructions from the ticket, tone and scope, confidence (FR-09, A7) |
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
| `test_guardrails.py` | The six checks, with attack tickets that must be stopped |
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
| `governance.md` | The Governance Framework's six sections: decision logging, risk register, fairness audit, guardrails, incident response and kill switch, declaration (draft; the judgements are Mohnish Grover's to complete) |
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

To follow: one section per file in `src/`, in the order a ticket passes through them.
