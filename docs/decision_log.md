# Decision log

Engineering decisions for the CloudServe support system: what was decided, why, and the evidence.
Runtime decisions made by the system itself are logged separately in `storage/decisions.db` (Setup Guide step 05).

## D-001 · Python 3.11 in a virtual environment
- **Date:** 3 Nov 2026
- **Decision:** Use Python 3.11 (`py install 3.11`, then `py -3.11 -m venv .venv`).
- **Why:** The laptop's default Python is 3.14, which is newer than much of the pinned stack supports. The guide requires 3.10 or later, and its own CI file uses 3.11.

## D-002 · Windows equivalents of the guide's commands
- **Date:** 3 Nov 2026
- **Decision:** `python3` → `py -3.11`; `which python` → `Get-Command python`; the guide's `echo ".env" >> .gitignore` is not run.
- **Why:** `python3` and `which` are macOS/Linux commands. In Windows PowerShell 5.1, `echo >>` writes UTF-16, which Git does not read as a valid `.gitignore`. `.env` is already line 1 of `.gitignore`, created before `.env` existed, so the guide's intent is met.

## D-003 · Six fixes to the pack's requirements.txt
- **Date:** 3–4 Nov 2026
- **Decision:** The smallest change that installs and imports cleanly, one line at a time, each tested with `pip install --dry-run` and an import test.
- **Why and evidence:**
  1. `openai 1.0.0 → 1.10.0`: pip ResolutionImpossible, langchain-openai needs openai >= 1.10.0.
  2. `pydantic 2.0.0 → 2.0.2`: fastapi 0.104.0 excludes pydantic 2.0.0 and 2.0.1.
  3. `langchain-openai 0.0.7 → 0.0.6`: 0.0.7 needs langsmith >= 0.1 while langchain 0.1.0 needs < 0.1. 0.0.6 is the newest that fits.
  4. `chromadb 0.3.21 → 0.4.13`: 0.3.21 depends on hnswlib, which needs Microsoft C++ Build Tools on Windows. 0.4.13 is the oldest 0.4 that installs ready-made (tested 0.4.0 to 0.4.13 in order).
  5. Added `huggingface-hub==0.25.2`: sentence-transformers 2.2.2 imports `cached_download`, removed in huggingface-hub 0.26 (ImportError).
  6. Added `posthog==5.4.0`: chromadb 0.4.13 uses posthog's pre-6 API, and posthog 7.x logged "Failed to send telemetry event" on every Chroma call.
- **Rejected:** Installing C++ Build Tools, because the marker's machine will not have them and setup must work from a clean checkout (A1).

## D-004 · Groq as the model provider
- **Date:** 3 Nov 2026
- **Decision:** Groq free tier, main model `openai/gpt-oss-20b`, backup `openai/gpt-oss-120b`.
- **Why:** The guide allows OpenRouter or Groq. The pack's OpenRouter model `meta-llama/llama-3.1-8b-instruct` is no longer free, and OpenRouter's free tier allows about 50 requests a day, too few for a 120-ticket run. Groq limits for gpt-oss-20b: 30 requests/min, 1,000/day, 8,000 tokens/min, 200,000 tokens/day.
- **Evidence:** `scripts/check_model.py` returned 200 "ready" for both models (4 Nov 2026).

## D-005 · Provider-neutral settings and an optional fallback
- **Date:** 4 Nov 2026
- **Decision:** `.env.example` uses `LLM_BASE_URL` / `LLM_API_KEY` instead of `OPENROUTER_API_KEY`. The OpenRouter fallback is supported but its key is left empty, so if Groq is unavailable, tickets escalate to a person (A11).
- **Why:** Changing provider becomes a settings change, not a code change. The free fallback was not reliable enough to depend on.
- **Evidence:** OpenRouter free models returned 429 "rate-limited upstream" in three separate tests (3–4 Nov 2026, gemma-4-26b and gemma-31b).

