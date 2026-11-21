"""The web page's "Start the live charts from zero" button (README: Optional: watch it live).

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
Pressing the button sets the system's own chart numbers back to 0 (src/metrics.py reset) and runs
scripts/start_live_charts.ps1, which stops Prometheus, deletes the numbers it collected before, starts it again,
makes sure Grafana is running, and waits until Prometheus has read the system plus 30 seconds. The page shows each
line the script prints. Nothing here makes a decision about a ticket. Windows only, like the README.
"""
import os
import subprocess
import threading
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "start_live_charts.ps1"
DASHBOARD = "http://localhost:3000/d/cloudserve-triage?orgId=1&from=now-15m&to=now&refresh=10s"


def run_script(command, say) -> int:
    """Run the PowerShell script with no window of its own, pass each line it prints to say(), return its exit code."""
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                            text=True, encoding="utf-8", errors="replace", creationflags=flags, cwd=str(ROOT))
    for line in proc.stdout:
        if line.strip():
            say(line.rstrip())
    return proc.wait()


class LiveCharts:
    """One start at a time; keeps the lines the script printed for the page to show."""

    def __init__(self, runner=None, reset=None, windows=None):
        self.runner = runner or run_script          # tests pass a fake
        self.reset = reset
        self.windows = (os.name == "nt") if windows is None else windows
        self.lock = threading.Lock()
        self.state = {"status": "not started", "lines": [], "dashboard": DASHBOARD}

    def _reset(self):
        if self.reset is not None:
            return self.reset()
        from src import metrics
        metrics.reset()

    def start(self) -> dict:
        if not self.windows:
            raise RuntimeError("This button works on Windows only. Start Prometheus and Grafana as the README shows.")
        with self.lock:
            if self.state["status"] == "starting":
                raise RuntimeError("The live charts are already being started. Wait for this one to finish.")
            self.state = {"status": "starting", "lines": [], "dashboard": DASHBOARD,
                          "started": datetime.now(timezone.utc).isoformat()}
        threading.Thread(target=self._work, daemon=True).start()
        return self.status()

    def _say(self, line: str):
        with self.lock:
            self.state["lines"].append(line)

    def _work(self):
        try:
            self._reset()
            self._say("Set the system's chart numbers back to 0.")
            command = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SCRIPT), "-FromPage"]
            code = self.runner(command, self._say)
            with self.lock:
                self.state["status"] = "ready" if code == 0 else "failed"
        except Exception as e:  # noqa: BLE001 - the page must say what went wrong
            with self.lock:
                self.state["lines"].append(f"Could not start the live charts: {type(e).__name__}: {e}")
                self.state["status"] = "failed"

    def status(self) -> dict:
        with self.lock:
            return {**self.state, "lines": list(self.state["lines"])}
