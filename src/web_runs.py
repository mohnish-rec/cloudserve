"""Process an uploaded ticket file from a web page, inside the running system (README: "Run a ticket file from the
web page").

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
                                 "report": None, "error": None}
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

        def progress(done, total, ticket_id, action, label):
            with self.lock:
                job["done"], job["total"] = done, total
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
 header{background:#0f4c47;color:#fff;padding:16px 32px;display:flex;justify-content:space-between;align-items:center}
 header a{color:#fff;margin-left:18px;font-size:14px}
 main{max-width:1000px;margin:24px auto;padding:0 16px}
 .card{background:#fff;border-radius:10px;padding:20px 24px;margin-bottom:18px;box-shadow:0 1px 3px rgba(0,0,0,.08)}
 h1{font-size:26px;margin:0 0 4px} h2{font-size:18px;margin:0 0 12px} p.note{color:#5b6472;margin:4px 0 0}
 button{background:#0f766e;color:#fff;border:0;border-radius:6px;padding:10px 22px;font-size:15px;cursor:pointer}
 button:disabled{background:#94a3b8;cursor:default}
 .bar{height:14px;background:#e2e8f0;border-radius:7px;overflow:hidden;margin:12px 0}
 .bar div{height:100%;background:#0f766e;width:0}
 .stats{display:flex;gap:12px;flex-wrap:wrap}
 .stat{flex:1;min-width:150px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:10px 14px}
 .stat b{display:block;font-size:24px}
 table{width:100%;border-collapse:collapse;font-size:14px} td,th{text-align:left;padding:6px 8px;border-bottom:1px solid #e2e8f0}
 pre{white-space:pre-wrap;font-size:12px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:12px;overflow:auto}
 .md h1{font-size:22px;margin:18px 0 8px} .md h2{font-size:18px;margin:22px 0 8px;padding-top:12px;border-top:2px solid #e2e8f0}
 .md h3{font-size:15px;margin:16px 0 6px} .md p,.md li{font-size:14px;line-height:1.5} .md table{margin:8px 0 12px}
 .md th{background:#0f4c47;color:#fff} .md tr:nth-child(even) td{background:#f8fafc}
 .md td.no{color:#b91c1c;font-weight:bold} .md td.yes{color:#15803d;font-weight:bold} .md code{background:#eef2f7;padding:1px 4px;border-radius:4px}
 .msg{color:#b91c1c;margin-top:10px} .ok{color:#15803d}
 .switch{display:flex;align-items:center;gap:16px;flex-wrap:wrap;margin-top:12px}
 .badge{font-weight:bold;padding:6px 14px;border-radius:20px;font-size:15px}
 .badge.on{background:#fee2e2;color:#b91c1c} .badge.off{background:#dcfce7;color:#15803d}
 button.danger{background:#b91c1c}
 button.second{background:#fff;color:#0f766e;border:2px solid #0f766e}
 #chartlog{display:none;margin-top:12px;max-height:220px} .ready{color:#15803d;font-weight:bold;margin-top:8px}
 .ready a{color:#15803d}
</style></head>
<body>
<header><strong>CloudServe</strong><span><a href="/docs">Send one ticket (API docs)</a>
<a href="http://localhost:3000" target="_blank">Grafana</a><a href="http://localhost:9090/targets" target="_blank">Prometheus</a></span></header>
<main>
<div class="card"><h1>Support ticket triage</h1>
<p class="note">Choose a ticket file and press Run. Every ticket goes through the same steps as the unattended run:
the safety rules, the article search, the reply and its five guardrails, and the decision log. A metrics report is
written at the end. If Grafana is open, its charts fill in while the file is processed.</p>
</div>
<div class="card"><h2>Kill switch</h2>
<p class="note">Stops every automatic reply at once: while it is on, every ticket goes to a person. It works straight
away, even in the middle of a run, and can be turned off again at any time.</p>
<div class="switch"><span class="badge" id="killbadge">Checking…</span>
<button id="killbtn" onclick="flipKill()" disabled>…</button></div><div class="msg" id="killmsg"></div></div>
<div class="card"><h2>Live charts (optional)</h2>
<p class="note">Starts Prometheus and Grafana with every chart at zero, so only the next run shows. Press it before
choosing a file; it takes about a minute and tells you when it is ready. If Windows asks for permission, press Yes.</p>
<p style="margin-top:12px"><button class="second" id="chartbtn" onclick="startCharts()">Start the live charts from zero</button></p>
<pre id="chartlog"></pre><div id="chartdone"></div><div class="msg" id="chartmsg"></div></div>
<div class="card"><h2>1. Choose a ticket file</h2>
<input type="file" id="file" accept=".json"> <button id="run" onclick="run()">Run</button>
<div class="msg" id="msg"></div></div>
<div class="card" id="progress" style="display:none"><h2>2. Progress</h2>
<div id="line"></div><div class="bar"><div id="fill"></div></div>
<div class="stats"><div class="stat"><b id="c_auto">0</b>answered automatically</div>
<div class="stat"><b id="c_esc">0</b>sent to a person</div><div class="stat"><b id="c_block">0</b>blocked by a guardrail</div></div>
<h2 style="margin-top:16px">Latest tickets</h2><table><thead><tr><th>Ticket</th><th>Result</th><th>Label</th></tr></thead>
<tbody id="recent"></tbody></table></div>
<div class="card" id="done" style="display:none"><h2>3. Metrics report</h2><p class="note" id="files"></p><div class="md" id="report"></div></div>
</main>
<script>
function esc(t){return t.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");}
function inline(t){return esc(t).replace(/\*\*(.+?)\*\*/g,"<b>$1</b>").replace(/`([^`]+)`/g,"<code>$1</code>");}
function cells(l){return l.trim().replace(/^\|/,"").replace(/\|$/,"").split("|").map(c=>c.trim());}
function md(text){            // the metrics report (Markdown) as tidy HTML: headings, tables, lists, code
 const L=(text||"").split("\n"); let h="", i=0;
 while(i<L.length){const l=L[i];
  if(l.startsWith("```")){let c=[];i++;while(i<L.length&&!L[i].startsWith("```"))c.push(L[i++]);i++;h+="<pre>"+esc(c.join("\n"))+"</pre>";continue;}
  const m=l.match(/^(#{1,3}) (.*)/); if(m){h+="<h"+m[1].length+">"+inline(m[2])+"</h"+m[1].length+">";i++;continue;}
  if(l.trim().startsWith("|")){let rows=[];while(i<L.length&&L[i].trim().startsWith("|"))rows.push(L[i++]);
   let t="<table><thead><tr>"+cells(rows[0]).map(c=>"<th>"+inline(c)+"</th>").join("")+"</tr></thead><tbody>";
   for(const r of rows.slice(2))t+="<tr>"+cells(r).map(c=>"<td"+(c==="**No**"?' class="no"':c==="Yes"?' class="yes"':"")+">"+inline(c)+"</td>").join("")+"</tr>";
   h+=t+"</tbody></table>";continue;}
  if(l.startsWith("- ")){let it=[];while(i<L.length&&L[i].startsWith("- "))it.push(L[i++].slice(2));h+="<ul>"+it.map(x=>"<li>"+inline(x)+"</li>").join("")+"</ul>";continue;}
  if(l.trim()){h+="<p>"+inline(l)+"</p>";} i++;}
 return h;}
const WORDS={auto_respond:"Answered automatically",escalate:"Sent to a person",block:"Blocked by a guardrail"};
function msg(t){document.getElementById("msg").textContent=t||"";}
let killOn=null;
function showKill(on){killOn=on; const b=document.getElementById("killbadge"), k=document.getElementById("killbtn");
 b.className="badge "+(on?"on":"off");
 b.textContent=on?"ON: every ticket goes to a person":"Off: automatic replies are allowed";
 k.textContent=on?"Turn the kill switch off":"Turn the kill switch on"; k.className=on?"":"danger"; k.disabled=false;}
function checkKill(){fetch("/health").then(r=>r.json()).then(j=>showKill(j.kill_switch_on)).catch(()=>{
 document.getElementById("killbadge").textContent="The system did not answer. Is it still running? (README step 7)";});}
async function flipKill(){
 const k=document.getElementById("killbtn"), m=document.getElementById("killmsg"); k.disabled=true; m.textContent="";
 try{const r=await fetch("/kill-switch",{method:"POST",headers:{"Content-Type":"application/json"},
   body:JSON.stringify({on:!killOn})}); const j=await r.json();
  if(!r.ok){m.textContent="The kill switch could not be changed.";k.disabled=false;return;}
  showKill(j.kill_switch_on); m.textContent=j.note||"";}
 catch(e){m.textContent="The system did not answer. Is it still running? (README step 7)";k.disabled=false;}
}
checkKill(); setInterval(checkKill,5000);   // also shows a change made with the README's PowerShell commands
async function startCharts(){
 const b=document.getElementById("chartbtn"), m=document.getElementById("chartmsg");
 m.textContent=""; document.getElementById("chartdone").innerHTML=""; b.disabled=true;
 try{const r=await fetch("/live-charts",{method:"POST"}); const j=await r.json();
  if(!r.ok){m.textContent=j.detail||"The live charts could not start.";b.disabled=false;return;}
  chartPoll();}
 catch(e){m.textContent="The system did not answer. Is it still running? (README step 7)";b.disabled=false;}
}
async function chartPoll(){
 const j=await (await fetch("/live-charts")).json(), log=document.getElementById("chartlog");
 log.style.display="block"; log.textContent=j.lines.join("\n")+(j.status==="starting"?"\n…":"");
 log.scrollTop=log.scrollHeight;
 if(j.status==="starting"){setTimeout(chartPoll,2000);return;}
 document.getElementById("chartbtn").disabled=false;
 if(j.status==="ready")document.getElementById("chartdone").innerHTML='<p class="ready">Ready: the charts start '+
  'from zero. <a href="'+j.dashboard+'" target="_blank">Open the Grafana dashboard</a>, then choose a ticket file below.</p>';
 else document.getElementById("chartmsg").textContent="The live charts did not start. The lines above say why.";
}
async function run(){
 const f=document.getElementById("file").files[0];
 if(!f){msg("Choose a ticket file first.");return;}
 msg(""); document.getElementById("run").disabled=true;
 const fd=new FormData(); fd.append("file",f);
 try{const r=await fetch("/runs",{method:"POST",body:fd}); const j=await r.json();
  if(!r.ok){msg(j.detail||"The run could not start.");document.getElementById("run").disabled=false;return;}
  document.getElementById("done").style.display="none"; poll(j.job_id);}
 catch(e){msg("The system did not answer. Is it still running? (README step 7)");document.getElementById("run").disabled=false;}
}
async function poll(id){
 const j=await (await fetch("/runs/"+id)).json();
 document.getElementById("progress").style.display="block";
 document.getElementById("line").textContent=j.file+": "+j.done+" of "+j.total+" tickets processed"+
  (j.status==="running"?"…":j.status==="done"?". Finished.":". Stopped: "+j.error);
 document.getElementById("fill").style.width=(j.total?100*j.done/j.total:0)+"%";
 document.getElementById("c_auto").textContent=j.counts.auto_respond||0;
 document.getElementById("c_esc").textContent=j.counts.escalate||0;
 document.getElementById("c_block").textContent=j.counts.block||0;
 const tb=document.getElementById("recent"); tb.innerHTML="";
 for(const t of j.recent){const tr=document.createElement("tr");
  for(const v of [t.ticket_id,WORDS[t.action]||t.action,t.label||"-"]){const td=document.createElement("td");td.textContent=v;tr.appendChild(td);}
  tb.appendChild(tr);}
 if(j.status==="running"){setTimeout(()=>poll(id),2000);return;}
 document.getElementById("run").disabled=false;
 if(j.status==="done"){document.getElementById("done").style.display="block";
  document.getElementById("files").textContent="Saved in the project: "+j.results_file+" and "+j.report_file+
   ". Check it against the decision log with: python scripts/check_decision_log.py";
  document.getElementById("report").innerHTML=md(j.report);}
 else msg("The run stopped: "+j.error);
}
</script></body></html>
"""
