# CloudServe support system

Triage for CloudServe support tickets: classifies each ticket, finds the relevant documentation, drafts a cited answer or escalates to a person, and logs every decision.

## What you need first

- **Python 3.11.** [Download 3.11.9](https://www.python.org/downloads/release/python-3119/). Other versions will not work: several pinned packages support Python only up to 3.11.
- **A free Groq API key**, from https://console.groq.com/keys
- About **4 GB of free disk space** and an internet connection. The first run downloads about 1 GB.

## Setup

Open a terminal in this folder (the one containing this README) and run each step in order.

### 1. Create and activate the environment

**Windows (PowerShell):**

```powershell
py -3.11 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
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

This takes several minutes.

### 3. Add your API key

```
cp .env.example .env
```

Open `.env` in any text editor, replace `your_groq_key_here` with your Groq key (no quotes, no spaces), and save.

### 4. Check the model responds

```
python scripts/check_model.py
```

You should see `200` and `reply: ready` for `main` and `backup`, then `fallback: skipped`.

### 5. Build the document store and the decision log

```
python scripts/setup_vector_store.py
python scripts/setup_decision_log.py
```

The first run downloads the embedding model, which takes a few minutes. You should see:

```
stored 59 passages from 29 documents
test query -> top result: DOC-AUTH-001 | Resolving invalid credential errors on login
decision log ready: storage/decisions.db (18 columns, 0 rows)
```

### 6. Run the tests

```
python -m pytest tests/ -v
```

Every test should show `PASSED`.

## Running the system

To be added as each stage is built.