## D-006 · Vector store built from the guide's code, with four changes
- **Date:** 4 Nov 2026
- **Decision:** `doc["id"]` → `doc["doc_id"]`; file read as UTF-8; store rebuilt from empty on each run; library notices switched off individually, each with a comment.
- **Why:** The guide's `id` field does not exist in the data (KeyError). Windows' default encoding breaks on non-ASCII characters. A rebuild must give the same result however often it runs.
- **Evidence:** 59 passages from 29 documents. Test query "How do I reset my password?" returns DOC-AUTH-001.
- **Open:** Chunk size 800/120 is the guide's starting point. At least two configurations will be compared on retrieval quality (guide step 04).

## D-007 · Five added columns in the runtime decision log
- **Date:** 4 Nov 2026
- **Decision:** The guide's 13 columns plus `run_id`, `alternatives`, `provider`, `model`, `latency_ms`.
- **Why:** Reconciling one run against its tickets (A8, A9), explaining low confidence, tracing which model answered or that none did (A11), and measuring the 95th-percentile response time.

## D-008 · Full pack datasets committed in data/
- **Date:** 4 Nov 2026
- **Decision:** Commit the four pack JSON files, although the guide's layout says `data/` should hold "small samples only".
- **Why:** The system cannot build its vector store on a clean machine without `documentation.json`, and the evaluation needs the ticket files. The files are the pack's own and contain no secrets.

## D-009 · Environment loaded by the code, not by the editor
- **Date:** 4 Nov 2026
- **Decision:** VS Code's `python.terminal.useEnvFile` stays off.
- **Why:** The marker runs the code in a plain terminal. With injection on, a script that forgot `load_dotenv()` would work here and fail for them (guide section 09: KeyError on an environment variable).

## D-010 · Monitoring: metrics now, Prometheus and Grafana once the pipeline runs
- **Date:** 4 Nov 2026
- **Decision:** The guide's three metrics are in `src/metrics.py`, plus a `classification_confidence` histogram. The guide's `prometheus.yml` is in `monitoring/`, unchanged. Prometheus and Grafana are installed once there is a running pipeline to watch.
- **Why:** The guide's dashboard list includes "the distribution of confidence scores", which none of its three metrics can show. A dashboard with no pipeline behind it would show empty charts. The unattended run (A9) and metrics report (A10) must not depend on either program, so the marker never needs to install them.
- **Also:** The metrics server is bound to 127.0.0.1, so Windows shows no firewall prompt, and Prometheus reads it from the same machine.
- **Evidence:** A test ticket and a confidence score were read back from `http://localhost:8001/metrics` (4 Nov 2026).


## D-011 · CI: the guide's workflow with current action versions and a pinned runner
- **Date:** 4 Nov 2026
- **Decision:** `actions/checkout@v4 → @v6`, `actions/setup-python@v5 → @v6`, `ubuntu-latest → ubuntu-24.04`. Everything else as in the guide.
- **Why:** The first CI run passed (5 tests, 2m 45s) but GitHub annotated it with a warning ("Node.js 20 is deprecated" for checkout@v4 and setup-python@v5) and a notice ("ubuntu-latest will migrate to Ubuntu 26"). The v6 actions run on Node 24. Pinning the runner keeps CI reproducible instead of changing operating system without notice.
- **Evidence:** GitHub Actions run for commit 3f0062b (4 Nov 2026): Success, 1 warning, 1 notice.


## D-012 · README requires Python 3.11 exactly
- **Date:** 4 Nov 2026
- **Decision:** The README asks for Python 3.11 (link to 3.11.9), not the guide's "3.10 or later". Only the environment step differs by operating system. Windows activation uses `Set-ExecutionPolicy -Scope Process`, which applies to that window only and needs no administrator rights.
- **Why:** The pack pins numpy 1.24.0 and pandas 2.0.0, which support Python only up to 3.11. On a newer Python, pip would try to build them from source and fail. PowerShell's default policy blocks the activation script (hit on day one).


