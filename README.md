# CloudServe support system

Triage for CloudServe support tickets: classifies each ticket, finds the relevant documentation, drafts a cited answer or escalates to a person, and logs every decision.

## What you need first

- **Python 3.11.** [Download 3.11.9](https://www.python.org/downloads/release/python-3119/). On that page, under **Files**, choose **Windows installer (64-bit)** on Windows or **macOS 64-bit universal2 installer** on a Mac, and install with the default options. On Linux, install `python3.11` and `python3.11-venv` with your package manager. Other versions will not work: several pinned packages support Python only up to 3.11.
- **A free Groq API key**, from https://console.groq.com/keys
- About **4 GB of free disk space** and an internet connection. The first run downloads about 1 GB.

## Setup

Open a terminal in this folder (the one containing this README) and run each step in order.

### 1. Create and activate the environment

**Windows (PowerShell):**

```powershell
py -3.11 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.venv\Scripts\activate
python --version
```

**macOS / Linux:**

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python --version
```

You should see `Python 3.11.x`, and your prompt now starts with `(.venv)`.
**From here on, every command is the same on every system.**

### 2. Install the dependencies

```
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

This takes several minutes. Every package is pinned to the exact version that was tested.

### 3. Add your API key

```
cp .env.example .env
```

This creates a new file called `.env`. Open **`.env`** (not `.env.example`): on Windows with `notepad .env`, on macOS with `open -e .env`, on Linux with `nano .env`. Replace `your_groq_key_here` with your Groq key (no quotes, no spaces), leave every other line as it is, and save.

### 4. Check the model responds

```
python scripts/check_model.py
```

You should see `200` and `reply: ready` for both `main` and `backup`.

### 5. Build the document store and the decision log

```
python scripts/setup_vector_store.py
python scripts/setup_decision_log.py
```

The first run downloads the embedding model, which takes a few minutes. You should see:

```
stored 141 passages from 29 documents
test query -> top result: DOC-AUTH-001 | Resolving invalid credential errors on login
decision log ready: storage/decisions.db (18 columns, 0 rows)
```

### 6. Run the tests

```
python -m pytest tests/ -v
```

Every test should show `PASSED` (274 tests).

## Running the system

### Process a file of tickets, unattended

Put the ticket file (in the same format as `data/development_tickets.json`) anywhere you like, then run:

```
python -m src.run_evaluation <tickets file> <results file>
```

For example, for the hidden test set:

```
python -m src.run_evaluation data/test_tickets.json evaluation/results/test_run.json
```

It needs no further input. Each ticket is classified, checked against the safety rules, matched to the help
articles, answered or passed to a person, and logged. It writes:

- `<results file>`: one entry per ticket, with the decision, the reply sent and the articles cited;
- `<results file>_metrics.md` beside it: the measures for the run, with the settings it used;
- `storage/decisions.db`: a log row for every decision.

**How long it takes:** on Groq's free tier, 80 tickets took about 8 minutes and 500 tickets about 10 hours
(12 Nov 2026). When the free tier's limit is reached, the system waits and tries again on its own; a ticket whose
reply cannot be checked is never sent and goes to a person instead. Leave the terminal open until it finishes.

### Settings

The tested settings are the defaults, so nothing needs to be set. Each can be switched off for a comparison,
for example `$env:QUESTION_RULES="off"` in PowerShell or `export QUESTION_RULES=off` on macOS/Linux:

| Setting | Default | What it does |
|---|---|---|
| `PR01_FILE` | `PR-01_draft_reply_v1.7.md` | The reply prompt. `PR-01_draft_reply.md` is the earlier v1.2 (rollback) |
| `QUESTION_RULES` | on | Questions decided by Mohnish Grover go to a person (data location, missing export records, jobs failing after a password change) |
| `NARROW_RULES` | on | Safety rules hold back requests and disputes, not plain questions |
| `TYPE_AWARE_SEARCH` | on | Article search also uses the ticket's type |
| `TRIM_UNSUPPORTED` | on | A sentence the checker cannot support is removed and the whole reply checked again |
| `REPLY_CACHE` | off in runs | Stored answers are never used for validation or test runs (D-025) |

To stop all automatic replies at once (kill switch), create an empty file called `storage/kill_switch`:
every ticket then goes to a person. Delete the file to turn replies back on.

### Red-team check

```
python scripts/red_team.py
```

Runs the attack tickets in `data/red_team/` through the real system and writes `evaluation/results/red_team.md`.
Every one must be stopped.