"""Process an uploaded ticket file from a web page, inside the running system (README step 9,
Way 1).

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
The page at http://127.0.0.1:8000/ lets someone choose a ticket file and press Run. The file goes through exactly the
same unattended run as `python -m src.run_evaluation` (src/run_evaluation.py): every ticket, every rule and guardrail,
the decision log and the metrics report. Because it runs inside the system that Prometheus reads, Grafana shows it
live. Nothing here makes a decision; it only starts the run, reports its progress and shows the report at the end.
One file at a time, so two runs never compete for the free tier's limit.
"""
import json
import re
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ACTIONS = ("auto_respond", "escalate", "block")


def read_tickets(data: bytes) -> list:
    """The uploaded file as a list of tickets, or a ValueError saying in plain words what is wrong with it."""
    try:
        raw = json.loads(data.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ValueError("This file could not be read as a ticket file. Choose a .json file in the same format as "
                         "data/validation_tickets.json.") from None
    tickets = raw.get("tickets") if isinstance(raw, dict) else raw
    if not isinstance(tickets, list) or not tickets or not all(isinstance(t, dict) for t in tickets):
        raise ValueError("This file has no tickets in it. Choose a .json file in the same format as "
                         "data/validation_tickets.json.")
    return tickets


class FileRuns:
    """Starts a run for an uploaded file in the background and keeps its progress for the page to show."""

    def __init__(self, runner=None, results_dir=None):
        self.runner = runner                      # tests pass a fake; otherwise the real unattended run
        self.results_dir = Path(results_dir) if results_dir else ROOT / "evaluation" / "results"
        self.jobs = {}
        self.lock = threading.Lock()
        self.threads = {}
        self.results = {}      # job id -> {ticket id: full result}, for the ticket details (kept out of status)
        self.paths = {}        # job id -> (results file, metrics report)

    def _runner(self):
        if self.runner is None:
            from src.run_evaluation import run_evaluation
            return run_evaluation
        return self.runner

    def start(self, filename: str, data: bytes) -> dict:
        tickets = read_tickets(data)
        with self.lock:
            if any(j["status"] == "running" for j in self.jobs.values()):
                raise RuntimeError("A file is already being processed. Wait until it finishes, then run the next one.")
            stem = re.sub(r"[^A-Za-z0-9_-]+", "_", Path(filename or "tickets").stem)[:40].strip("_") or "tickets"
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
            uploaded = self.results_dir / "uploads" / f"{stem}_{stamp}.json"
            results = self.results_dir / f"web_{stem}_{stamp}.json"
            uploaded.parent.mkdir(parents=True, exist_ok=True)
            uploaded.write_bytes(data)
            job_id = uuid.uuid4().hex[:12]
            self.jobs[job_id] = {"job_id": job_id, "status": "running", "file": filename or uploaded.name,
                                 "total": len(tickets), "done": 0, "counts": {a: 0 for a in ACTIONS},
                                 "recent": [], "results_file": self._shown(results),
                                 "report_file": self._shown(results.with_name(results.stem + "_metrics.md")),
                                 "report": None, "error": None, "run_id": None}
            self.results[job_id] = {}
            self.paths[job_id] = (results, results.with_name(results.stem + "_metrics.md"))
            thread = threading.Thread(target=self._work, args=(job_id, uploaded, results), daemon=True)
            self.threads[job_id] = thread
        thread.start()
        return self.status(job_id)

    def _shown(self, path: Path) -> str:
        try:
            return path.relative_to(ROOT).as_posix()
        except ValueError:
            return str(path)

    def _work(self, job_id, uploaded: Path, results: Path):
        job = self.jobs[job_id]

        def progress(done, total, ticket_id, action, label, result=None):
            with self.lock:
                job["done"], job["total"] = done, total
                if result:
                    self.results[job_id][ticket_id] = result
                    job["run_id"] = result.get("run_id")
                job["counts"][action] = job["counts"].get(action, 0) + 1
                job["recent"] = ([{"ticket_id": ticket_id, "action": action, "label": label or ""}]
                                 + job["recent"])[:10]
        try:
            self._runner()(str(uploaded), str(results), progress=progress)
            report = results.with_name(results.stem + "_metrics.md")
            with self.lock:
                job["report"] = report.read_text(encoding="utf-8") if report.exists() else "(no report was written)"
                job["status"] = "done"
        except Exception as e:  # noqa: BLE001 - the page must say what went wrong, never just stop
            with self.lock:
                job["status"], job["error"] = "failed", f"{type(e).__name__}: {e}"

    def ticket(self, job_id: str, ticket_id: str):
        """One ticket's full result from a file run, for the ticket details."""
        with self.lock:
            r = self.results.get(job_id, {}).get(ticket_id)
            return json.loads(json.dumps(r)) if r else None

    def files(self, job_id: str):
        """(results file, metrics report) of a finished run, or None."""
        with self.lock:
            job = self.jobs.get(job_id)
            return self.paths.get(job_id) if job and job["status"] == "done" else None

    def busy(self) -> bool:
        """True while a file is being processed."""
        with self.lock:
            return any(j["status"] == "running" for j in self.jobs.values())

    def status(self, job_id: str):
        with self.lock:
            job = self.jobs.get(job_id)
            return json.loads(json.dumps(job)) if job else None


PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>CloudServe support triage</title>
<style>
 body{margin:0;font-family:Segoe UI,Arial,sans-serif;background:#f4f6f8;color:#14213d}
 header{background:#0f4c47;color:#fff;padding:16px 32px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px}
 header a{color:#fff;margin-left:18px;font-size:14px}
 main{max-width:1000px;margin:24px auto;padding:0 16px}
 .card{background:#fff;border-radius:10px;padding:20px 24px;margin-bottom:18px;box-shadow:0 1px 3px rgba(0,0,0,.08)}
 h1{font-size:26px;margin:0 0 4px} h2{font-size:18px;margin:0 0 12px} h3{font-size:15px;margin:18px 0 8px}
 p.note{color:#5b6472;margin:4px 0 0}
 button{background:#0f766e;color:#fff;border:0;border-radius:6px;padding:10px 22px;font-size:15px;cursor:pointer}
 button:disabled{background:#94a3b8;cursor:default}
 button.second{background:#fff;color:#0f766e;border:2px solid #0f766e} button.second:disabled{color:#94a3b8;border-color:#94a3b8;background:#fff}
 button.danger{background:#b91c1c} button.small{padding:5px 12px;font-size:13px}
 a.button{display:inline-block;background:#fff;color:#0f766e;border:2px solid #0f766e;border-radius:6px;padding:8px 18px;font-size:14px;text-decoration:none;margin-right:8px}
 .bar{height:14px;background:#e2e8f0;border-radius:7px;overflow:hidden;margin:12px 0}
 .bar div{height:100%;background:#0f766e;width:0}
 .stats{display:flex;gap:12px;flex-wrap:wrap}
 .stat{flex:1;min-width:150px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:10px 14px}
 .stat b{display:block;font-size:24px}
 table{width:100%;border-collapse:collapse;font-size:14px} td,th{text-align:left;padding:6px 8px;border-bottom:1px solid #e2e8f0;vertical-align:top}
 th{background:#f1f5f9}
 pre{white-space:pre-wrap;font-size:12px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:12px;overflow:auto}
 .md h1{font-size:22px;margin:18px 0 8px} .md h2{font-size:18px;margin:22px 0 8px;padding-top:12px;border-top:2px solid #e2e8f0}
 .md h3{font-size:15px;margin:16px 0 6px} .md p,.md li{font-size:14px;line-height:1.5} .md table{margin:8px 0 12px}
 .md th{background:#0f4c47;color:#fff} .md tr:nth-child(even) td{background:#f8fafc}
 .md td.no,.fail{color:#b91c1c;font-weight:bold} .md td.yes,.pass{color:#15803d;font-weight:bold} .md td.nm,.notrun{color:#64748b;font-style:italic}
 .md code{background:#eef2f7;padding:1px 4px;border-radius:4px}
 .msg{color:#b91c1c;margin-top:10px}
 .switch{display:flex;align-items:center;gap:16px;flex-wrap:wrap;margin-top:12px}
 .badge{font-weight:bold;padding:6px 14px;border-radius:20px;font-size:15px}
 .badge.on{background:#fee2e2;color:#b91c1c} .badge.off{background:#dcfce7;color:#15803d}
 .out{font-weight:bold;padding:2px 10px;border-radius:12px;font-size:13px;white-space:nowrap}
 .out.auto_respond{background:#dcfce7;color:#15803d} .out.escalate{background:#fef3c7;color:#92400e} .out.block{background:#fee2e2;color:#b91c1c}
 #chartlog{display:none;margin-top:12px;max-height:220px} .ready{color:#15803d;font-weight:bold;margin-top:8px} .ready a{color:#15803d}
 form.ticket{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:12px}
 form.ticket label{font-size:13px;color:#5b6472;display:flex;flex-direction:column;gap:4px}
 form.ticket .wide{grid-column:1/-1}
 input,select,textarea{font:inherit;font-size:14px;padding:7px 9px;border:1px solid #cbd5e1;border-radius:6px;background:#fff;color:#14213d}
 textarea{min-height:80px;resize:vertical}
 tr.click{cursor:pointer} tr.click:hover td{background:#ecfdf5}
 #overlay{display:none;position:fixed;inset:0;background:rgba(15,23,42,.45);z-index:10;overflow:auto;padding:24px 12px}
 #panel{background:#fff;max-width:900px;margin:0 auto;border-radius:10px;padding:22px 26px;box-shadow:0 10px 30px rgba(0,0,0,.25)}
 #panel .top{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}
 #panel dl{display:grid;grid-template-columns:200px 1fr;gap:6px 14px;font-size:14px;margin:8px 0}
 #panel dt{color:#5b6472} #panel dd{margin:0}
 details{margin:6px 0} summary{cursor:pointer;color:#0f766e}
 .govnote{background:#f0fdfa;border-left:4px solid #0f766e;padding:8px 12px;font-size:13px;color:#134e4a;margin:10px 0}
 .lim{margin:12px 0 4px} .lim .head{display:flex;justify-content:space-between;flex-wrap:wrap;gap:6px;font-size:14px}
 .lim .bar{height:16px;margin:6px 0 2px} .lim .bar div{transition:width .6s} .lim small{color:#5b6472}
 .lim .bar div.mid{background:#d97706} .lim .bar div.high{background:#b91c1c}
 @media (max-width:700px){form.ticket{grid-template-columns:1fr 1fr} #panel dl{grid-template-columns:1fr}}
</style></head>
<body>
<header><strong>CloudServe support triage</strong><span><a href="/docs" target="_blank">API docs</a>
<a href="http://localhost:3000" target="_blank">Grafana</a><a href="http://localhost:9090/targets" target="_blank">Prometheus</a></span></header>
<main>
<div class="card"><h1>Support ticket triage</h1>
<p class="note">Every ticket sent from this page goes through the same steps as the unattended run: the safety rules,
the article search, the reply and its five guardrails, and the decision log. Click any ticket in a table to see
everything the system decided about it, and why.</p></div>

<div class="card"><h2>Kill switch</h2>
<p class="note">Stops every automatic reply at once: while it is on, every ticket goes to a person. It works straight
away, even in the middle of a run, and can be turned off again at any time.</p>
<div class="switch"><span class="badge" id="killbadge">Checking…</span>
<button id="killbtn" onclick="flipKill()" disabled>…</button></div><div class="msg" id="killmsg"></div></div>

<div class="card"><h2>Live charts (optional)</h2>
<p class="note">Starts Prometheus and Grafana with every chart at zero, so only what you send next shows. It takes
about a minute and tells you when it is ready. If Windows asks for permission, press Yes.</p>
<p style="margin-top:12px"><button class="second" id="chartbtn" onclick="startCharts()">Start the live charts from zero</button></p>
<pre id="chartlog"></pre><div id="chartdone"></div><div class="msg" id="chartmsg"></div></div>

<div class="card"><h2>Free tier limits (Groq)</h2>
<p class="note">How much of each model's limit is used, as Groq reported it on the latest call. It updates by
itself every few seconds while tickets are processed. Tokens are limited per minute and refill fully within a minute;
requests are limited per day. When a model's tokens bar is full, Groq refuses calls (HTTP 429, too many requests):
the system waits and tries again, and a reply whose grounding check cannot run is never sent.</p>
<div class="stats" id="capacity" style="margin-top:12px"></div><p class="note" id="capnote"></p>
<div id="limits"><p class="note">No call has been made since the system started. Press the button to check now.</p></div>
<p style="margin-top:12px"><button class="second" id="limbtn" onclick="checkLimits()">Check the limits now</button>
<small style="color:#5b6472;margin-left:8px">makes one tiny call to each model (about 20 to 60 tokens each)</small></p>
<div class="msg" id="limmsg"></div></div>

<div class="card"><h2>Try tickets one at a time</h2>
<p class="note">The seven demo tickets cover every channel, an escalation and a guardrail ticket (README step 8).
Sending them again to the same running system can change some results: a repeat contact within 7 days of an
automatic reply goes to a person.</p>
<p style="margin-top:12px"><button id="demobtn" onclick="sendDemo()">Send the 7 demo tickets</button></p>
<h3>Or write your own ticket</h3>
<form class="ticket" onsubmit="sendOne(event)">
 <label>Channel<select id="f_channel"><option value="email">email</option><option value="chat">chat</option>
  <option value="docs_comment">documentation comment</option><option value="forum">forum</option></select></label>
 <label>Plan<select id="f_tier"><option value="standard">Standard</option><option value="business">Business</option>
  <option value="enterprise">Enterprise</option></select></label>
 <label>Region<select id="f_region"><option value="north_america">North America</option><option value="europe">Europe</option>
  <option value="asia_pacific">Asia Pacific</option><option value="latin_america">Latin America</option></select></label>
 <label>Language<select id="f_fluency"><option value="fluent">fluent English</option><option value="non_fluent">non-fluent English</option></select></label>
 <label class="wide">Subject<input id="f_subject" placeholder="for example: Deployment keeps rolling back"></label>
 <label class="wide">Message<textarea id="f_body" placeholder="Write the customer's message here"></textarea></label>
 <div class="wide"><button id="onebtn" type="submit">Send this ticket</button></div>
</form>
<div class="msg" id="onemsg"></div>
<div id="singles" style="display:none"><h3>Results</h3>
<table><thead><tr><th>Ticket</th><th>Channel</th><th>Result</th><th>Label</th><th>Reason</th></tr></thead><tbody id="singlerows"></tbody></table></div>
</div>

<div class="card"><h2>Run a whole ticket file</h2>
<p class="note">The same unattended run as the README's command, with a metrics report at the end.</p>
<p style="margin-top:12px"><input type="file" id="file" accept=".json"> <button id="run" onclick="run()">Run</button></p>
<div class="msg" id="msg"></div></div>
<div class="card" id="progress" style="display:none"><h2>Progress</h2>
<div id="line"></div><div class="bar"><div id="fill"></div></div>
<div class="stats"><div class="stat"><b id="c_auto">0</b>Answered automatically</div>
<div class="stat"><b id="c_esc">0</b>Escalated</div><div class="stat"><b id="c_block">0</b>Blocked by guardrails</div></div>
<h3>Latest tickets (click one for its details)</h3><table><thead><tr><th>Ticket</th><th>Result</th><th>Label</th></tr></thead>
<tbody id="recent"></tbody></table></div>
<div class="card" id="done" style="display:none"><h2>Metrics report</h2>
<p id="downloads"></p><p class="note" id="files"></p>
<p style="margin-top:12px"><button class="second" id="checkbtn" onclick="checkLog()">Check against the decision log</button></p>
<div id="check"></div>
<div class="md" id="report"></div></div>
</main>

<div id="overlay" onclick="if(event.target===this)closeDetails()"><div id="panel"></div></div>

<script>
function esc(t){return String(t==null?"":t).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");}
function inline(t){return esc(t).replace(/\*\*(.+?)\*\*/g,"<b>$1</b>").replace(/`([^`]+)`/g,"<code>$1</code>");}
function cells(l){return l.trim().replace(/^\|/,"").replace(/\|$/,"").split("|").map(c=>c.trim());}
function cls(c){return c==="**No**"?' class="no"':c==="Yes"?' class="yes"':c==="Not measured"?' class="nm"':"";}
function md(text){            // the metrics report (Markdown) as tidy HTML: headings, tables, lists, code
 const L=(text||"").split("\n"); let h="", i=0;
 while(i<L.length){const l=L[i];
  if(l.startsWith("```")){let c=[];i++;while(i<L.length&&!L[i].startsWith("```"))c.push(L[i++]);i++;h+="<pre>"+esc(c.join("\n"))+"</pre>";continue;}
  const m=l.match(/^(#{1,3}) (.*)/); if(m){h+="<h"+m[1].length+">"+inline(m[2])+"</h"+m[1].length+">";i++;continue;}
  if(l.trim().startsWith("|")){let rows=[];while(i<L.length&&L[i].trim().startsWith("|"))rows.push(L[i++]);
   let t="<table><thead><tr>"+cells(rows[0]).map(c=>"<th>"+inline(c)+"</th>").join("")+"</tr></thead><tbody>";
   for(const r of rows.slice(2))t+="<tr>"+cells(r).map(c=>"<td"+cls(c)+">"+inline(c)+"</td>").join("")+"</tr>";
   h+=t+"</tbody></table>";continue;}
  if(l.startsWith("- ")){let it=[];while(i<L.length&&L[i].startsWith("- "))it.push(L[i++].slice(2));h+="<ul>"+it.map(x=>"<li>"+inline(x)+"</li>").join("")+"</ul>";continue;}
  if(l.trim()){h+="<p>"+inline(l)+"</p>";} i++;}
 return h;}
const WORDS={auto_respond:"Answered automatically",escalate:"Escalated to a person",block:"Blocked by a guardrail"};
const CHANNEL={email:"email",chat:"chat",docs_comment:"documentation comment",forum:"forum",unknown:"unknown"};
const GUARD={   // docs/governance.md section 4: what each guardrail checks
 private_data:"Names, addresses, keys, account numbers, anything identifying a customer",
 grounding_words:"Every sentence's words and numbers appear in its article",
 grounding_model:"A second model (Qwen, another family) checks the article fits the situation and each sentence is supported",
 instruction_integrity:"The ticket has not tried to instruct the system; the reply holds none of our instructions",
 tone_and_scope:"No commitments about refunds, credits or dates; within support; within the length limit",
 confidence_floor:"The classifier was confident enough and the writer was sure; a missing confidence counts as low"};
const STAGE={classification:"1. Classification",routing:"2. Routing",generation:"3. Generation",validation:"4. Validation",outcome:"5. Outcome"};
function badge(a){return '<span class="out '+esc(a)+'">'+esc(WORDS[a]||a)+"</span>";}
function $(id){return document.getElementById(id);}
async function getJSON(u,o){const r=await fetch(u,o);let j=null;try{j=await r.json();}catch(e){}
 if(!r.ok)throw new Error((j&&j.detail)||("The system answered "+r.status));return j;}
const DOWN="The system did not answer. Is it still running? (README step 7)";

// ---------- kill switch ----------
let killOn=null;
function showKill(on){killOn=on; const b=$("killbadge"), k=$("killbtn");
 b.className="badge "+(on?"on":"off");
 b.textContent=on?"ON: every ticket goes to a person":"Off: automatic replies are allowed";
 k.textContent=on?"Turn the kill switch off":"Turn the kill switch on"; k.className=on?"":"danger"; k.disabled=false;}
function checkKill(){fetch("/health").then(r=>r.json()).then(j=>showKill(j.kill_switch_on)).catch(()=>{$("killbadge").textContent=DOWN;});}
async function flipKill(){
 const k=$("killbtn"), m=$("killmsg"); k.disabled=true; m.textContent="";
 try{const j=await getJSON("/kill-switch",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({on:!killOn})});
  showKill(j.kill_switch_on); m.textContent=j.note||"";}
 catch(e){m.textContent=e.message||DOWN;k.disabled=false;}
}
checkKill(); setInterval(checkKill,5000);   // also shows a change made with the README's PowerShell commands

// ---------- live charts ----------
async function startCharts(){
 const b=$("chartbtn"), m=$("chartmsg"); m.textContent=""; $("chartdone").innerHTML=""; b.disabled=true;
 try{await getJSON("/live-charts",{method:"POST"}); chartPoll();}
 catch(e){m.textContent=e.message||DOWN;b.disabled=false;}
}
async function chartPoll(){
 const j=await getJSON("/live-charts"), log=$("chartlog");
 log.style.display="block"; log.textContent=j.lines.join("\n")+(j.status==="starting"?"\n…":""); log.scrollTop=log.scrollHeight;
 if(j.status==="starting"){setTimeout(chartPoll,2000);return;}
 $("chartbtn").disabled=false;
 if(j.status==="ready")$("chartdone").innerHTML='<p class="ready">Ready: the charts start from zero. <a href="'+esc(j.dashboard)+
  '" target="_blank">Open the Grafana dashboard</a>, then send tickets.</p>';
 else $("chartmsg").textContent="The live charts did not start. The lines above say why.";
}

// ---------- free tier limits ----------
function limBar(label,used,limit,extra){
 if(used==null||!limit)return "<small>"+esc(label)+": not reported</small>";
 const pc=Math.min(100,100*used/limit), c=pc>=85?"high":pc>=60?"mid":"";
 return "<small>"+esc(label)+": "+Math.round(used).toLocaleString()+" of "+Math.round(limit).toLocaleString()+" used ("+Math.round(pc)+"%)"+
  (extra?"; "+extra:"")+'</small><div class="bar"><div class="'+c+'" style="width:'+pc+'%"></div></div>';}
function showLimits(list){
 if(!list||!list.length)return;
 $("limits").innerHTML=list.map(m=>'<div class="lim"><div class="head"><b>'+esc(m.role.charAt(0).toUpperCase()+m.role.slice(1))+": "+esc(m.model)+"</b><small>"+
  (m.refused_last_10_min?'<span class="fail">Refused '+m.refused_last_10_min+" times in the last 10 minutes (last "+Math.round(m.last_refused_ago)+" s ago)</span>":
   '<span class="pass">No refusals in the last 10 minutes</span>')+" · figures from "+Math.round(m.seconds_ago)+" s ago</small></div>"+
  limBar("Tokens this minute",m.tokens_used,m.tokens_limit,m.tokens_used?"full again in "+m.tokens_refill_in+" s":"")+
  limBar("Requests today",m.requests_used,m.requests_limit,"")+"</div>").join("");}
function showCapacity(c){if(!c)return; const v=x=>x==null?"–":"Approx. "+x.toLocaleString();
 $("capacity").innerHTML='<div class="stat"><b>'+v(c.now)+"</b>Answered tickets left this minute<br><small>More tickets can get an automatic reply before this minute's limit is reached</small></div>"+
  '<div class="stat"><b>'+v(c.per_minute)+"</b>Answered tickets in a full minute<br><small>The most the limit allows each minute, once it has refilled</small></div>"+
  '<div class="stat"><b>'+v(c.today)+"</b>Answered tickets left today<br><small>From the requests per day still left</small></div>";
 $("capnote").textContent="All three are approximate. Each answered ticket needs one writer call (about "+c.tokens_per_ticket.writer.toLocaleString()+
  " tokens, "+c.source.writer+") and one grounding check (about "+c.tokens_per_ticket["grounding check"].toLocaleString()+" tokens, "+
  c.source["grounding check"]+"). Tickets a rule sends to a person need no model call, and a refused call that is tried again uses more."+
  (c.now==null?" The numbers appear after the first call: press Check the limits now.":"");}
function pollLimits(){fetch("/limits").then(r=>r.json()).then(j=>{showLimits(j.models);showCapacity(j.capacity);}).catch(()=>{});}
async function checkLimits(){const b=$("limbtn"), m=$("limmsg"); b.disabled=true; m.textContent="";
 try{const j=await getJSON("/limits/check",{method:"POST"}); showLimits(j.models); showCapacity(j.capacity);
  const bad=j.answers.filter(a=>a.answer!=="works"); if(bad.length)m.textContent=bad.map(a=>a.model+": "+a.answer).join("; ");}
 catch(e){m.textContent=e.message||DOWN;}
 b.disabled=false;}
pollLimits(); setInterval(pollLimits,3000);

// ---------- one ticket at a time ----------
const singles={};   // ticket id -> result (from POST /tickets, with its run id)
function addSingle(ticket,r){singles[r.ticket_id]=r; $("singles").style.display="block";
 const tr=document.createElement("tr"); tr.className="click"; tr.onclick=()=>openDetails(r);
 tr.innerHTML="<td>"+esc(r.ticket_id)+"</td><td>"+esc(CHANNEL[ticket.channel]||ticket.channel)+"</td><td>"+badge(r.action)+
  "</td><td>"+esc(r.label||"-")+"</td><td>"+esc((r.reason||"").slice(0,140))+((r.reason||"").length>140?"… (click for all)":"")+"</td>";
 $("singlerows").prepend(tr);}
async function postTicket(t){return getJSON("/tickets",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(t)});}
async function sendDemo(){
 const b=$("demobtn"), m=$("onemsg"); b.disabled=true; m.textContent="";
 try{const list=await getJSON("/demo-tickets");
  for(let i=0;i<list.length;i++){b.textContent="Sending "+(i+1)+" of "+list.length+"…"; addSingle(list[i],await postTicket(list[i]));}}
 catch(e){m.textContent=e.message||DOWN;}
 b.disabled=false; b.textContent="Send the 7 demo tickets";}
async function sendOne(ev){ev.preventDefault();
 const b=$("onebtn"), m=$("onemsg"), body=$("f_body").value.trim(); m.textContent="";
 if(!body){m.textContent="Write the customer's message first.";return;}
 const now=new Date(), stamp=now.toISOString().replace(/[-:T.Z]/g,"").slice(0,14);
 const t={ticket_id:"WEB-"+stamp,channel:$("f_channel").value,subject:$("f_subject").value.trim(),body:body,
  received_at:now.toISOString(),customer_id:"WEB-"+stamp,customer_tier:$("f_tier").value,
  customer_region:$("f_region").value,language_fluency:$("f_fluency").value};
 b.disabled=true; b.textContent="Sending…";
 try{const r=await postTicket(t); addSingle(t,r); openDetails(r);}catch(e){m.textContent=e.message||DOWN;}
 b.disabled=false; b.textContent="Send this ticket";}

// ---------- ticket details (governance: every automated decision reconstructable) ----------
function closeDetails(){$("overlay").style.display="none";}
document.addEventListener("keydown",e=>{if(e.key==="Escape")closeDetails();});
function row(k,v){return "<dt>"+esc(k)+"</dt><dd>"+v+"</dd>";}
function guardCell(v){v=String(v||"");
 return v==="pass"?'<span class="pass">pass</span>':v.startsWith("not run")?'<span class="notrun">'+esc(v)+"</span>":'<span class="fail">'+esc(v)+"</span>";}
async function openDetails(r){
 const p=$("panel"); $("overlay").style.display="block";
 p.innerHTML="<p>Loading the details of "+esc(r.ticket_id)+"…</p>";
 let trail=[], trailErr="";
 try{trail=await getJSON("/decision-log/"+encodeURIComponent(r.run_id)+"/"+encodeURIComponent(r.ticket_id));}catch(e){trailErr=e.message;}
 const h=r.handover||{}, auto=r.action==="auto_respond";
 let x='<div class="top"><h2 style="margin:0">Ticket '+esc(r.ticket_id)+" "+badge(r.action)+'</h2><button class="small" onclick="closeDetails()">Close</button></div>';
 x+="<h3>Decision</h3><dl>"+row("Outcome",esc(WORDS[r.action]||r.action)+(r.label?" ("+esc(r.label)+")":""))+
  row("Why",esc(r.reason))+row("Priority",esc(r.priority||"-"))+
  row("Ticket type",esc(r.type||"-")+(r.confidence!=null?" at "+Math.round(r.confidence*100)+"% confidence (threshold 85%)":""))+
  row("Run",esc(r.run_id))+"</dl>";
 x+="<h3>"+(auto?"The reply the customer received":"What the customer received")+"</h3><pre>"+esc(r.sent_text||"(nothing)")+"</pre>";
 if(!auto){x+="<h3>Handover note for the person</h3><dl>"+row("Summary","<pre style='margin:0'>"+esc(h.summary||"-")+"</pre>");
  if(h.tried&&h.tried.length)x+=row("What the system tried","<ul style='margin:0;padding-left:18px'>"+h.tried.map(t=>"<li>"+esc(t)+"</li>").join("")+"</ul>");
  if(h.documents&&h.documents.length)x+=row("Help articles attached",h.documents.map(d=>esc(d.doc_id)+": "+esc(d.title)).join("<br>"));
  x+="</dl>";
  if(h.draft)x+="<details><summary>Draft reply for the person to check and send</summary><pre>"+esc(h.draft)+"</pre></details>";
  if(h.stopped_reply)x+="<details><summary>The reply a guardrail stopped (for information, not for sending)</summary><pre>"+esc(h.stopped_reply)+"</pre></details>";
  if(h.earlier_reply)x+="<details><summary>The earlier automatic reply</summary><pre>"+esc(h.earlier_reply)+"</pre></details>";}
 x+="<h3>Articles</h3><dl>"+row("Found by the search (top 5)",esc((r.articles_found||[]).join(", ")||"-"))+
  row("Cited in the reply",esc((r.cited||[]).join(", ")||"none"))+"</dl>";
 for(const c of (r.citations||[]))x+="<details><summary>"+esc(c.doc_id)+": "+esc(c.title)+" (search score "+esc(c.score)+
  ") — the sentences taken from it</summary><ul>"+(c.sentences||[]).map(s=>"<li>"+esc(s)+"</li>").join("")+"</ul></details>";
 const g=r.guardrails||{};
 if(Object.keys(g).length){x+="<h3>Guardrails on the reply</h3><table><thead><tr><th>Guardrail</th><th>What it checks</th><th>Result</th></tr></thead><tbody>";
  for(const k of Object.keys(g))x+="<tr><td>"+esc(k)+"</td><td>"+esc(GUARD[k]||"")+"</td><td>"+guardCell(g[k])+"</td></tr>";
  x+='</tbody></table><div class="govnote">All guardrails fail closed: if a check itself errors or cannot run, the reply is blocked and the ticket goes to a person.</div>';}
 else x+="<h3>Guardrails on the reply</h3><p class='note'>No reply was written, so no reply check ran (a rule sent the ticket to a person first).</p>";
 const tk=r.tokens||{};
 x+="<h3>Time and cost</h3><dl>"+row("Response time",((r.latency_ms||0)/1000).toFixed(1)+" s"+(r.wait_ms?" (of which "+(r.wait_ms/1000).toFixed(1)+" s waiting for the free tier's rate limit)":""))+
  row("Model calls",esc(r.model_calls))+row("Tokens","writer "+(tk.writer_in||0)+" in, "+(tk.writer_out||0)+" out; checker "+(tk.checker_in||0)+" in, "+(tk.checker_out||0)+" out")+"</dl>";
 x+="<h3>Decision log (audit trail)</h3>";
 if(trailErr)x+="<p class='msg'>"+esc(trailErr)+"</p>";
 else{x+='<div class="govnote">Every step is written to the decision log (storage/decisions.db) with its reason, the model and prompt version used, and the requirement it serves (FR = functional requirement, PR = prompt in the prompt library). No customer name or ticket text is stored there: the input summary holds only channel, plan, region, fluency and length.</div>';
  x+="<table><thead><tr><th>Step</th><th>Decision</th><th>Reason</th><th>Recorded</th></tr></thead><tbody>";
  for(const d of trail){const extra=[];
   if(d.prediction)extra.push("prediction: "+esc(d.prediction)+(d.confidence!=null?" ("+Math.round(d.confidence*100)+"%)":""));
   if(d.threshold!=null)extra.push("threshold: "+Math.round(d.threshold*100)+"%");
   if(d.model)extra.push("model: "+esc(d.model)); if(d.prompt_version)extra.push("prompt: "+esc(d.prompt_version));
   if(d.requirement_ids&&d.requirement_ids.length)extra.push("requirements it serves: "+esc(d.requirement_ids.join(", ")));
   x+="<tr><td>"+esc(STAGE[d.stage]||d.stage)+"</td><td>"+esc(d.action_taken)+(d.label?"<br>"+esc(d.label):"")+"</td><td>"+esc(d.reason)+
    (extra.length?"<br><small style='color:#5b6472'>"+extra.join("; ")+"</small>":"")+"</td><td><small>"+esc(d.created_at)+"<br>"+esc(d.input_summary||"")+
    "<br>id "+esc((d.decision_id||"").slice(0,8))+"</small></td></tr>";}
  x+="</tbody></table>"; if(!trail.length)x+="<p class='note'>No rows found for this ticket in the decision log.</p>";}
 p.innerHTML=x;}

// ---------- a whole file ----------
let job=null;
function msg(t){$("msg").textContent=t||"";}
async function run(){
 const f=$("file").files[0];
 if(!f){msg("Choose a ticket file first.");return;}
 msg(""); $("run").disabled=true;
 const fd=new FormData(); fd.append("file",f);
 try{const j=await getJSON("/runs",{method:"POST",body:fd}); $("done").style.display="none"; $("check").innerHTML=""; job=j.job_id; poll(j.job_id);}
 catch(e){msg(e.message||DOWN);$("run").disabled=false;}
}
async function fileTicket(id){try{openDetails(await getJSON("/runs/"+job+"/tickets/"+encodeURIComponent(id)));}
 catch(e){$("panel").innerHTML="<p class='msg'>"+esc(e.message)+"</p>";$("overlay").style.display="block";}}
async function poll(id){
 const j=await getJSON("/runs/"+id);
 $("progress").style.display="block";
 $("line").textContent=j.file+": "+j.done+" of "+j.total+" tickets processed"+(j.status==="running"?"…":j.status==="done"?". Finished.":". Stopped: "+j.error);
 $("fill").style.width=(j.total?100*j.done/j.total:0)+"%";
 $("c_auto").textContent=j.counts.auto_respond||0; $("c_esc").textContent=j.counts.escalate||0; $("c_block").textContent=j.counts.block||0;
 const tb=$("recent"); tb.innerHTML="";
 for(const t of j.recent){const tr=document.createElement("tr"); tr.className="click"; tr.onclick=()=>fileTicket(t.ticket_id);
  tr.innerHTML="<td>"+esc(t.ticket_id)+"</td><td>"+badge(t.action)+"</td><td>"+esc(t.label||"-")+"</td>"; tb.appendChild(tr);}
 if(j.status==="running"){setTimeout(()=>poll(id),2000);return;}
 $("run").disabled=false;
 if(j.status==="done"){$("done").style.display="block";
  $("downloads").innerHTML='<a class="button" href="/runs/'+id+'/download/results">Download the results file</a>'+
   '<a class="button" href="/runs/'+id+'/download/report">Download the metrics report</a>';
  $("files").textContent="Also saved in the project: "+j.results_file+" and "+j.report_file+".";
  $("report").innerHTML=md(j.report);}
 else msg("The run stopped: "+j.error);
}
async function checkLog(){
 const b=$("checkbtn"), out=$("check"); b.disabled=true; out.innerHTML="<p>Counting the decision log…</p>";
 try{const c=await getJSON("/runs/"+job+"/check"), L=c.log, R=c.report, A=L.by_action||{};
  const line=(m,a,b_)=>"<tr><td>"+m+"</td><td>"+a+"</td><td>"+b_+"</td><td>"+(String(a)===String(b_)?'<span class="pass">Match</span>':'<span class="fail">Different</span>')+"</td></tr>";
  let x="<h3>Metrics report against the decision log (README step 10)</h3><p class='note'>Run "+esc(c.run_id)+": "+L.rows+" rows in the decision log.</p>"+
   "<table><thead><tr><th>Measure</th><th>Metrics report (results of the run)</th><th>Decision log</th><th></th></tr></thead><tbody>"+
   line("Tickets processed",R.processed,L.tickets)+line("Final outcomes (one per ticket)",R.processed,L.outcomes)+
   line("Tickets with exactly one final outcome",R.processed,L.once)+line("Answered automatically",R.auto_respond,A.auto_respond||0)+
   line("Escalated",R.escalate,A.escalate||0)+line("Blocked by guardrails",R.block,A.block||0)+"</tbody></table>";
  x+="<p class='"+(c.reconciles?"pass":"fail")+"' style='margin-top:10px'>"+(c.reconciles?"RECONCILES: every ticket has exactly one final outcome in the decision log.":"DOES NOT RECONCILE: look at the decision log for this run.")+"</p>";
  x+="<p class='note'>Rows by step: "+Object.entries(L.by_stage||{}).map(([k,v])=>esc(k)+" "+v).join(", ")+". The same counts as <code>python scripts/check_decision_log.py "+esc(c.run_id)+"</code>.</p>";
  out.innerHTML=x;}
 catch(e){out.innerHTML="<p class='msg'>"+esc(e.message||DOWN)+"</p>";}
 b.disabled=false;}
</script></body></html>
"""