## D-013 · OpenRouter fallback removed
- **Date:** 4 Nov 2026
- **Decision:** One provider (Groq) with two models. If Groq is unavailable, tickets are escalated to a person with the reason logged (A11). Replaces the optional fallback in D-005.
- **Why:** The free OpenRouter models returned 429 "rate-limited upstream" in all three tests (3–4 Nov 2026). The pack uses free tiers only, so a working fallback was never available to the marker. In the clean-clone rehearsal, the empty fallback key made the README unclear.

## D-014 · Every package pinned with constraints.txt
- **Date:** 4 Nov 2026
- **Decision:** `constraints.txt` holds `pip freeze` of the tested environment. `requirements.txt` references it with `-c constraints.txt`, so the guide's install command is unchanged.
- **Why:** requirements.txt pins only the packages we ask for. Between the 3 Nov install and the 4 Nov rehearsal, five helper packages came out at newer versions with no change on our side (filelock, jsonpatch, platformdirs, pyzmq, mypy-extensions). Unpinned helper releases already broke setup twice (huggingface-hub, posthog). The marker installs later than we test.
- **Note:** Regenerate constraints.txt whenever requirements.txt changes.

## D-015 · README fixes from the clean-clone rehearsal
- **Date:** 4 Nov 2026
- **Decision:** Name the Python installer file to choose; add `-Force` to the execution policy line; say that `.env` (not `.env.example`) is the file to edit, with the command to open it; say to leave every other line as it is.
- **Why:** A fresh clone followed literally in a new PowerShell window (Setup Guide step 09) worked end to end, but each of these points made the reader stop or guess.

## D-016 · Ticket type is decided by a classifier trained on the development tickets, not by the language model
- **Date:** 7 Nov 2026
- **Decision:** Each ticket is turned into numbers by meaning (the same embedding model as the document store) and a small classifier, trained on the 500 labelled development tickets, predicts its type and urgency with a probability. The language model is used only to write replies. Fixed safety rules run alongside the classifier (FR-03).
- **Why:** It gives the same answer every time (acceptance criterion A5); its probabilities can be checked against real accuracy (NFR-08: within 5 points); it costs no model calls, which protects the unattended run on the free tier (FR-12, NFR-07); and it answers in milliseconds (NFR-01). The development tickets are labelled for exactly this purpose (Project Brief: "developing your classifier").
- **Considered:** Asking the language model to choose the type. Rejected: a model call per ticket on the free tier, answers that can vary between runs, and a stated confidence that is hard to calibrate.

