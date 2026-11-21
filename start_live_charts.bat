@echo off
rem Double-click this file to start the live charts (Prometheus and Grafana) with no earlier numbers.
rem It runs scripts\start_live_charts.ps1; the README section "Optional: watch it live" explains it.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start_live_charts.ps1"
pause
