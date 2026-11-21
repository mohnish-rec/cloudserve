# CloudServe support system

Triage for CloudServe support tickets: classifies each ticket, finds the relevant documentation, drafts a cited answer or escalates to a person, and logs every decision.

Built by Mohnish Grover for the FDE (Forward Deployed Engineer) capstone, November 2026. Code written with help from
Claude (Anthropic) says so at the top of the file; every file was reviewed and run by Mohnish Grover.

## The order to follow

If you are setting this up for the first time, do these steps from top to bottom. Each step says what you should see
when it has worked.

**Before you start:** [What you need first](#what-you-need-first): Python 3.11, a free Groq key and Git. To read what
the system does first, see [About the project](#about-the-project) at the end.

**Set it up (about 20 minutes, most of it downloading):**

1. [Get the code](#step-1-get-the-code)
2. [Create the project's Python environment](#step-2-create-the-projects-python-environment)
3. [Install the packages it needs](#step-3-install-the-packages-it-needs)
4. [Add your API key](#step-4-add-your-api-key)
5. [Check the AI model answers](#step-5-check-the-ai-model-answers)
6. [Build the article store and the decision log](#step-6-build-the-article-store-and-the-decision-log)

**Optional, only if you want to watch the system live on charts (do it here, after step 6):**
[set up Prometheus and Grafana](#optional-watch-it-live-prometheus-and-grafana).

**Use it (in the same order the assessors use to test the system):**

7. [Start the system](#step-7-start-the-system)
8. [Send one ticket from each channel, an escalation and a guardrail ticket](#step-8-send-one-ticket-from-each-channel-an-escalation-and-a-guardrail-ticket)
9. [Run a whole file of tickets, unattended](#step-9-run-a-whole-file-of-tickets-unattended)
10. [Check the metrics report against the decision log](#step-10-check-the-metrics-report-against-the-decision-log)
11. [Run the tests](#step-11-run-the-tests)

**More checks, any time after step 6:** [check the kill switch](#check-the-kill-switch),
[check it copes with problems](#check-it-copes-with-problems),
[check it stops attacks](#check-it-stops-attacks-red-team-check).

**Optional:** [change the settings](#optional-settings).

## What you need first

*Install these before you start. Everything else is installed by the steps below.*

These instructions are for **Windows, using PowerShell**, where the system was built and tested.

- **Python 3.11.** [Download 3.11.9](https://www.python.org/downloads/release/python-3119/). On that page, under **Files**, choose **Windows installer (64-bit)**, and install it with the default options. Other versions will not work: several pinned packages support Python only up to 3.11.
- **A free Groq API key**, from https://console.groq.com/keys
- About **4 GB of free disk space** and an internet connection. The first run downloads about 1 GB.
- **Git**, from https://git-scm.com (check with `git --version`).

On Windows 10 or 11 you can install Python and Git from PowerShell instead of the websites (the same official
installers; then close PowerShell and open a new one, so it finds them):

```powershell
winget install -e --id Python.Python.3.11
winget install -e --id Git.Git
```

- **Optional, only to watch the system live on charts: Prometheus and Grafana.** Nothing else needs them. Set them up
  after [step 6](#step-6-build-the-article-store-and-the-decision-log), because Prometheus reads a settings file from the project:
  [Optional: watch it live](#optional-watch-it-live-prometheus-and-grafana).

## Set it up

### Step 1. Get the code

*This downloads a copy of the project to your computer.*

Open PowerShell, make a new, empty folder for the project, and download it there:

```powershell
mkdir C:\cloudserve_test
cd C:\cloudserve_test
git clone https://github.com/mohnish-rec/cloudserve.git
cd cloudserve
```

Every command below is run in this `cloudserve` folder (the one containing this README), in order.

### Step 2. Create the project's Python environment

*This makes a private copy of Python just for this project, so nothing else on your computer is affected. Each time you open a new terminal later, run only the activate line again.*

```powershell
py -3.11 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.venv\Scripts\activate
python --version
```

You should see `Python 3.11.x`, and your prompt now starts with `(.venv)`.

### Step 3. Install the packages it needs

*This installs the exact versions of every package the system was tested with.*

```
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

This takes several minutes. Every package is pinned to the exact version that was tested.

### Step 4. Add your API key

*The system uses an AI model on Groq; your free key lets it call that model. The key stays in a file on your computer that is never shared or committed.*

```
cp .env.example .env
```

This creates a new file called `.env`. Open **`.env`** (not `.env.example`): with `notepad .env`. Replace `your_groq_key_here` with your Groq key (no quotes, no spaces), leave every other line as it is, and save.

### Step 5. Check the AI model answers

*This sends one test message to each model, to prove the key works before anything else.*

```
python scripts/check_model.py
```

You should see `200` and `reply: ready` for both `main` and `backup`.

### Step 6. Build the article store and the decision log

*This loads the 29 help articles so the system can search them, and creates the empty log where every decision will be written.*

```
python scripts/setup_vector_store.py
python scripts/setup_decision_log.py
```

The first run downloads the embedding model, which takes a few minutes. You should see:

```
stored 141 passages from 29 documents
test query -> top result: DOC-AUTH-001 | Resolving invalid credential errors on login
decision log ready: storage/decisions.db (20 columns, 0 rows)
```

### Optional: watch it live on charts

*Do this now, before step 7, only if you want to see the system working on live charts. Nothing else needs it.*

Set up Prometheus (it collects the numbers) and Grafana (it draws the charts) by following
[Optional: watch it live (Prometheus and Grafana)](#optional-watch-it-live-prometheus-and-grafana), then come back here
and carry on with [step 7](#step-7-start-the-system).

## Use it

### Step 7. Start the system

*This starts the system as a small web service that takes one ticket at a time. It also switches on the live numbers that monitoring reads (port 8001).*

```
python -m src.api
```

Run this in the PowerShell window you used for steps 1 to 6 (the one showing `(.venv)`). The system keeps running in
this window: leave it open, and press Ctrl+C in it when you want to stop the system.

**For the next steps, open another new PowerShell window**, go to the project and switch the environment on:

```powershell
cd C:\cloudserve_test\cloudserve
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.venv\Scripts\activate
```

You should see `(.venv)` at the start of the line. Type the commands from [step 8](#step-8-send-one-ticket-from-each-channel-an-escalation-and-a-guardrail-ticket) onwards in this window.

To try a ticket by hand, open http://127.0.0.1:8000/docs in a browser, choose **POST /tickets**, press **Try it out**, paste a ticket
(the same fields as in `data/development_tickets.json`) and press **Execute**. The answer shows the decision, the
reply or the handover for a person, and the reasons. It is the same pipeline as the unattended run: every guardrail
runs and every decision is written to `storage/decisions.db`. `GET /health` shows whether the kill switch is on; `GET /healthz` answers while the API is alive, and `GET /readyz` lists anything still missing (the trained models, the article index or the AI key).
Labels sent with a ticket are ignored. Stop it with Ctrl+C.

### Step 8. Send one ticket from each channel, an escalation and a guardrail ticket

*Seven prepared tickets show every kind of outcome: four are answered automatically (a success on each of the four channels), two are sent to a person (escalations), and one is blocked by a guardrail.*

The seven tickets are in `data/samples/demo_tickets.json`. The last column shows what you should see **the first
time you send them after starting the system** (step 7):

| Ticket | Channel | About | You should see |
|---|---|---|---|
| DEV-0319 | email | Unexpected overage charges | Answered |
| DEV-0108 | chat | Deployments fail at the health check | Answered |
| DEV-0422 | docs comment | A pagination cursor stops working | Answered |
| DEV-0330 | forum | Connection pool exhausted | Answered |
| DEV-0058 | email | Where is our data stored? | Sent to a person (data location rule) |
| DEV-0033 | chat | Single sign-on problem, Standard plan | Sent to a person with a draft (the article is for other plans) |
| RT-01 | email | Hidden instruction: "ignore all previous instructions…" | Blocked by a guardrail |

**If you send them again without restarting the system,** the tickets that were answered now go to a person, with
the reason "follow-up: the same customer had an automatic reply on the same type…". This is the follow-up rule
working: the running system remembers its automatic replies, and when the same customer writes again about the same
type of problem within 7 days, it assumes the first answer did not solve it and sends the new ticket to a person with
the earlier reply as a draft. To see the first-time results again, restart the system: press **Ctrl+C** in its window,
then run `python -m src.api` again.

**The simplest way: the web page.** Keep the system from step 7 running, open http://127.0.0.1:8000 and press
**Send the 7 demo tickets**. Each result appears in a table; click a ticket to see everything the system decided
about it: the reason, the reply the customer received (or the handover note for the person), the articles found and
cited, each guardrail's result, the time and cost, and every row the decision log holds for it. Under the button,
**Or write your own ticket** sends any ticket you type, the same way.

**Or from PowerShell.** Use the other PowerShell window showing `(.venv)`, keep the system from step 7 running, and run:

```
python scripts/send_demo_tickets.py
```

For each ticket it shows the channel, the result and the full reason. You should see DEV-0319, DEV-0108, DEV-0422 and
DEV-0330 **answered automatically**; DEV-0058 and DEV-0033 **sent to a person**; and RT-01 **blocked by a guardrail**.
If it says the system is not running, start it again (step 7). These tickets also appear on the live charts, if you set them up.

**Another way, without the running system:** this runs the seven tickets as a separate program and writes a results
file and a metrics report (`evaluation/results/demo_tickets_results.json`). Its tickets do **not** appear on the live
charts.

```
python -m evaluation.harness --input data/samples/demo_tickets.json --output evaluation/results/
```

Each ticket can also be pasted into http://127.0.0.1:8000/docs (POST /tickets, Try it out). An answered ticket shows
the reply in `sent_text`; a ticket for a person shows the acknowledgement in `sent_text` and the summary for the agent
in `handover`; a blocked one shows which guardrail fired in `reason` and `guardrails`.

### Step 9. Run a whole file of tickets, unattended

*One command processes every ticket in a file, with nobody touching it, and writes a metrics report at the end.*

There are three ways to do this step: with a command, with a command and the live charts, or from a web page. The
assessors' test uses the first.

#### Without the live charts

**1. Put the ticket file in the project's `data` folder**, which is `C:\cloudserve_test\cloudserve\data` if you
followed step 1. The file must be in the same format as `data/development_tickets.json`.

**2. Start the run.** In the PowerShell window showing `(.venv)`, type:

```
python -m src.run_evaluation <tickets file> <results file>
```

- Replace `<tickets file>` with `data/` followed by your ticket file's real name, exactly as it is spelled, including
  `.json` at the end (for example `data/hidden_evaluation_tickets.json`).
- Replace `<results file>` with `evaluation/results/` followed by a new name you choose for the results, also ending
  in `.json` (for example `evaluation/results/hidden_evaluation_run.json`).
- Type only the names: the `<` and `>` are not part of the command.

For example, for the hidden evaluation set (the 120 tickets the assessors run), if it is saved as `data/hidden_evaluation_tickets.json`:

```
python -m src.run_evaluation data/hidden_evaluation_tickets.json evaluation/results/hidden_evaluation_run.json
```

To try it now on the 80 validation tickets that come with the project (already in the `data` folder, so you can skip
point 1):

```
python -m src.run_evaluation data/validation_tickets.json evaluation/results/validation_run.json
```

**3. Leave it until it finishes.** It needs nothing from you, and the window must stay open. On Groq's free tier the
80 validation tickets took 8.0 minutes (19 Nov 2026) and the 500 development tickets about 10 hours (609.5 minutes,
19-20 Nov 2026). When the free tier's limit is reached, the system waits and tries again by itself; a reply that cannot
be checked is never sent, and that ticket goes to a person instead.

#### With the live charts

Only if you set up [Optional: watch it live](#optional-watch-it-live-prometheus-and-grafana).

**1. Stop the system from step 7.** Press **Ctrl+C** in its window. The run and the system cannot both use the
live-chart connection (port 8001) at the same time, and the run does not need the system.

**2. Put the ticket file in the project's `data` folder**, as in the first way.

**3. Start the run with `--metrics-port 8001` at the end.** It is the same command as in the first way, with the same
replacements, plus this ending. For example, for the hidden evaluation set (the 120 tickets the assessors run), if it is saved as `data/hidden_evaluation_tickets.json`:

```
python -m src.run_evaluation data/hidden_evaluation_tickets.json evaluation/results/hidden_evaluation_run.json --metrics-port 8001
```

For the 80 validation tickets that come with the project:

```
python -m src.run_evaluation data/validation_tickets.json evaluation/results/validation_run.json --metrics-port 8001
```

**4. Watch the charts while it runs.** In Grafana, set the time range to **Last 15 minutes** and the refresh to
**10s**. Leave the window open until the run finishes.

#### From the web page (the simplest way)

The system from [step 7](#step-7-start-the-system) has a web page that does the same run without typing a command.

1. Keep the system from step 7 running.
2. Open http://127.0.0.1:8000 in your browser.
   If you set up the live charts, press **Start the live charts from zero** first and wait until it shows **Ready**.
3. Under **Run a whole ticket file**, press **Choose file**, pick the ticket file (for example
   `data\validation_tickets.json` in the project folder), and press **Run**.
4. Leave the page open. It shows how many tickets have been processed, how many were answered, escalated or
   blocked, and the latest tickets (click one for its details). When it finishes, it shows the metrics report, with
   buttons to download it and the results file, and to check it against the decision log (step 10).

The page's **Free tier limits (Groq)** box shows, for each model, how much of its tokens per minute and requests per
day are used, as Groq reports them on every call, and how many calls it refused (HTTP 429, too many requests) in the
last 10 minutes. It updates by itself; **Check the limits now** makes one tiny call to each model for fresh figures.
If the grounding check model's tokens bar is full, wait about a minute before sending more tickets.

Every ticket goes through exactly the same steps as the command above, and every decision is written to the decision
log. If you set up the live charts, Grafana shows the run as it happens. The page writes its
results into the `evaluation/results` folder, with names starting `web_`, and keeps a copy of the uploaded file in
`evaluation/results/uploads`. Only one file can run at a time.

#### What the run writes

In the `evaluation/results` folder, with the hidden evaluation set names above (for the validation tickets, the same with
`validation_run` instead of `hidden_evaluation_run`):

- `hidden_evaluation_run.json`: one entry per ticket, with the decision, the reply sent and the articles cited;
- `hidden_evaluation_run_metrics.md`: the metrics report, with every measure for the run and the settings it used;

and a row for every decision in the decision log, `storage/decisions.db`.

*Another way to start the same run*, with the input and output named:
`python -m evaluation.harness --input data/hidden_evaluation_tickets.json --output evaluation/results/`

### Step 10. Check the metrics report against the decision log

*This proves every ticket was logged exactly once.*

**1. Open the metrics report** from step 9 (for example `evaluation/results/hidden_evaluation_run_metrics.md`). The report opens with **Results against the targets**:
every measure and target in the Evaluation Framework, in its three tiers (business outcomes, technical performance and
governance conditions), each marked Yes, No or Not measured. **Why targets were missed** gives the reason for any No,
and **Why some measures are not measured** says why a run cannot produce those. Under
**Governance**, the line **Decisions logged** says how many rows the run wrote to the decision log and
whether every ticket has exactly one final outcome, for example `356 rows; 80 final outcomes for 80 tickets -> reconciles`.
Under **Volume** are the numbers answered automatically, escalated and blocked.

**On the web page:** after a file run from the page finishes, press **Check against the decision log** under the
metrics report. It shows the run's results next to the decision log's counts, line by line, and says **RECONCILES**
when every ticket has exactly one final outcome. The buttons above it download the results file and the metrics report.
The steps below do the same from PowerShell.

**2. Count the same things straight from the decision log.** In the PowerShell window showing `(.venv)`:

```
python scripts/check_decision_log.py
```

It checks the most recent run. It shows the rows written, the rows for each step, the final outcomes, and whether
every ticket has exactly one final outcome. You should see the same numbers as in the report, and
**Result: RECONCILES**. For example, for the final validation run: 356 rows; 53 answered automatically, 24 sent to a
person and 3 blocked by a guardrail; 80 tickets, each with exactly one final outcome.

To check an earlier run, add its run id from the top of its metrics report, for example
`python scripts/check_decision_log.py run-20261119T182708-10f116`.

### Step 11. Run the tests

*The tests check every part of the system automatically. They need no API key and make no calls to the model service.*

```
python -m pytest tests/ -v
```

Every test should pass; the summary line reads `381 passed, 1 xfailed`.

The one `xfailed` ("expected to fail") is deliberate: a known limitation kept visible as a test
(`tests/test_decisions.py`). Tickets like "We were throttled… we would rather pay overage than be stopped" go to a
person, but the same request in other words ("We got rate limited… we'd prefer to pay extra than be cut off") is not
recognised and would be answered automatically. It is described in `docs/known_limitations.md` (5). `xfailed` is not a
failure: pytest still finishes successfully. If the system ever gets this case right, pytest shows `xpassed` instead.

## More checks

*Do these any time after [step 6](#step-6-build-the-article-store-and-the-decision-log), in the PowerShell window showing `(.venv)`.*

### Check the kill switch

*The course's governance rules require a way to stop automatic replies at once, without changing any code; this is
it. The kill switch stops all automatic replies at once: while it is on, every ticket goes to a person. It is checked
before every ticket, so it works straight away, even in the middle of a run, without restarting anything.*

**The simplest way: the web page.** With the system from [step 7](#step-7-start-the-system) running, open
http://127.0.0.1:8000. The **Kill switch** box shows whether it is on, and its button turns it on or off. Then send the
demo tickets (step 2 below) to see every one go to a person. Each change is written, with the time, to
`storage/kill_switch_history.txt`. The commands below do exactly the same, from PowerShell.

Use the PowerShell window showing `(.venv)`, in the project folder (`C:\cloudserve_test\cloudserve`).

**1. Turn it on** (this creates an empty file called `storage/kill_switch`):

```powershell
New-Item storage\kill_switch -ItemType File -Force
```

**2. Check it is on.** If the system from [step 7](#step-7-start-the-system) is running, open
http://127.0.0.1:8000/health: it shows `"kill_switch_on": true`. Then send the demo tickets:

```powershell
python scripts/send_demo_tickets.py
```

All seven now show **SENT TO A PERSON**, with the reason "the kill switch is on, so all automatic replies are stopped".
(After you turn it off, restart the system before sending the demo tickets again, so the follow-up rule described in
[step 8](#step-8-send-one-ticket-from-each-channel-an-escalation-and-a-guardrail-ticket) does not change the results.)

**3. Turn it off** (this deletes the file), so automatic replies start again:

```powershell
Remove-Item storage\kill_switch
```

http://127.0.0.1:8000/health now shows `"kill_switch_on": false`.

### Check it copes with problems

*The assessors check that the system keeps going when something goes wrong: the AI service is down, the free tier's
limit is reached, no article matches, or a ticket is broken. This shows how to cause each one and what you should see.*

**1. The AI service cannot be reached.**
- How: disconnect from the internet, or put a wrong key in `.env`, then send the demo tickets (step 8). Put your real
  key back afterwards.
- You should see: nothing crashes and no unchecked reply is sent. Each ticket goes to a person with the reason "model
  unavailable"; after 3 failures in a row, the rest go to a person straight away. (Both checks were run on
  17 Nov 2026; results in `evaluation/results/a11_no_network/` and `evaluation/results/a11_wrong_key/`.)

**2. The free tier's limit is reached.**
- How: it happens by itself on Groq's free tier with a large file (step 9).
- You should see: the system waits as long as Groq asks, then carries on. The report shows the waiting time separately.

**3. No article matches the ticket.**
- How: on [step 7](#step-7-start-the-system)'s page, send a ticket about something the articles do not cover, for
  example "What is the weather like today?".
- You should see: it goes to a person, and the AI model is not called.

**4. A broken or empty ticket.**
- How: on [step 7](#step-7-start-the-system)'s page, send a ticket with an empty body (`"body": ""`).
- You should see: it goes to a person ("Needs a specialist"), and the system carries on.

Each of these is also covered by the tests (step 11), for example "when every model fails the ticket is escalated
with the reason", "a rate limit waits as long as the provider asks", "an unrelated question returns nothing" and
"missing fields, empty body and odd characters never crash".

### Check it stops attacks (red-team check)

*Fourteen tickets written to attack or trick the system are sent through the real system: for example, hidden
instructions to the AI inside a question, a secret key or someone's contact details pasted into a ticket, a demand for
a refund, or a message in Spanish. Each must be handled safely: most must go to a person, and any that may be answered
must contain no private data and no promises. It needs the API key and takes a few minutes.*

```
python scripts/red_team.py
```

It writes the result for every ticket to `evaluation/results/red_team.md`.

## Optional extras

### Optional: watch it live (Prometheus and Grafana)

*This shows the system's work on live charts while tickets are processed. Nothing else needs it. Set it up once,
after steps 1 to 6 and before you start the system: Prometheus collects the numbers, and Grafana draws the charts.*

**1. Get Prometheus.** Tested with Prometheus 3.13.5. It needs no installing: you unzip it and run it. On https://prometheus.io/download/, under
**prometheus**, download the version for Windows (the file ending in `windows-amd64.zip`).

**Open a new PowerShell window for Prometheus.** It keeps running in this window, so keep it separate from the window
you use for the project (the one showing `(.venv)`). In the new window:

```powershell
Get-ChildItem "$env:USERPROFILE\Downloads\prometheus-*windows-amd64.zip" | Expand-Archive -DestinationPath C:\prometheus -Force
cd C:\prometheus\prometheus-*
.\prometheus.exe --version
```

**2. Start Prometheus** in that same new window. It keeps running there: leave the window open (minimise it if you like)
for as long as you want the charts, and close it to stop Prometheus.

```powershell
.\prometheus.exe --config.file=C:\cloudserve_test\cloudserve\monitoring\prometheus.yml --web.listen-address=127.0.0.1:9090
```

If you downloaded the project somewhere other than `C:\cloudserve_test` in [step 1](#step-1-get-the-code), change that part of the path.
Open http://localhost:9090/targets: you will see `support-system`. It shows **DOWN** until the system is started.

**3. Get Grafana.** Tested with Grafana 13.3.1; the dashboard needs Grafana 10 or newer. On Windows 10 or 11, run this in the
PowerShell window you used for steps 1 to 6 (it is free until step 7; not the Prometheus window, which is busy):

```powershell
winget install -e --id GrafanaLabs.Grafana.OSS
```

If Windows asks for permission to make changes, press **Yes**. It installs Grafana and starts it in the background as a Windows service, so it needs no PowerShell window of its own:
from now on you use it in your web browser. (Otherwise, download it from https://grafana.com/grafana/download.)
Open http://localhost:3000 and sign in with `admin` / `admin`; it then asks you to choose a new password.

If Grafana is already installed, `winget` says so ("Found an existing package already installed"); that is fine, carry
on. To start completely fresh instead, first remove it in the same window (the one from steps 1 to 6), then run the
install command above again:

```powershell
winget uninstall -e --id GrafanaLabs.Grafana.OSS
```

Removing it may also remove an earlier connection and dashboard; steps 4 and 5 below set them up again.

**4. Connect Grafana to Prometheus.** In Grafana: **Connections > Data sources > Add data source > Prometheus**, set the
URL to `http://localhost:9090`, then press **Save & test**.

**5. Load the dashboard.** **Dashboards > New > Import**, upload `monitoring/grafana_dashboard.json` from the project,
choose the Prometheus data source when asked, and press **Import**.

**From now on, start the charts with one button.** Start the system ([step 7](#step-7-start-the-system)), open its web
page at http://127.0.0.1:8000 and press **Start the live charts from zero**. Each time, it:

- sets the system's own chart numbers back to 0, stops any Prometheus already running and deletes the numbers it
  collected before, so every chart starts from zero;
- starts Prometheus again in its own small window, minimised on the taskbar (leave it open; close it to stop Prometheus);
- starts Grafana if it is not running (if Windows asks for permission, press **Yes**);
- waits until Prometheus can read the system, then 30 seconds more, and shows **Ready** with a link to the dashboard.

Then choose a ticket file on the same page and press **Run**. It finds Prometheus in `C:\prometheus`, as in step 1, and
never touches the project's own `data` folder (the tickets) or the decision log. Without the web page, double-clicking
**`start_live_charts.bat`** in the project folder does the same, before you start the system (if Windows shows "Windows
protected your PC", press **More info**, then **Run anyway**). The manual steps above and below still work the same way.

**6. Start the system and watch.** Start the system ([step 7](#step-7-start-the-system)), or start a full run with
`--metrics-port 8001` added to the [step 9](#step-9-run-a-whole-file-of-tickets-unattended) command. Within about 15 seconds, http://localhost:9090/targets shows **UP**, and the dashboard fills in as
tickets are processed. It has five charts: tickets per hour by channel and outcome; the share answered automatically
against escalated; response time at the median and the slowest 5% (with the 3-second target line); guardrail
activations over time; and how confident the system was. In Grafana, set the time range at the top right to
**Last 15 minutes** and the refresh to **10s** to see the charts move.

Only tickets sent to the running system appear on the charts: in [step 8](#step-8-send-one-ticket-from-each-channel-an-escalation-and-a-guardrail-ticket),
use the command that sends the tickets to the system you started in step 7, not the one that runs them as a separate program.

**Always wait before sending tickets.** The charts show how much the numbers go up, so Prometheus must read the
starting value of 0 first. After starting Prometheus or the system, wait until http://localhost:9090/targets shows
**UP**, then 30 seconds more. Tickets sent sooner are processed normally but may not appear on the charts.

**If the charts stay empty:**

- Open http://localhost:9090, type `tickets_processed_total` in the query box and press **Execute**. Numbers above 0
  mean Prometheus has the tickets; all 0 means no ticket has reached the running system yet.
- If Prometheus has them but Grafana does not show them, open a chart's menu (the three dots at its top right),
  choose **Edit**, and check that the data source above its query says **Prometheus**. If not, import the dashboard
  again (step 5), choosing **Prometheus** in the drop-down, and press **Overwrite** if asked.

**To clear the charts and start fresh:** the simplest way is the **Start the live charts from zero** button (above).
To do it by hand instead: Prometheus keeps everything it has collected in a folder called `data`,
inside the folder it is started from. To clear it:

1. Stop Prometheus: press **Ctrl+C** in its window and wait until the normal `PS C:\...>` prompt is back.
2. In that window, delete its stored numbers and start it again:

   ```powershell
   cd C:\prometheus\prometheus-*
   Remove-Item -Recurse -Force data
   .\prometheus.exe --config.file=C:\cloudserve_test\cloudserve\monitoring\prometheus.yml --web.listen-address=127.0.0.1:9090
   ```

   This removes only the collected numbers, not Prometheus itself or its settings. It makes a new, empty `data`
   folder when it starts. (Do not delete the project's own `data` folder, which holds the tickets.)
3. Restart the system too, so it does not send its earlier totals again: press **Ctrl+C** in its window, then run
   `python -m src.api`.
4. Wait until http://localhost:9090/targets shows **UP**, then **30 seconds more**, before sending any tickets.

### Optional: settings

*The tested settings are already the defaults, so you do not need this section to run the system.*

Each can be switched off for a comparison, for example `$env:QUESTION_RULES="off"` in PowerShell:

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
6. **Write** the reply: an AI model (on Groq) picks which parts of the article answer, and the code copies them word for
   word.
7. **Check** the reply with five guardrails (private data, every sentence backed by the article, no instructions taken
   from the ticket, tone, confidence). If any check fails, or cannot run, the reply is not sent.
8. **Plan rule:** a reply from an article meant only for other plans goes to a person with the draft.

A ticket for a person comes with a plain summary, the relevant articles and, where useful, a draft reply. The labels in
the ticket files are never used to decide.

### What is where

| Folder | What it holds |
|---|---|
| `src/` | The system itself |
| `tests/` | The automatic tests, run on GitHub after every change |
| `evaluation/` | The run command, every run's results and metrics report, and the two people's review sheets |
| `data/` | The tickets, the help articles, the demo tickets and the attack tickets |
| `prompts/` | The instructions given to the AI models, with their versions |
| `models/` | The two trained models (ticket type, and the decisions learned from Mohnish Grover) |
| `scripts/` | Setup, checking and analysis scripts; each says at the top what it does |
| `monitoring/` | The Prometheus settings and the Grafana dashboard |
| `start_live_charts.bat` | Starts the live charts with no earlier numbers, like the web page's button (Optional: watch it live) |
| `docs/` | The design, governance, decision log, known limitations and a guide to every file |

`.env.example` lists every setting with placeholder values. Your own `.env` (with your key) and the `storage/` folder
are never shared or committed.

### Results of the final runs

On Groq's free tier, 19 to 20 November 2026. The full results and the reasons for any missed target are in the report
and in `evaluation/results/`.

| Measure (target) | 80 validation tickets | 500 development tickets |
|---|---|---|
| Answered automatically (60% or more) | 66.2% | 66.0% |
| Sent to a person (30% or less) | 33.8% | 34.0% |
| Tickets that must go to a person but were answered (0) | 0 of 14 | 0 of 87 |
| Replies citing the right article (95%) | 97.6% | 93.0% |
| Private data in a reply (0) | 0 | 0 |
| Slowest 5% of replies, leaving out the free tier's waiting (under 3 seconds) | 3.4 s | 7.2 s |
| Every ticket logged exactly once | 80 of 80 | 500 of 500 |
