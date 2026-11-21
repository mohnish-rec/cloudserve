# start_live_charts.ps1 - start Prometheus with empty charts, make sure Grafana is running, and open the dashboard.
# Start it with the "Start the live charts from zero" button on the system's web page (http://127.0.0.1:8000), or by
# double-clicking start_live_charts.bat in the project folder (README: Optional: watch it live).
# Every time it runs, it stops any Prometheus already running and deletes the numbers Prometheus collected before
# (its own "data" folder inside C:\prometheus\prometheus-...), so the charts start from zero.
# It never touches the project's own data folder (the tickets) or the decision log.
param([string]$PrometheusFolder = "", [switch]$FromPage)

$ErrorActionPreference = "Stop"
$project = Split-Path -Parent $PSScriptRoot
$settings = Join-Path $project "monitoring\prometheus.yml"
$dashboard = "http://localhost:3000/d/cloudserve-triage?orgId=1&from=now-15m&to=now&refresh=10s"

function Say($text, $colour = "White") {
    if ($FromPage) { [Console]::Out.WriteLine($text) }    # the web page shows these lines
    else { Write-Host $text -ForegroundColor $colour }
}
function Fetch($url) {
    try { return Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 3 } catch { return $null }
}

Say ""
Say "Starting the live charts (Prometheus and Grafana) with no earlier numbers..." "Cyan"

# 1. Find Prometheus (unzipped into C:\prometheus in the README).
if (-not $PrometheusFolder) {
    $found = Get-ChildItem -Path "C:\prometheus" -Directory -Filter "prometheus-*" -ErrorAction SilentlyContinue |
        Sort-Object Name -Descending | Select-Object -First 1
    if ($found) { $PrometheusFolder = $found.FullName }
}
$exe = if ($PrometheusFolder) { Join-Path $PrometheusFolder "prometheus.exe" } else { "" }
if (-not $exe -or -not (Test-Path $exe)) {
    Say "Prometheus was not found in C:\prometheus. Follow 'Optional: watch it live', step 1, in the README first." "Red"
    exit 1
}

# 2. Stop any Prometheus that is already running, so its numbers can be deleted.
$running = Get-Process -Name "prometheus" -ErrorAction SilentlyContinue
if ($running) {
    Say "Stopping the Prometheus that was already running..."
    $running | Stop-Process -Force
    $running | Wait-Process -Timeout 15 -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

# 3. Delete the numbers it collected before (only Prometheus's own data folder).
$old = Join-Path $PrometheusFolder "data"
if (Test-Path $old) {
    try {
        Remove-Item -Recurse -Force $old
        Say "Cleared the earlier chart numbers."
    } catch {
        Say "Could not clear the earlier numbers: $($_.Exception.Message)" "Red"
        Say "Close any window that is still running Prometheus, then double-click start_live_charts.bat again." "Red"
        exit 1
    }
}

# 4. Start Prometheus in its own small window (minimised). Closing that window stops Prometheus.
Start-Process -FilePath $exe -WorkingDirectory $PrometheusFolder -WindowStyle Minimized `
    -ArgumentList "--config.file=`"$settings`"", "--web.listen-address=127.0.0.1:9090"
$ready = $false
foreach ($i in 1..30) {
    if (Fetch "http://127.0.0.1:9090/-/ready") { $ready = $true; break }
    Start-Sleep -Seconds 1
}
if (-not $ready) {
    Say "Prometheus did not start. Open its window (on the taskbar) to see why." "Red"
    exit 1
}
Say "Prometheus is running (minimised on the taskbar; leave it open)." "Green"

# 5. Make sure Grafana is running. It is a Windows service that normally starts with Windows.
$grafana = Get-Service -Name "Grafana" -ErrorAction SilentlyContinue
if (-not $grafana) { $grafana = Get-Service -DisplayName "*Grafana*" -ErrorAction SilentlyContinue | Select-Object -First 1 }
if (-not $grafana) {
    Say "Grafana is not installed. Follow 'Optional: watch it live', step 3, in the README." "Red"
} elseif ($grafana.Status -ne "Running") {
    Say "Starting Grafana. If Windows asks for permission, press Yes."
    try {
        Start-Process powershell -Verb RunAs -Wait -WindowStyle Hidden `
            -ArgumentList "-NoProfile -Command Start-Service -Name '$($grafana.Name)'"
    } catch {
        Say "Grafana was not started (permission was not given)." "Red"
    }
}
foreach ($i in 1..30) {
    if (Fetch "http://localhost:3000/api/health") { break }
    Start-Sleep -Seconds 1
}
if (Fetch "http://localhost:3000/api/health") {
    if ($FromPage) { Say "Grafana is running." "Green" }
    else { Say "Grafana is running. Opening the dashboard in your browser..." "Green"; Start-Process $dashboard }
} else {
    Say "Grafana is not answering at http://localhost:3000 yet." "Red"
}

# 6. Wait until Prometheus can read the system, then 30 seconds more, so the charts start from 0.
Say ""
if ($FromPage) {
    # started from the system's own page: the system is running and its numbers were just set back to 0
} elseif (Fetch "http://127.0.0.1:8001/metrics") {
    Say "The system is already running. For every chart to start from zero, restart it now:" "Yellow"
    Say "press Ctrl+C in its window, then run: python -m src.api" "Yellow"
} else {
    Say "Now start the system (README step 7: python -m src.api). This window will tell you when to send tickets." "Yellow"
}
Say "Waiting for Prometheus to reach the system..."
$up = $false
foreach ($i in 1..600) {
    $r = Fetch "http://127.0.0.1:9090/api/v1/targets"
    if ($r -and $r.Content -match '"health":"up"') { $up = $true; break }
    Start-Sleep -Seconds 2
}
if (-not $up) {
    Say "Prometheus has not reached the system after 20 minutes. Is it running (README step 7)?" "Red"
    exit 1
}
Say "Prometheus has reached the system. Waiting 30 seconds more so the charts start from 0..."
Start-Sleep -Seconds 30
Say ""
Say "READY: you can send tickets now. They will appear on the dashboard." "Green"
if (-not $FromPage) { Say "You can close this window. Prometheus keeps running in its own window; close that one to stop it." }
exit 0