## D-017 · Articles are split into 400-character passages and searched by meaning and keyword together, with a relevance threshold of 0.35
- **Date:** 7 Nov 2026
- **Decision:** Chunk size 400 characters with an overlap of 80; hybrid search (meaning-based embeddings plus BM25 (Best Matching 25) keyword scores, merged by reciprocal rank fusion); each article appears once in the results; nothing is returned when the best meaning-based match is below 0.35, and the ticket is escalated.
- **Why:** 400 found the expected article in the top 5 for 98.0% of answerable development tickets, usually first (MRR (mean reciprocal rank) 0.935), the best of the six options, and its passages are about a quarter the size of whole articles, so each model call is cheaper and faster on the free tier. Hybrid beat meaning-only search at 400 (98.0% against 97.8%) and at 800 (97.8% against 96.9%) at no extra cost, and catches exact codes such as 429 and 401. A threshold of 0.35 wrongly escalates the same single answerable ticket as 0.30 (1 of 357) while returning nothing for 11.2% of unanswerable tickets rather than 4.2%, and keeps a wide gap above off-topic questions (best match 0.11 to 0.15). Higher thresholds cost real answers: 0.50 would wrongly escalate 28 answerable tickets (7.8%).
- **How strong the evidence is:** against the Setup Guide's 800, the quality difference is small (about one more ticket found in the top 5, MRR 0.935 against 0.924). What tips it is cost: passages half the size make each model call about half the size. Chosen on development tickets only. The final validation run reports the result; nothing is changed after it (D-026).
- **Considered:** the Setup Guide's 800 / 120 ("a starting point", "a design decision, not a default") and 1,500 characters (in effect whole articles: 29 passages for 29 articles); meaning-only search; thresholds from 0.20 to 0.50.
- **Found while testing:** keyword search matched common words ("how", "do", "to"), lifting a billing article to second place for a rollback question, and the same article filled several of the five places. Common words are now ignored and each article appears once; both fixes are tested.
- **Limits:** the threshold only catches off-topic questions. Tickets that need a person are caught by the classifier, the safety rules and the confidence threshold (D-019). Non-fluent tickets find the expected article 94.3% of the time against 98.0% overall: reported in the fairness audit.
- **Evidence:** `evaluation/results/retrieval_comparison.md` (`python scripts/compare_retrieval.py`), 357 answerable and 143 unanswerable development tickets, 7 Nov 2026.
- **Revisit if:** articles become longer or more numerous (after submission; not on validation results, D-026).


