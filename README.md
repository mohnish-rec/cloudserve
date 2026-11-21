# CloudServe support system

Triage for CloudServe support tickets: it classifies each ticket, finds the relevant help article, sends a cited
answer or passes the ticket to a person, and logs every decision.

Built by Mohnish Grover for the FDE (Forward Deployed Engineer) capstone, November 2026. Code written with help from
Claude (Anthropic) says so at the top of the file; every file was reviewed and run by Mohnish Grover.

## Contents

Follow the steps in order. Each one says what you should see when it has worked.

- [Before you start](#before-you-start)
- **Set it up (once, about 20 minutes):** [1. Get the code](#step-1-get-the-code) ·
  [2. Create the Python environment](#step-2-create-the-projects-python-environment) ·
  [3. Install the packages](#step-3-install-the-packages-it-needs) · [4. Add your API key](#step-4-add-your-api-key) ·
  [5. Check the AI model answers](#step-5-check-the-ai-model-answers) ·
  [6. Build the article store and the decision log](#step-6-build-the-article-store-and-the-decision-log)
- **Use it:** [7. Start the system](#step-7-start-the-system) ·
  [8. Send one ticket from each channel, an escalation and a guardrail ticket](#step-8-send-one-ticket-from-each-channel-an-escalation-and-a-guardrail-ticket) ·
  [9. Run a whole file of tickets, unattended](#step-9-run-a-whole-file-of-tickets-unattended) ·
  [10. Check the metrics report against the decision log](#step-10-check-the-metrics-report-against-the-decision-log) ·
  [11. Run the tests](#step-11-run-the-tests)
- [More checks](#more-checks): the kill switch, coping with problems, attacks
- [Optional: watch it live](#optional-watch-it-live-prometheus-and-grafana) (Prometheus and Grafana)
- [If something goes wrong](#if-something-goes-wrong)
- [About the project](#about-the-project)

## Before you start

These instructions are for **Windows 10 or 11, using PowerShell**, where the system was built and tested. Every
command here is typed in PowerShell (press the Windows key, type `PowerShell`, press Enter).

You need:

- **Python 3.11** (other versions will not work) and **Git**. Install both with these two commands, then **close
  PowerShell and open a new one**:

  ```powershell
  winget install -e --id Python.Python.3.11
  winget install -e --id Git.Git
  ```

  (If `winget` is not found, download [Python 3.11.9](https://www.python.org/downloads/release/python-3119/), the
  **Windows installer (64-bit)**, and Git from https://git-scm.com.)

- **A free Groq API key** (the password that lets the system use Groq's AI models), from https://console.groq.com/keys
- About **4 GB of free disk space** and an internet connection.

## Set it up (once)

### Step 1. Get the code

```powershell
mkdir C:\cloudserve_test
cd C:\cloudserve_test
git clone https://github.com/mohnish-rec/cloudserve.git
cd cloudserve
```

Every command from here on is typed in this `C:\cloudserve_test\cloudserve` folder.

### Step 2. Create the project's Python environment

*A private copy of Python just for this project.*

```powershell
py -3.11 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.venv\Scripts\activate
python --version
```

You should see `Python 3.11.x`, and the line now starts with `(.venv)`.

> **The project window.** "The project window" in this README means a PowerShell window in the project folder with
> `(.venv)` at the start of the line. In any **new** PowerShell window, type these three lines first:
>
> ```powershell
> cd C:\cloudserve_test\cloudserve
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
> .venv\Scripts\activate
> ```

### Step 3. Install the packages it needs

*The exact versions the system was tested with. This takes several minutes.*

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Step 4. Add your API key

```powershell
cp .env.example .env
notepad .env
```

In Notepad, replace `your_groq_key_here` with your Groq key (no quotes, no spaces), leave every other line as it is,
save and close. The `.env` file stays on your computer and is never uploaded.

### Step 5. Check the AI model answers

```powershell
python scripts/check_model.py
```

You should see `200` and `reply: ready` for both `main` and `backup`.

### Step 6. Build the article store and the decision log

```powershell
python scripts/setup_vector_store.py
python scripts/setup_decision_log.py
```

The first time, it downloads a model, which takes a few minutes. You should see:

```
stored 141 passages from 29 documents
test query -> top result: DOC-AUTH-001 | Resolving invalid credential errors on login
decision log ready: storage/decisions.db (20 columns, 0 rows)
```

## Use it

### Step 7. Start the system

In the project window:

```powershell
python -m src.api
```

The system keeps running in this window: **leave it open**. To stop it, press **Ctrl+C** in this window.

Open **http://127.0.0.1:8000** in your web browser. Steps 8 to 10 can all be done on this page, and clicking any
ticket shows everything the system decided about it and why (the reply or the note for the person, the articles, each
guardrail's result, and its rows in the decision log).

For the PowerShell commands in the next steps, **open a second PowerShell window** and make it a project window (the
three lines in step 2).

### Step 8. Send one ticket from each channel, an escalation and a guardrail ticket

**On the web page,** press **Send the 7 demo tickets**. **Or,** in the second project window:

```powershell
python scripts/send_demo_tickets.py
```

You should see:

| Ticket | Channel | About | You should see |
|---|---|---|---|
| DEV-0319 | Email | Unexpected overage charges | Answered automatically |
| DEV-0108 | Chat | Deployments fail at the health check | Answered automatically |
| DEV-0422 | Documentation comment | A pagination cursor stops working | Answered automatically |
| DEV-0330 | Forum | Connection pool exhausted | Answered automatically |
| DEV-0058 | Email | Where is our data stored? | Sent to a person (data location rule) |
| DEV-0033 | Chat | Single sign-on problem, Standard plan | Sent to a person with a draft (the article is for other plans) |
| RT-01 | Email | Hidden instruction: "ignore all previous instructions…" | Blocked by a guardrail |

Two things to know:

- **Send them once after starting the system.** A second time, the answered ones go to a person on purpose: the same
  customer writing again within 7 days means the first answer did not solve it (the follow-up rule). To start again,
  restart the system (**Ctrl+C**, then `python -m src.api`).
- **Groq's free tier allows about 5 answered tickets a minute.** Sent faster, a reply's check cannot run and the reply
  is blocked rather than sent unchecked. Wait a minute between batches.

### Step 9. Run a whole file of tickets, unattended

*One run processes every ticket in a file with nobody touching it, and writes a metrics report at the end.*

**With one command** (this does not need the system from step 7). In the project window, for the 80 validation
tickets that come with the project:

```powershell
python -m src.run_evaluation data/validation_tickets.json evaluation/results/validation_run.json
```

For another file, put it in the project's `data` folder and use its name instead, with a new name for the results.
For example, for the hidden evaluation set saved as `data/hidden_evaluation_tickets.json`:

```powershell
python -m src.run_evaluation data/hidden_evaluation_tickets.json evaluation/results/hidden_evaluation_run.json
```

Leave it until it finishes, with the window open. On Groq's free tier the 80 validation tickets take about 8 minutes.
When the free tier's limit is reached, the system waits and tries again by itself.

**Or on the web page:** under **Run a whole ticket file**, press **Choose file**, pick the file, press **Run**, and
leave the page open.

**What it writes,** in the `evaluation/results` folder:

- the results file (for example `validation_run.json`): one entry per ticket, with the decision, the reply and the
  articles cited;
- the metrics report (for example `validation_run_metrics.md`): every measure against its target, why any target was
  missed, and the volume, business, technical and governance figures;
- and a row for every decision in the decision log, `storage/decisions.db`.

(The same run can also be started as `python -m evaluation.harness --input data/validation_tickets.json --output evaluation/results/`.)

### Step 10. Check the metrics report against the decision log

*This proves every ticket was logged exactly once.*

1. Open the metrics report from step 9. Under **Governance**, the line **Decisions logged** says, for example,
   `356 rows; 80 final outcomes for 80 tickets -> reconciles`. Under **Volume** are the numbers answered
   automatically, escalated and blocked.
2. Count the same things straight from the decision log, in the project window:

   ```powershell
   python scripts/check_decision_log.py
   ```

   It checks the most recent run. You should see the same numbers as in the report, and **Result: RECONCILES**.

**On the web page,** after a run from the page, press **Check against the decision log** under the metrics report.

### Step 11. Run the tests

*They need no API key and make no calls to the AI models.* In the project window:

```powershell
python -m pytest tests/ -v
```

The last line should read `382 passed, 1 xfailed`. The one `xfailed` ("expected to fail") is deliberate: a known
limitation kept visible as a test (`docs/known_limitations.md`, number 5). It is not a failure.

## More checks

### Check the kill switch

*It stops every automatic reply at once, without changing any code: while it is on, every ticket goes to a person.*

**On the web page,** the **Kill switch** box shows whether it is on, and its button turns it on or off. Turn it on,
send the demo tickets, and every one goes to a person with the reason "the kill switch is on". Then turn it off.
Every change is written, with the time, to `storage/kill_switch_history.txt`.

**Or in the project window:** `New-Item storage\kill_switch -ItemType File -Force` turns it on, and
`Remove-Item storage\kill_switch` turns it off.

Turn it off before running the tests, and restart the system before sending the demo tickets again.

### Check it copes with problems

| Problem | How to cause it | You should see |
|---|---|---|
| The AI service cannot be reached | Disconnect from the internet, or put a wrong key in `.env` (put the real one back afterwards), then send the demo tickets | Nothing crashes and no unchecked reply is sent: each ticket goes to a person with the reason "model unavailable" |
| The free tier's limit is reached | Send the demo tickets twice quickly | The system waits and tries again; a reply whose check cannot run goes to a person. The page's **Free tier limits** box shows it |
| No article matches | On the web page, write a ticket such as "What is the weather like today?" | It goes to a person, and the AI model is not called |
| An empty ticket | At http://127.0.0.1:8000/docs, **POST /tickets**, **Try it out**, send a ticket with `"body": ""` | It goes to a person, and the system carries on |

### Check it stops attacks (red-team check)

*Fourteen tickets written to trick the system (hidden instructions, a pasted secret key, a refund demand, and others)
are sent through the real system. Each must be handled safely. It takes a few minutes.*

```powershell
python scripts/red_team.py
```

The result for every ticket is written to `evaluation/results/red_team.md`.

## Optional: watch it live (Prometheus and Grafana)

*Live charts of the system's work. Nothing else needs them. Set them up once, with the system from step 7 running.*

1. **Get Prometheus** (tested with 3.13.5). From https://prometheus.io/download/, under **prometheus**, download the
   Windows file (ending in `windows-amd64.zip`), then unzip it into `C:\prometheus`:

   ```powershell
   Get-ChildItem "$env:USERPROFILE\Downloads\prometheus-*windows-amd64.zip" | Expand-Archive -DestinationPath C:\prometheus -Force
   ```

2. **Get Grafana** (tested with 13.3.1). Press **Yes** if Windows asks for permission:

   ```powershell
   winget install -e --id GrafanaLabs.Grafana.OSS
   ```

   Open http://localhost:3000, sign in with `admin` / `admin`, and choose a new password.

3. **Start the charts.** On the system's web page, press **Start the live charts from zero** and wait for **Ready**
   (about a minute). It starts Prometheus in a small window on the taskbar; leave that open.
4. **Connect Grafana to Prometheus** (once). In Grafana: **Connections > Data sources > Add data source >
   Prometheus**, URL `http://localhost:9090`, **Save & test**.
5. **Load the dashboard** (once). In Grafana: **Dashboards > New > Import**, upload
   `C:\cloudserve_test\cloudserve\monitoring\grafana_dashboard.json`, choose the Prometheus data source, **Import**.

**From now on:** start the system, press **Start the live charts from zero**, wait for **Ready**, click **Open the
Grafana dashboard**, and send tickets from the page. In Grafana, set the time range to **Last 15 minutes** and the
refresh to **10s**.

## If something goes wrong

| What you see | What to do |
|---|---|
| `.venv\Scripts\activate` says running scripts is disabled | Type `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force` first (the three lines in step 2) |
| Tickets blocked with "grounding_model: the check failed … HTTP 429" | The free tier's limit for that minute is used up. Wait about a minute, then send again; the page's **Free tier limits** box shows it |
| Tickets that were answered now go to a person | The follow-up rule (step 8). Restart the system: **Ctrl+C**, then `python -m src.api` |
| Every ticket goes to a person | The kill switch is on. Turn it off on the web page |
| The web page says the system did not answer | The system has stopped. Start it again: `python -m src.api` |
| The charts stay empty | Press **Start the live charts from zero** and wait for **Ready**. If still empty, open a chart's menu (three dots) > **Edit** and check the data source is **Prometheus** |
| "Prometheus was not found" | Do step 1 of the optional charts again |

## About the project

Every ticket goes through the same steps (`src/workflow.py`):

1. **Read** the ticket, from any of the four channels, into one shape. The customer's name is dropped.
2. **Classify** its type and urgency, with how sure the system is.
3. **Safety rules:** some tickets must always go to a person (for example data location questions, refunds and
   security issues).
4. **Search** the 29 help articles for the best 5 passages.
5. **Decide:** answer only if the system is at least 85% sure and an article fits; otherwise send it to a person.
6. **Write** the reply: an AI model picks which parts of the article answer, and the code copies them word for word.
7. **Check** the reply with five guardrails. If any check fails, or cannot run, the reply is not sent.
8. **Plan rule:** a reply from an article meant only for other plans goes to a person with the draft.

A ticket for a person comes with a plain summary, the relevant articles and, where useful, a draft reply. The labels
in the ticket files are never used to decide.

| Folder | What it holds |
|---|---|
| `src/` | The system itself, including its web page |
| `tests/` | The automatic tests |
| `evaluation/` | The run command, every run's results and metrics report, and the review sheets |
| `data/` | The tickets, the help articles, the demo tickets and the attack tickets |
| `prompts/` | The instructions given to the AI models, with their versions |
| `models/` | The two trained models |
| `scripts/` | Setup and checking scripts; each says at the top what it does |
| `monitoring/` | The Prometheus settings and the Grafana dashboard |
| `docs/` | The design (`architecture.md`), governance, decision log, known limitations, settings and a guide to every file (`code_guide.md`) |

`.env.example` lists every setting with placeholder values. Your own `.env` (with your key) and the `storage/` folder
are never uploaded.
