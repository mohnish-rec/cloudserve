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
- **Use it on the web page:** [7. Start the system](#step-7-start-the-system) ·
  [8. Send one ticket from each channel, an escalation and a guardrail ticket](#step-8-send-one-ticket-from-each-channel-an-escalation-and-a-guardrail-ticket) ·
  [9. Run a whole file of tickets, unattended](#step-9-run-a-whole-file-of-tickets-unattended) ·
  [10. Check the metrics report against the decision log](#step-10-check-the-metrics-report-against-the-decision-log) ·
  [the kill switch](#check-the-kill-switch) · [coping with problems](#check-it-copes-with-problems)
- **[Use it with commands](#use-it-with-commands):** steps 8 to 10 and the kill switch with PowerShell commands ·
  [11. Run the tests](#step-11-run-the-tests) · [the attack check](#check-it-stops-attacks-red-team-check)
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

## Use it on the web page

*Steps 7 to 10 show everything on the system's own web page. The same steps with PowerShell commands, which give the
same results, are in [Use it with commands](#use-it-with-commands).*

### Step 7. Start the system

In the project window:

```powershell
python -m src.api
```

The system keeps running in this window: **leave it open**. To stop it, press **Ctrl+C** in this window.

Then open **http://127.0.0.1:8000** in your web browser. Clicking any ticket on this page shows everything the system
decided about it and why: the reply, or the note for the person; the articles used; each guardrail's result; and its
rows in the decision log.

### Step 8. Send one ticket from each channel, an escalation and a guardrail ticket

Under **Try tickets one at a time**, press **Send the 7 demo tickets**. You should see:

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
  is blocked rather than sent unchecked. Wait a minute between batches; the **Free tier limits** box shows how much
  is left.

Under the button, **Or write your own ticket** sends any ticket you type in the same way.

### Step 9. Run a whole file of tickets, unattended

*One run processes every ticket in a file with nobody touching it, and writes a metrics report at the end.*

Under **Run a whole ticket file**, press **Choose file**, pick `C:\cloudserve_test\cloudserve\data\validation_tickets.json`
(the 80 validation tickets), press **Run**, and leave the page open. It shows the progress and, when it finishes
(about 8 minutes on Groq's free tier), the metrics report: every measure against its target, why any target was
missed, and the volume, business, technical and governance figures. The buttons above the report download it and the
results file.

### Step 10. Check the metrics report against the decision log

*This proves every ticket was logged exactly once.*

Under the metrics report, press **Check against the decision log**. It shows the run's results next to the decision
log's counts, line by line, and says **RECONCILES** when every ticket has exactly one final outcome.

### Check the kill switch

*It stops every automatic reply at once, without changing any code: while it is on, every ticket goes to a person.*

In the **Kill switch** box, press **Turn the kill switch on**, then **Send the 7 demo tickets**: every one goes to a
person with the reason "the kill switch is on". Then press **Turn the kill switch off**, and restart the system before
sending the demo tickets again. Every change is written, with the time, to `storage/kill_switch_history.txt`.

### Check it copes with problems

| Problem | How to cause it | You should see |
|---|---|---|
| No article matches | Under **Or write your own ticket**, send "What is the weather like today?" | It goes to a person, and the AI model is not called |
| The free tier's limit is reached | Send the demo tickets twice quickly | The system waits and tries again; a reply whose check cannot run goes to a person. The **Free tier limits** box shows the refusals |
| The AI service cannot be reached | Disconnect from the internet, or put a wrong key in `.env` and restart the system (put the real key back afterwards), then send the demo tickets | Nothing crashes and no unchecked reply is sent: each ticket goes to a person with the reason "model unavailable" |
| An empty ticket | Open http://127.0.0.1:8000/docs, choose **POST /tickets**, **Try it out**, and send a ticket with `"body": ""` | It goes to a person, and the system carries on |

## Use it with commands

*The same steps with PowerShell commands, for anyone who prefers them; they give the same results. The system from
step 7 must be running for step 8. Open a **second PowerShell window** and make it a project window (the three lines in
step 2).*

**Step 8 with a command:**

```powershell
python scripts/send_demo_tickets.py
```

**Step 9 with a command** (this does not need the system from step 7):

```powershell
python -m src.run_evaluation data/validation_tickets.json evaluation/results/validation_run.json
```

For another file, put it in the project's `data` folder and use its name, with a new name for the results. For
example, for the hidden evaluation set saved as `data/hidden_evaluation_tickets.json`:

```powershell
python -m src.run_evaluation data/hidden_evaluation_tickets.json evaluation/results/hidden_evaluation_run.json
```

Leave it until it finishes, with the window open. It writes, in `evaluation/results`, the results file (for example
`validation_run.json`) and the metrics report (for example `validation_run_metrics.md`), and a row for every decision in
the decision log, `storage/decisions.db`. (The same run can also be started as
`python -m evaluation.harness --input data/validation_tickets.json --output evaluation/results/`.)

**Step 10 with a command:** open the metrics report; under **Governance**, the line **Decisions logged** says, for
example, `356 rows; 80 final outcomes for 80 tickets -> reconciles`. Then count the same things from the decision log:

```powershell
python scripts/check_decision_log.py
```

It checks the most recent run. You should see the same numbers as in the report, and **Result: RECONCILES**.

**The kill switch with commands:** `New-Item storage\kill_switch -ItemType File -Force` turns it on, and
`Remove-Item storage\kill_switch` turns it off.

### Step 11. Run the tests

*They need no API key and make no calls to the AI models.* In the project window, with the kill switch off:

```powershell
python -m pytest tests/ -v
```

The last line should read `382 passed, 1 xfailed`. The one `xfailed` ("expected to fail") is deliberate: a known
limitation kept visible as a test (`docs/known_limitations.md`, number 5). It is not a failure.

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