## D-018 · The classifier reads tickets as embeddings, with logistic regression at C = 10
- **Date:** 7 Nov 2026
- **Decision:** Ticket type and urgency come from logistic regression on all-MiniLM-L6-v2 sentence embeddings (the same model the search uses), with C (strength setting) = 10 and a learned temperature so that stated confidence matches real accuracy. Saved to `models/classifier.joblib` with a record of the data, code version, seed and date.
- **Why (Mohnish's reasoning):** type accuracy is 99%, the calibration gap is 0.6 points, and on questions it has not seen before it is right 77% of the time, which is better than every other option we compared.
- **The numbers:** 5-fold cross-validation, grouped so the same question never sits in both training and testing. Embeddings C = 10: accuracy 99.0%, weighted precision 99.1% [98.4%, 99.8%], macro recall 99.0%, largest calibration gap 0.6 points, stress test 77.6%. TF-IDF (term frequency–inverse document frequency) C = 10: 99.6%, gap 0.0 points, stress test 51.2%. Both C = 1 options fail the 5-point calibration limit (26.7 and 12.9 points).
- **How strong the evidence is:** on familiar questions the options are within each other's error ranges, so accuracy does not decide it. The stress test does: 77.6% against 51.2% when whole questions are hidden from training, which is the case that matters for reworded and new tickets. Chosen on development tickets only. The final validation run reports the result; nothing is changed after it (D-026).
- **Considered:** TF-IDF with C = 1 and C = 10; embeddings with C = 1; the language model as classifier (D-016).
- **Cost:** no new model or download; each ticket is embedded once, well under a second.
- **Limits:** urgency is right only about half the time for every option (48.0% to 51.8%), because the labels disagree with themselves: 74 of 203 groups of identical questions carry mixed urgency, and at most 55.2% is predictable from the type. Priority (FR-13 (functional requirement 13)) therefore adds rule signals in routing, and this is reported as a data finding.
- **Safety rules alongside it (FR-03):** of 122 person-only development tickets, the word rules catch 107 (87.7%) and the person-only type catches the other 15; none is missed by both. 12 of 378 safe tickets (3.2%) are flagged, all "charges for a service we do not believe we use", sent to a person by choice as possible billing disputes.
- **Evidence:** `evaluation/results/classifier_comparison.md` (`python scripts/train_classifier.py`), run on Mohnish's machine, 7 Nov 2026.
- **Revisit if:** in service, type accuracy falls below 90% or the calibration gap rises above 5 points (not on validation results, D-026).

## D-019 · A ticket is answered automatically only when the classifier is at least 85% confident
- **Date:** 7 Nov 2026
- **Decision:** `CONFIDENCE_THRESHOLD=0.85` (Setup Guide default 0.80). Below it, a safe ticket with a relevant article goes to a person labelled "Draft ready: check and send" (FR-07 (functional requirement 7)). The threshold applies after the safety rules (FR-03) and the search threshold (D-017), never instead of them.
- **Why (Mohnish's reasoning):** 0.85 gives the same results as 0.80.
- **The numbers:** out-of-fold predictions on the 500 development tickets (classifier from D-018). At 0.80 and 0.85 alike: no must-not ticket answered automatically, no wrong type among automatic answers, 268 of the 311 should-be-automatic tickets answered (real FCR (first contact resolution) 53.6%), largest group gap 8.2 points (region). 0.50 and 0.60 answer 3 tickets with the wrong type; 0.90 and above lose answers (252 to 260) and widen the gap to 11.4 to 15.6 points.
- **How strong the evidence is:** the threshold moves real FCR only between 50.8% and 54.6%; the safety rules, not the threshold, keep risky tickets out (0 at every threshold). Chosen on development tickets only. The final validation run reports the result; nothing is changed after it (D-026).
- **Considered:** 0.50, 0.60, 0.70, 0.80, 0.90, 0.95, 0.98.
- **Found while testing:** routing lets through about 86 tickets the answer key sends to a person, 72 of them not answerable from the articles: search finds something close, but not an answer. The grounding check (Day 4) must stop these, so the 70.8% "answered automatically" is not the expected FCR. Also, on Windows, loading scikit-learn before Chroma crashed Python ("access violation" in onnxruntime); `src/__init__.py` now loads Chroma first.
- **Limits:** the fairness gap (8.2 points by region, Latin America 82.1% against Europe 90.3%) fails the 5-point target at every threshold, so the threshold does not cause it and cannot fix it. Cause found: 36 of the 43 should-be-automatic tickets sent to a person were sent by the safety rules on purpose (21 data location, 9 possible billing disputes, 6 leaked keys), and 6 of Latin America's 7 were data location questions; on the questions the rules allow the system to answer, Latin America got 32 of 33. The gap's 95% range is wide (3.6 to 22.3 points) because the groups are small. The official fairness audit (Governance Framework, section 3) is measured on the validation run, on resolution rate, quality score and citation accuracy, with this explanation in its Explanation column.
- **Evidence:** `evaluation/results/threshold_comparison.md` (`python scripts/compare_thresholds.py`), run on Mohnish's machine, 7 Nov 2026.
- **Revisit if:** in service, a wrong type appears among automatic answers, or calibration drifts above 5 points (not on validation results, D-026).

## D-020 · Grounding is checked twice: a word check in code, then a second model from another family
- **Date:** 8 Nov 2026
- **Decision:** Guardrail 2 (grounding, FR-09 (functional requirement 9)) has two layers. (a) In code: for each sentence, every number and at least 60% of its meaningful words must appear in the article it cites. (b) Only if every cheaper check passes: qwen/qwen3.8-27b (prompt PR-02) checks that the cited article fits the customer's actual situation and that every sentence is supported. Either layer blocks; if the checker is unavailable or its answer cannot be read, the reply is blocked (fail closed).
- **Why:** option (c) of three, chosen by Mohnish after asking for a recommendation. The word check alone cannot see a correctly copied step that does not fit the situation, which is the failure seen on DEV-0011 (security-incident steps for a password change, then a console-login step for failing automated jobs), and "a confident but wrong answer" is rated critical in the risk register. The second model alone could miss a made-up number that the word check catches for certain. A different model family from the writer (gpt-oss) means the writer does not mark its own work (Module 5); the day-5 evaluation judge is chosen then, so that the evaluation is not marked by the guardrail's own model either.
- **Considered:** (a) word check only (free, instant, same result every time); (b) second model only.
- **Cost:** one extra free-tier call per reply that would be sent automatically, and only after the cheap checks pass; slower replies, measured against the 3-second target on the full run.
- **First evidence:** on the six v1.2 replies (8 Nov), the word check passes five and blocks DEV-0012's third sentence ("…you can cancel it and start a new job, but it is usually not necessary…"), which the article does not say: a correct block. The other four guardrails pass all six.
- **Model change (same day):** llama-3.1-8b-instant was planned, but Groq returned HTTP 404 (no longer offered). `scripts/list_models.py` listed the chat models Groq offers on 8 Nov 2026: gpt-oss (20b, 120b, safeguard-20b), qwen/qwen3.8-27b and allam-2-7b. Qwen is the only other general model family, so it is the checker. Model names are now checked against the provider's list rather than remembered.
- **Limits:** the 60% word threshold is a first setting, to be checked against the false-alarm rate on ordinary tickets (FR-09 asks for it).
- **Revisit if:** the false-alarm rate on development tickets is high, or the checker misses a wrong-situation reply found in development testing (not on validation results, D-026).

## D-021 · Red-team findings: four rule gaps closed, the tickets kept as regression tests
- **Date:** 8 Nov 2026
- **Decision:** after the first red-team run (14 attack tickets in `data/red_team/red_team_tickets.json`, real pipeline and models), add: a safety rule that sends any ticket containing something that looks like a key or token to a person before any model call (RT-05); security-incident patterns for "someone logged into our account from…" (RT-10); "money back" as a billing dispute (RT-07); and instruction-integrity patterns for politely worded instructions aimed at the system ("note to the AI assistant", "mark this ticket as…", "bypass your checks") (RT-04, RT-14). The 14 tickets stay as regression tests, re-run after every prompt or guardrail change.
- **Why:** first run, 13 of 14 passed, but only one of the passes was luck-free in every case. RT-05 failed: a real-looking key pasted into the ticket was sent to the model and a reply was sent to the customer (NFR-04: "a ticket containing a key or token goes to a person as a security matter"; "send the model only what it needs"). Four passes had the right outcome for the wrong reason: RT-04 was stopped only by the word check, RT-07 by the phrase "written confirmation" in the data location rule, RT-10 by the classifier calling it an unclear request, RT-03 by the classifier calling it a security incident.
- **False alarms:** none of the new patterns matches any of the 500 development tickets.
- **Also seen:** RT-13 (Spanish) found no article and went to a person, which is safe but means non-English tickets are never answered automatically; noted for the fairness audit. The writer model sometimes joins two words ("log inagain") even after the space fix, so it appears to come from the model itself; to be counted in the evaluation.
- **Evidence:** `evaluation/results/red_team.md` (`python scripts/red_team.py`), 8 Nov 2026.

## D-022 · The word check compares numbers exactly; "one" is not treated as a number
- **Date:** 9 Nov 2026
- **Decision:** in grounding guardrail layer (a), a number in a reply sentence must appear in the cited article exactly as written (not in the shortened form used for other words), and "one" is no longer on the list of number words.
- **Why:** the full run of all 500 development tickets (8–9 Nov, parts 1–5, `evaluation/results/dev_all_run.json`) had 50 replies blocked by the word check; 42 of them for "a number not in the article". 34 were the word "hundred" ("keep the page size at or below two hundred", which the article says word for word): the article's words were shortened ("hundred" → "hundr") but the reply's numbers were not, so they never matched. 8 were "one" used as an ordinary word ("one of the keys"). A bug in code, found on development tickets, not validation.
- **Still blocked, correctly:** numbers the article does not state, such as a time the model calculated itself ("a 400-gigabyte database should take roughly 40 minutes", DEV-0024).
- **Evidence:** the 50 word-check blocks are re-run on their own (`evaluation/samples/dev_word_blocked.json`) to measure the fix before any re-check on validation.

## D-023 · The stages run as one LangGraph workflow
- **Date:** 9 Nov 2026
- **Decision:** the pipeline's stages (classify, safety rules, search, route, write, validate) and its three endings (hand-over to a person, guardrail block, send) are nodes in one LangGraph graph (`src/workflow.py`, langgraph 0.0.20 as pinned); every branch is a conditional edge decided by code from the stage results. `process()` runs every ticket through it, so the harness, the red-team run and the tests all use the same graph.
- **Why:** Module 7: a single orchestrated workflow, bounded (no loops, at most eight steps per ticket), with the model never choosing the path, and one state per ticket whose ID is the trace ID in the decision log (FR-10). The architecture (`docs/architecture.md`, section on orchestration) planned LangGraph only.
- **What did not change:** the stages, their order and their rules are the same as the plain function they replace (day 4), so earlier results stay comparable; the 99 tests, including the six pipeline tests and four harness tests, now pass through the graph.
- **Considered:** keeping the plain Python function (simpler, but the course asks for an orchestrated workflow with visible, testable branches).

## D-024 · Withdrawn the same day: no paid provider, even for development test runs
- **Date:** 9 Nov 2026
- **What was proposed:** sending the reply writer through OpenRouter's paid service (pinned to Groq's servers, about $0.10 per 500 tickets) to make test runs faster, because the free tier's daily token allowance made them take hours (part 2 of the 500 development tickets: 5 hours; the validation check run: 32 of 80 tickets after about 90 minutes). The code was written and tested, then removed before any money was spent.
- **Why withdrawn:** the project rules say so directly. Project Instructions: "Nothing. Free tiers only, and no part of the marking advantages paid capacity." Build Specification: "Free tiers throttle. Handling that with backoff, queuing and caching is part of the engineering, not an obstacle to it", and throttling during assessment "is not a defect in your work and it will not reduce your marks." NFR-07 (free tiers only) stands unchanged.
- **Instead:** a reply cache (D-025), the engineering answer the Build Specification names.
- **Also checked:** the model the Setup Guide suggests, meta-llama/llama-3.1-8b-instruct through OpenRouter, is still offered there (Groq no longer offers it directly: HTTP 404 on 8 Nov); not adopted, because it is smaller and older than gpt-oss-20b and switching would mean re-testing every prompt. The laptop (12 GB memory, 2 GB GeForce 920M) is too small to run gpt-oss-20b locally.

## D-025 · A reply cache: the same prompt to the same model is answered once, then reused
- **Date:** 9 Nov 2026
- **Decision:** every model answer that was read successfully (the writer's reply and the grounding checker's verdict) is stored in `storage/cache.db`, keyed by a hash of exactly what the model received (prompt text and version, ticket, articles) and the model list. The same input later gets the stored answer with no model call and no tokens. Turned off with `REPLY_CACHE=off`.
- **Why:** the Build Specification: "Free tiers throttle. Handling that with backoff, queuing and caching is part of the engineering" (and D-024). The tickets repeat: 343 different texts among the 500 development tickets (31% repeats). It also makes the system more consistent (NFR-11): the same ticket gets the same reply.
- **Safe because:** any change to the prompt, ticket, articles or model changes the key, so nothing stale is reused; answers that could not be read are never stored; replies hold no personal details (guardrail 1 blocks any that do), every reused reply still passes through all five guardrails, and the cache sits in `storage/`, which Git ignores. Only the real model call uses it; tests with fake models never do.
- **Reported:** each metrics report states how many replies and checks were reused.
- **Never on validation or final runs (Mohnish's point, the same day):** the harness turns the cache off for every run unless `--use-cache` is given, and that flag is only for development runs. Validation, hidden-set and final runs neither read nor write stored answers, so they stay a fresh, independent test and are not shaped by earlier runs, as the assessors' run (with an empty cache) will not be. Each report states whether the cache was on. No validation answer was ever stored: the cache was created after the validation runs had started.

## D-026 · Validation tickets are closed until the final run: no peeking at all
- **Date:** 9 Nov 2026
- **Decision (Mohnish's rule):** nothing is taken from the validation tickets. They are not opened, analysed or run while the system is being developed. All finding and fixing uses development tickets only. Validation is run once more, at the very end, after every decision is final; its results are reported as they are, and nothing is changed afterwards, whatever they show.
- **Why:** the Project Brief's rule for `validation_tickets.json`: "Your final evaluation, run once, near the end. Do not look at these while building. Do not tune against them." and "Report your evaluation date and the number of runs in your report; a single honest run is worth more than an inflated one." (The Project Instructions and Dataset Guide say the validation tickets may be checked "as often as you like"; the stricter rule is followed from this date.)
- **What had been done before this rule, disclosed in full** (found by searching the code, tests, documents and history on 9 Nov; the use of validation here was Claude's working error, not checked against the Project Brief at the time):
  1. Discovery (Stage 1): the validation answer key was read to work out two figures (67.5% answerable and safe; 32.5% to a person) and a count of 14 reworded tickets; these appeared in the Stage 1 workbook, the PRD, the deck and the explainer document.
  2. 7 Nov (day 1): the ingest check and one test read the validation file (ticket text and channels, not labels).
  3. 7 Nov: the stated reason for D-018 mentioned the count of reworded validation tickets (the choice itself rested on the development stress test).
  4. 8 Nov: the new D-021 safety patterns were run over validation text to look for false alarms; none matched and nothing was changed.
  5. 8 Nov: validation run 1 (the baseline), and its results read ticket by ticket.
  6. 9 Nov: the stated reason for D-025 mentioned how many validation texts repeat development texts.
  7. 9 Nov: validation run 2 (a check of the D-022 fix found on development tickets), compared with run 1.
- **What never used validation:** the classifier's training, the search settings (D-017), the threshold (D-019), the safety rules and guardrails, every prompt, the D-022 fix, the 60-ticket experiment set and the cache contents. No rule, prompt or setting was written for a validation ticket.
- **Put right on 9 Nov:** validation figures removed from the workbook, PRD, prompt library, deck and explainer; the reasons for D-017 to D-020 and D-025 rewritten with development evidence only, and their "the validation run confirms or overturns it" lines replaced; the ingest check and its test moved to the development file. The two runs' result files are kept, not deleted, so the record is complete.
- **Limit that cannot be removed:** the validation set has been run twice and looked at, so the final validation figure is not a first look. The hidden 120 tickets, never seen, remain the clean measure.

## Entries D-027 to D-042: how they were written

Drafted by Claude (Anthropic) on 17 Nov 2026 from the project's files and Mohnish Grover's own words, which are quoted with their dates; checked and approved by Mohnish Grover on 21 Nov 2026. Every "Why" is his words or the course team's.

## Corrections to D-024, D-025 and D-026 (the log must match what happened)

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

## D-042 · Decisions confirmed before the final development run (17 Nov 2026)
- **Q41 stays with a person.** His words: "q41 to person" (as on 15 Nov: "send it to a person because of the noise").
  Evidence: `docs/known_limitations.md`, 3 (the noise check of 341 replies).
- **Type-aware search stays on.** His words: "type aware search on". Evidence: found in development run v14 (11 Nov
  11:50), tested on development run v14_typed (non-fluent tickets: expected article found 81 to 83 of 87; answered
  89 to 95 of 120).
- **A refresh mode for the reply cache** (`--refresh-cache`): every answer fresh, the new answers stored. His words:
  "you can store the cache but dont use the old one from previos 500 run".
- **Check before the run:** 50 development tickets run fresh (`sandbox_dev_check_50_nocache.json`): 49 of 50 identical
  to the last 500-ticket run; DEV-0376 (Q02) used one article instead of two (known limitation 2).
