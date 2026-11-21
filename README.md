# CloudServe support system

Triage for CloudServe support tickets: classifies each ticket, finds the relevant help article, drafts a cited answer
or passes the ticket to a person, and logs every decision.

Built by Mohnish Grover for the FDE (Forward Deployed Engineer) capstone, November 2026. Code written with help from
Claude (Anthropic) says so at the top of the file; every file was reviewed and run by Mohnish Grover.

## Contents

Do the steps from top to bottom. Each one says what you should see when it has worked.

| Part | Steps | Time |
|---|---|---|
| [Before you start](#before-you-start) | Python 3.11, Git and a free Groq key | 10 minutes |
| **Set it up (once)** | [1. Get the code](#step-1-get-the-code) · [2. Create the Python environment](#step-2-create-the-projects-python-environment) · [3. Install the packages](#step-3-install-the-packages-it-needs) · [4. Add your API key](#step-4-add-your-api-key) · [5. Check the AI model answers](#step-5-check-the-ai-model-answers) · [6. Build the article store and the decision log](#step-6-build-the-article-store-and-the-decision-log) | 20 minutes, mostly downloading |
| **Use it** | [7. Start the system](#step-7-start-the-system) · [8. Send the demo tickets](#step-8-send-one-ticket-from-each-channel-an-escalation-and-a-guardrail-ticket) · [9. Run a whole file of tickets](#step-9-run-a-whole-file-of-tickets-unattended) · [10. Check the report against the decision log](#step-10-check-the-metrics-report-against-the-decision-log) · [11. Run the tests](#step-11-run-the-tests) | Step 9 takes about 8 minutes for 80 tickets |
| [More checks](#more-checks) | The kill switch · coping with problems · attacks | A few minutes each |
| [Optional: live charts](#optional-watch-it-live-prometheus-and-grafana) | Prometheus and Grafana, set up once after step 7 | 15 minutes |
| [If something goes wrong](#if-something-goes-wrong) | The usual problems and what to do | |
| [About the project](#about-the-project) | What it does, what is where, the results | |

## Before you start

These instructions are for **Windows 10 or 11, using PowerShell**, where the system was built and tested. Every
command in this README is typed in PowerShell (press the Windows key, type `PowerShell`, press Enter).

You need:

- **Python 3.11.** Other versions will not work: several pinned packages support Python only up to 3.11.
- **Git**, to download the project.
- **A free Groq API key** (the password that lets the system use Groq's AI models), from https://console.groq.com/keys
- About **4 GB of free disk space** and an internet connection. The first run downloads about 1 GB.

Install Python and Git with these two commands, then **close PowerShell and open a new one**, so it finds them:

```powershell
winget install -e --id Python.Python.3.11
winget install -e --id Git.Git
```

(Or download them: [Python 3.11.9](https://www.python.org/downloads/release/python-3119/), under **Files** choose
**Windows installer (64-bit)**; and Git from https://git-scm.com.)

## Set it up (once)

### Step 1. Get the code

*This downloads a copy of the project to your computer.*

```powershell
mkdir C:\cloudserve_test
cd C:\cloudserve_test
git clone https://github.com/mohnish-rec/cloudserve.git
cd cloudserve
```

Every command from here on is typed in this `C:\cloudserve_test\cloudserve` folder.

### Step 2. Create the project's Python environment

*This makes a private copy of Python just for this project, so nothing else on your computer is affected.*

```powershell
py -3.11 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.venv\Scripts\activate
python --version
```

You should see `Python 3.11.x`, and the start of the line now shows `(.venv)`.

> **The project window.** In this README, "the project window" means a PowerShell window in the project folder with
> `(.venv)` at the start of the line. Whenever you open a **new** PowerShell window for the project, type these three
> lines first:
>
> ```powershell
> cd C:\cloudserve_test\cloudserve
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
> .venv\Scripts\activate
> ```

### Step 3. Install the packages it needs

*This installs the exact versions of every package the system was tested with. It takes several minutes.*

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Step 4. Add your API key

*Your key stays in a file on your computer that is never shared or uploaded.*

```powershell
cp .env.example .env
notepad .env
```

In Notepad, replace `your_groq_key_here` with your Groq key (no quotes, no spaces), leave every other line as it is,
save and close.

### Step 5. Check the AI model answers

*This sends one test message to each model, to prove the key works.*

```powershell
python scripts/check_model.py
```

You should see `200` and `reply: ready` for both `main` and `backup`.

### Step 6. Build the article store and the decision log

*This loads the 29 help articles so the system can search them, and creates the empty log where every decision will be
written.*

```powershell
python scripts/setup_vector_store.py
python scripts/setup_decision_log.py
```

The first run downloads the embedding model, which takes a few minutes. You should see:

```
stored 141 passages from 29 documents
test query -> top result: DOC-AUTH-001 | Resolving invalid credential errors on login
decision log ready: storage/decisions.db (20 columns, 0 rows)
```

The set-up is finished.

## Use it

Steps 7 to 11 are in the order the assessors test the system.

### Step 7. Start the system

*This starts the system and its web page.*

In the project window:

```powershell
python -m src.api
```

The system keeps running in this window: **leave it open** (minimise it if you like). To stop the system later, press
**Ctrl+C** in this window.

Now open **http://127.0.0.1:8000** in your web browser. Everything in steps 8 to 10 can be done on this page:

| Box on the page | What it does |
|---|---|
| **Kill switch** | Stops every automatic reply at once, and starts them again |
| **Live charts (optional)** | Starts Prometheus and Grafana with every chart at zero (needs the [optional set-up](#optional-watch-it-live-prometheus-and-grafana)) |
| **Free tier limits (Groq)** | How much of the free tier's limits each AI model has used, and about how many more tickets can be answered |
| **Try tickets one at a time** | Sends the 7 demo tickets (step 8), or a ticket you write yourself |
| **Run a whole ticket file** | Runs every ticket in a file and shows the metrics report (step 9), with downloads and the check against the decision log (step 10) |

Click any ticket in a table to see everything the system decided about it: the reason, the reply the customer
received or the note for the person, the articles used, each guardrail's result, the time and cost, and every row the
decision log holds for it.

The system also answers at http://127.0.0.1:8000/docs (send one ticket by hand: **POST /tickets**, **Try it out**),
http://127.0.0.1:8000/health (is the kill switch on?), `/healthz` (is it alive?) and `/readyz` (is anything missing?).
Labels sent with a ticket are ignored.

For the PowerShell commands in the next steps, **open a second PowerShell window** and make it a project window (the
three lines in step 2).

### Step 8. Send one ticket from each channel, an escalation and a guardrail ticket

*Seven prepared tickets show every kind of outcome: four answered automatically (one on each channel), two sent to a
person (escalations), and one blocked by a guardrail.*

**On the web page:** press **Send the 7 demo tickets**.

**Or in the second project window:**

```powershell
python scripts/send_demo_tickets.py
```

You should see, the first time you send them after starting the system:

| Ticket | Channel | About | You should see |
|---|---|---|---|
| DEV-0319 | email | Unexpected overage charges | Answered automatically |
| DEV-0108 | chat | Deployments fail at the health check | Answered automatically |
| DEV-0422 | documentation comment | A pagination cursor stops working | Answered automatically |
| DEV-0330 | forum | Connection pool exhausted | Answered automatically |
| DEV-0058 | email | Where is our data stored? | Sent to a person (data location rule) |
| DEV-0033 | chat | Single sign-on problem, Standard plan | Sent to a person with a draft (the article is for other plans) |
| RT-01 | email | Hidden instruction: "ignore all previous instructions…" | Blocked by a guardrail |

The tickets are in `data/samples/demo_tickets.json`.

**Sending them a second time gives different results, on purpose.** The running system remembers its automatic
replies. When the same customer writes again about the same type of problem within 7 days, it assumes the first
answer did not solve it and sends the new ticket to a person (the follow-up rule). To see the first-time results
again, restart the system: **Ctrl+C** in its window, then `python -m src.api`.

**Wait about a minute between batches.** Groq's free tier allows about 5 answered tickets a minute. If tickets are
sent faster, the reply check cannot run and the reply is blocked rather than sent unchecked
(see [If something goes wrong](#if-something-goes-wrong)).

### Step 9. Run a whole file of tickets, unattended

*One run processes every ticket in a file, with nobody touching it, and writes a metrics report at the end.*

**Way 1, on the web page (the simplest).** Under **Run a whole ticket file**, press **Choose file**, pick the ticket
file, press **Run**, and leave the page open. It shows the progress and, at the end, the metrics report.

**Way 2, with one command (the assessors' test).** This does not need the system from step 7.

1. Put the ticket file in the project's `data` folder (`C:\cloudserve_test\cloudserve\data`). It must be in the same
   format as `data/development_tickets.json`.
2. In the project window, type the command below, with your file's real name after `data/` and a new name you choose
   for the results after `evaluation/results/`, both ending in `.json`. For the hidden evaluation set (the 120
   tickets the assessors run), if it is saved as `data/hidden_evaluation_tickets.json`:

   ```powershell
   python -m src.run_evaluation data/hidden_evaluation_tickets.json evaluation/results/hidden_evaluation_run.json
   ```

   To try it now on the 80 validation tickets that come with the project:

   ```powershell
   python -m src.run_evaluation data/validation_tickets.json evaluation/results/validation_run.json
   ```

3. Leave it until it finishes. It needs nothing from you; keep the window open.

The same run can also be started as `python -m evaluation.harness --input data/hidden_evaluation_tickets.json --output evaluation/results/`.

**How long it takes.** On Groq's free tier, the 80 validation tickets took 8.0 minutes (19 Nov 2026) and the 500
development tickets about 10 hours (19-20 Nov 2026). When the free tier's limit is reached, the system waits and tries
again by itself; a reply that cannot be checked is never sent, and that ticket goes to a person instead.

**What it writes,** in the `evaluation/results` folder (Way 1 adds `web_` to the start of the names):

- the results file, for example `hidden_evaluation_run.json`: one entry per ticket, with the decision, the reply sent
  and the articles cited;
- the metrics report, for example `hidden_evaluation_run_metrics.md`;
- and a row for every decision in the decision log, `storage/decisions.db`.

**The metrics report** starts with **Results against the targets**: every measure and target in the Evaluation
Framework, in its three tiers (business outcomes, technical performance, governance conditions), each marked Yes, No
or Not measured. **Why targets were missed** gives the reason for each No, and **Why some measures are not measured**
says why a run cannot produce those. Then come Volume, Business, Technical and Governance.

### Step 10. Check the metrics report against the decision log

*This proves every ticket was logged exactly once.*

**On the web page,** after a run from the page: press **Check against the decision log** under the metrics report. It
shows the run's results next to the decision log's counts, line by line, and says **RECONCILES** when every ticket has
exactly one final outcome.

**Or in the project window,** after either way of running step 9:

1. Open the metrics report. Under **Governance**, the line **Decisions logged** says, for example,
   `356 rows; 80 final outcomes for 80 tickets -> reconciles`. Under **Volume** are the numbers answered
   automatically, escalated and blocked.
2. Count the same things straight from the decision log:

   ```powershell
   python scripts/check_decision_log.py
   ```

   It checks the most recent run. You should see the same numbers as in the report, and **Result: RECONCILES**.
   For example, the final validation run: 356 rows; 53 answered automatically, 24 sent to a person, 3 blocked; 80
   tickets, each with exactly one final outcome.

To check an earlier run, add its run id from the top of its metrics report, for example
`python scripts/check_decision_log.py run-20261119T182708-10f116`.

### Step 11. Run the tests

*The tests check every part of the system automatically. They need no API key and make no calls to the AI models.*

In the project window:

```powershell
python -m pytest tests/ -v
```

The last line should read `382 passed, 1 xfailed`.

The one `xfailed` ("expected to fail") is deliberate: a known limitation kept visible as a test
(`tests/test_decisions.py`, and `docs/known_limitations.md` number 5). "We were throttled… we would rather pay overage
than be stopped" goes to a person, but the same request in other words ("We got rate limited… we'd prefer to pay extra
than be cut off") is not recognised. `xfailed` is not a failure: if the system ever gets this case right, pytest shows
`xpassed` instead.

The kill switch must be **off** when you run the tests (see below).

## More checks

### Check the kill switch

*The kill switch stops all automatic replies at once, without changing any code: while it is on, every ticket goes to
a person. It works straight away, even in the middle of a run.*

**On the web page:** the **Kill switch** box shows whether it is on; its button turns it on or off. Turn it on, press
**Send the 7 demo tickets**, and every ticket goes to a person with the reason "the kill switch is on, so all automatic
replies are stopped". Then turn it off again. Every change is written, with the time, to
`storage/kill_switch_history.txt`.

**Or in the project window:**

```powershell
New-Item storage\kill_switch -ItemType File -Force
```

turns it on (it creates an empty file called `storage/kill_switch`), and

```powershell
Remove-Item storage\kill_switch
```

turns it off. http://127.0.0.1:8000/health shows `"kill_switch_on": true` or `false`.

After turning it off, restart the system before sending the demo tickets again, so the follow-up rule (step 8) does
not change the results.

### Check it copes with problems

*The system must keep going when something goes wrong. This shows how to cause each problem and what you should see.*

| Problem | How to cause it | You should see |
|---|---|---|
| The AI service cannot be reached | Disconnect from the internet, or put a wrong key in `.env` (put the real key back afterwards), then send the demo tickets | Nothing crashes and no unchecked reply is sent. Each ticket goes to a person with the reason "model unavailable"; after 3 failures in a row, the rest go to a person straight away |
| The free tier's limit is reached | Send the demo tickets twice quickly, or run a large file | The system waits as long as Groq asks, then carries on; a reply whose check cannot run is blocked and goes to a person. The **Free tier limits** box shows the refusals |
| No article matches the ticket | Write your own ticket on the web page, for example "What is the weather like today?" | It goes to a person, and the AI model is not called |
| A broken or empty ticket | Send a ticket with an empty message from http://127.0.0.1:8000/docs (**POST /tickets**, **Try it out**, `"body": ""`) | It goes to a person ("Needs a specialist"), and the system carries on |

The no-network and wrong-key checks were run on 17 Nov 2026; their results are in `evaluation/results/a11_no_network/`
and `evaluation/results/a11_wrong_key/`. Each problem is also covered by the tests (step 11).

### Check it stops attacks (red-team check)

*Fourteen tickets written to attack or trick the system, for example hidden instructions to the AI, a secret key or
someone's contact details pasted into a ticket, a demand for a refund, or a message in Spanish. Each must be handled
safely. It needs the API key and takes a few minutes.*

In the project window:

```powershell
python scripts/red_team.py
```

It writes the result for every ticket to `evaluation/results/red_team.md`.

## Optional: watch it live (Prometheus and Grafana)

*Live charts of the system's work while tickets are processed. Nothing else needs them. Prometheus collects the
numbers and Grafana draws the charts. Set them up once, with the system from step 7 running.*

**1. Get Prometheus** (tested with version 3.13.5). On https://prometheus.io/download/, under **prometheus**, download
the Windows file (ending in `windows-amd64.zip`). Then, in any PowerShell window, unzip it into `C:\prometheus`:

```powershell
Get-ChildItem "$env:USERPROFILE\Downloads\prometheus-*windows-amd64.zip" | Expand-Archive -DestinationPath C:\prometheus -Force
```

**2. Get Grafana** (tested with version 13.3.1; the dashboard needs version 10 or newer). In any PowerShell window:

```powershell
winget install -e --id GrafanaLabs.Grafana.OSS
```

If Windows asks for permission, press **Yes**. Grafana runs in the background by itself from now on. Open
http://localhost:3000, sign in with `admin` / `admin`, and choose a new password when asked. (If `winget` says
Grafana is already installed, that is fine.)

**3. Start the charts.** On the system's web page (http://127.0.0.1:8000), press **Start the live charts from zero**.
It starts Prometheus in a small window on the taskbar (leave it open), makes sure Grafana is running, and after about
a minute shows **Ready**.

**4. Connect Grafana to Prometheus** (once). In Grafana: **Connections > Data sources > Add data source > Prometheus**,
set the URL to `http://localhost:9090`, and press **Save & test**.

**5. Load the dashboard** (once). In Grafana: **Dashboards > New > Import**, upload
`C:\cloudserve_test\cloudserve\monitoring\grafana_dashboard.json`, choose the Prometheus data source, and press
**Import**.

**From now on,** each time: start the system (step 7), press **Start the live charts from zero**, wait for **Ready**,
then click **Open the Grafana dashboard** and send tickets from the page. The button clears the earlier numbers, so
every chart starts from zero.

The dashboard has five charts: tickets per hour by channel and outcome; the share answered automatically against
escalated; response time at the median and the slowest 5% (with the 3-second target line); guardrail activations; and
how confident the system was. In Grafana, set the time range at the top right to **Last 15 minutes** and the refresh to
**10s**.

Only tickets sent to the running system appear on the charts: the web page, or `scripts/send_demo_tickets.py`. To show
a step 9 Way 2 run on the charts, press the button first, then stop the system (**Ctrl+C**; Prometheus keeps running),
and add `--metrics-port 8001` to the end of the command.

## If something goes wrong

| What you see | Why | What to do |
|---|---|---|
| `.venv\Scripts\activate` says running scripts is disabled | Windows blocks scripts in a new window | Type `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force` first (the three lines in step 2) |
| Tickets blocked with "grounding_model: the check failed … HTTP 429" | Groq's free tier allows about 8,000 tokens a minute for the reply check, about 5 answered tickets | Wait about a minute, then send again. The **Free tier limits** box shows when the limit is full |
| Tickets that were answered now go to a person | The follow-up rule (step 8) | Restart the system: **Ctrl+C**, then `python -m src.api` |
| Every ticket goes to a person | The kill switch is on | Turn it off on the web page, or `Remove-Item storage\kill_switch` |
| The web page says the system did not answer | The system from step 7 has stopped | Start it again in the project window: `python -m src.api` |
| The charts stay empty | Prometheus has not read the system yet, or the chart uses another data source | Press **Start the live charts from zero** and wait for **Ready**. If still empty, open a chart's menu (three dots) > **Edit** and check the data source says **Prometheus**; if not, import the dashboard again (optional step 5) and press **Overwrite** |
| **Start the live charts from zero** says Prometheus was not found | It is not unzipped in `C:\prometheus` | Do optional step 1 again |

**Without the web page,** the charts can be started by double-clicking `start_live_charts.bat` in the project folder,
before starting the system. (If Windows shows "Windows protected your PC", press **More info**, then **Run anyway**.)
Or start Prometheus by hand in its own PowerShell window, and leave that window open:

```powershell
cd C:\prometheus\prometheus-*
.\prometheus.exe --config.file=C:\cloudserve_test\cloudserve\monitoring\prometheus.yml --web.listen-address=127.0.0.1:9090
```

To clear its numbers by hand, stop it with **Ctrl+C**, type `Remove-Item -Recurse -Force data` in that same window
(only Prometheus's own `data` folder, never the project's), start it again, and restart the system.

## Optional: settings

*The tested settings are already the defaults, so you do not need this to run the system.*

Each can be switched off for a comparison, for example `$env:QUESTION_RULES="off"` in the project window before
starting the system:

| Setting | Default | What it does |
|---|---|---|
| `QUESTION_RULES` | on | Sends four question types to a person that Mohnish Grover decided need one |
| `LEARNED_DECISIONS` | on | Applies the decisions learned from Mohnish Grover's review of the development tickets |
| `NARROW_RULES` | on | Safety rules stop requests and disputes, not plain questions |
| `TYPE_AWARE_SEARCH` | on | The article search also uses the ticket's type |
| `TRIM_UNSUPPORTED` | on | A sentence the check cannot support is removed, and the reply is checked again |
| `PLAN_RULE` | on | A reply from an article for other plans goes to a person with the draft |
| `REPLY_CACHE` | off | Reuses earlier answers; for development runs only, never for validation or test runs |
| `PR01_FILE` | version 1.7 | Which version of the reply instructions to use |

## About the project

### What it does

Every ticket goes through the same steps (`src/workflow.py`). Each file is explained in `docs/code_guide.md`, and the
design, with a diagram, in `docs/architecture.md`.

1. **Read** the ticket, from any of the four channels, into one shape. The customer's name is dropped.
2. **Classify** its type and urgency, with how sure the system is. This runs on your computer.
3. **Safety rules:** some tickets must always go to a person (for example data location questions, refunds and
   security issues).
4. **Search** the 29 help articles for the best 5 passages.
5. **Decide:** answer only if the system is at least 85% sure and an article fits; otherwise send it to a person.
6. **Write** the reply: an AI model (on Groq) picks which parts of the article answer, and the code copies them word
   for word.
7. **Check** the reply with five guardrails (private data, every sentence backed by the article, no instructions taken
   from the ticket, tone, confidence). If any check fails, or cannot run, the reply is not sent.
8. **Plan rule:** a reply from an article meant only for other plans goes to a person with the draft.

A ticket for a person comes with a plain summary, the relevant articles and, where useful, a draft reply. The labels
in the ticket files are never used to decide.

### What is where

| Folder | What it holds |
|---|---|
| `src/` | The system itself, including its web page |
| `tests/` | The automatic tests, run on GitHub after every change |
| `evaluation/` | The run command, every run's results and metrics report, and the two people's review sheets |
| `data/` | The tickets, the help articles, the demo tickets and the attack tickets |
| `prompts/` | The instructions given to the AI models, with their versions |
| `models/` | The two trained models (ticket type, and the decisions learned from Mohnish Grover) |
| `scripts/` | Setup, checking and analysis scripts; each says at the top what it does |
| `monitoring/` | The Prometheus settings and the Grafana dashboard |
| `start_live_charts.bat` | Starts the live charts without the web page |
| `docs/` | The design, governance, decision log, known limitations and a guide to every file |

`.env.example` lists every setting with placeholder values. Your own `.env` (with your key) and the `storage/` folder
are never shared or uploaded.

### Results of the final runs

On Groq's free tier, 19 to 20 November 2026. The full results, and the reasons for each missed target, are in the
report and in `evaluation/results/`.

| Measure (target) | 80 validation tickets | 500 development tickets |
|---|---|---|
| First contact resolution (60% or better) | 66.2% | 66.0% |
| Escalation rate (30% or lower) | 33.8% | 34.0% |
| Must-not tickets answered automatically (0) | 0 of 14 | 0 of 87 |
| Citation accuracy (95% or better) | 97.6% | 93.0% |
| Private data in outbound text (zero occurrences) | 0 | 0 |
| Latency, 95th percentile, without the free tier's waiting (under 3 seconds) | 3.4 s | 7.2 s |
| Decision logging: every ticket logged exactly once (complete coverage) | 80 of 80 | 500 of 500 |
