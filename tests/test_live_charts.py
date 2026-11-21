"""The web page's "Start the live charts from zero" button (src/live_charts.py), with a fake script: no PowerShell,
Prometheus or Grafana is started by these tests."""
import time

import pytest

from src.live_charts import SCRIPT, LiveCharts


def wait(charts):
    for _ in range(200):
        if charts.status()["status"] != "starting":
            return charts.status()
        time.sleep(0.01)
    raise AssertionError("never finished")


def test_it_sets_the_numbers_to_zero_then_runs_the_script_and_shows_its_lines():
    seen, resets = [], []

    def script(command, say):
        seen.append(command)
        say("Prometheus is running.")
        say("READY: you can send tickets now.")
        return 0

    charts = LiveCharts(runner=script, reset=lambda: resets.append(1), windows=True)
    charts.start()
    status = wait(charts)
    assert status["status"] == "ready" and resets == [1]
    assert "READY: you can send tickets now." in status["lines"]
    assert str(SCRIPT) in seen[0] and "-FromPage" in seen[0]
    assert status["dashboard"].startswith("http://localhost:3000/d/cloudserve-triage")


def test_a_script_that_fails_is_shown_as_failed():
    charts = LiveCharts(runner=lambda command, say: (say("Prometheus was not found in C:\\prometheus."), 1)[1],
                        reset=lambda: None, windows=True)
    charts.start()
    status = wait(charts)
    assert status["status"] == "failed" and "Prometheus was not found" in status["lines"][-1]


def test_an_error_is_shown_in_plain_words():
    def broken(command, say):
        raise FileNotFoundError("powershell")
    charts = LiveCharts(runner=broken, reset=lambda: None, windows=True)
    charts.start()
    status = wait(charts)
    assert status["status"] == "failed" and "Could not start the live charts" in status["lines"][-1]


def test_only_one_start_at_a_time():
    def slow(command, say):
        time.sleep(0.3)
        return 0
    charts = LiveCharts(runner=slow, reset=lambda: None, windows=True)
    charts.start()
    with pytest.raises(RuntimeError, match="already being started"):
        charts.start()
    wait(charts)


def test_outside_windows_it_says_to_follow_the_readme():
    with pytest.raises(RuntimeError, match="Windows only"):
        LiveCharts(runner=lambda c, s: 0, reset=lambda: None, windows=False).start()


def test_reset_puts_every_chart_number_back_to_zero():
    metrics = pytest.importorskip("src.metrics")
    metrics.TICKETS.labels("email", "auto_respond").inc()
    metrics.GUARDRAIL.labels("private_data").inc()
    metrics.CONFIDENCE.observe(0.95)
    metrics.LATENCY.observe(1.5)
    metrics.reset()
    values = {}
    for metric in (metrics.TICKETS, metrics.GUARDRAIL, metrics.CONFIDENCE, metrics.LATENCY):
        for family in metric.collect():
            for s in family.samples:
                if not s.name.endswith("_created"):
                    values[(s.name, tuple(sorted(s.labels.items())))] = s.value
    assert values and all(v == 0 for v in values.values())
    assert any(name == "tickets_processed_total" for name, _ in values)   # the series still start at 0
