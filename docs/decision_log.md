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
