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
