"""The unattended run (A8, A9, FR-11, FR-12) on a small file, with fake models and search."""
import json
import os
import subprocess
import sys

import pytest

import src.run_evaluation as R
from src import logging_store as log
from src.pipeline import process
from tests.test_pipeline import FITS, REPLY, Classifier, Search, models

ROOT = R.ROOT


def tickets_file(tmp_path):
    rows = []
    for tid, body, intent, route in [("V-1", "How do I roll back to an earlier revision?", "rollback_request", "auto_respond"),
                                     ("V-2", "I want a refund for last month", "billing_query", "escalate"),
                                     ("V-3", "BOOM", "rollback_request", "escalate"),
                                     ("V-4", "   ", "unclear_request", "escalate")]:
        rows.append({"ticket_id": tid, "channel": "email", "subject": "", "body": body,
                     "received_at": "2026-11-08T09:00:00Z", "customer_id": "C", "customer_tier": "business",
                     "customer_region": "europe", "language_fluency": "fluent",
                     "labels": {"intent": intent, "urgency": "medium", "expected_route": route,
                                "answerable_from_docs": route == "auto_respond", "must_not_auto_respond": False,
                                "expected_doc_ids": ["DOC-DEPLOY-002"] if route == "auto_respond" else []}})
    p = tmp_path / "tickets.json"
    p.write_text(json.dumps(rows), encoding="utf-8")
    return p


@pytest.fixture
def fake(tmp_path, monkeypatch):
    url = f"sqlite:///{(tmp_path / 'decisions.db').as_posix()}"
    monkeypatch.setenv("DATABASE_URL", url)
    subprocess.run([sys.executable, "scripts/setup_decision_log.py"], cwd=ROOT,
                   env={**os.environ, "DATABASE_URL": url}, check=True, capture_output=True)
    monkeypatch.setattr(R.Retriever, "from_store", classmethod(lambda cls, **k: Search()))
    monkeypatch.setattr(R.TicketClassifier, "load", classmethod(lambda cls, **k: Classifier()))

    def fake_process(t, classifier, retriever):
        if "BOOM" in t.text:
            raise RuntimeError("something unexpected")
        return process(t, classifier, retriever, call=models(REPLY, FITS), sleep=lambda s: None,
                       kill_switch_file=tmp_path / "off")
    monkeypatch.setattr(R, "process", fake_process)
    return url


def test_one_command_processes_every_ticket_and_writes_the_report(tmp_path, fake):
    out = tmp_path / "out" / "run.json"
    R.run_evaluation(str(tickets_file(tmp_path)), str(out))
    data = json.loads(out.read_text(encoding="utf-8"))
    actions = {r["ticket_id"]: r["action"] for r in data["results"]}
    assert actions == {"V-1": "auto_respond", "V-2": "escalate", "V-3": "escalate", "V-4": "escalate"}
    assert "unexpected error" in next(r["reason"] for r in data["results"] if r["ticket_id"] == "V-3")
    md = (tmp_path / "out" / "run_metrics.md").read_text(encoding="utf-8")
    for must in ["## Volume", "First contact resolution", "95th percentile", "reconciles", "Retrieval hit rate",
                 "Citation accuracy", "precision", "Calibration", "Results by customer group", "Guardrail activations"]:
        assert must in md, must


def test_every_ticket_has_one_final_outcome_in_the_log(tmp_path, fake):
    meta = R.run_evaluation(str(tickets_file(tmp_path)), str(tmp_path / "run.json"))
    con = log.connect(fake)
    rows = log.read(con, meta["run_id"])
    assert sorted(r["ticket_id"] for r in rows if r["stage"] == "outcome") == ["V-1", "V-2", "V-3", "V-4"]
    assert {"classification", "routing", "generation", "validation"} <= {r["stage"] for r in rows}
    assert all(r["reason"] for r in rows)


def test_running_the_same_file_twice_gives_the_same_decisions_and_duplicates_nothing(tmp_path, fake):
    f = str(tickets_file(tmp_path))
    a = R.run_evaluation(f, str(tmp_path / "a.json"))
    b = R.run_evaluation(f, str(tmp_path / "b.json"))
    con = log.connect(fake)
    first = [(r["ticket_id"], r["action_taken"]) for r in log.read(con, a["run_id"], "outcome")]
    second = [(r["ticket_id"], r["action_taken"]) for r in log.read(con, b["run_id"], "outcome")]
    assert a["run_id"] != b["run_id"] and first == second and len(first) == 4


def test_when_the_provider_keeps_failing_the_rest_go_to_a_person_without_waiting(tmp_path, fake, monkeypatch):
    from src.pipeline import Outcome
    calls = []

    def down(t, classifier, retriever):
        calls.append(t.ticket_id)
        return Outcome(t.ticket_id, "escalate", "Needs a specialist", "medium",
                       "Sent to a person because model unavailable: HTTP 429.", "ack")
    monkeypatch.setattr(R, "process", down)
    rows = [{"ticket_id": f"P-{i}", "channel": "email", "subject": "", "body": "roll back please",
             "received_at": "2026-11-08T09:00:00Z", "customer_id": "C", "customer_tier": "business",
             "customer_region": "europe", "language_fluency": "fluent"} for i in range(6)]
    f = tmp_path / "six.json"
    f.write_text(json.dumps(rows), encoding="utf-8")
    R.run_evaluation(str(f), str(tmp_path / "six_out.json"))
    data = json.loads((tmp_path / "six_out.json").read_text(encoding="utf-8"))["results"]
    assert len(calls) == 3 and len(data) == 6                     # three tried, the rest not attempted
    assert all("circuit open" in r["reason"] for r in data[3:])


def test_the_cache_is_off_unless_a_development_run_asks_for_it(tmp_path, fake):
    meta = R.run_evaluation(str(tickets_file(tmp_path)), str(tmp_path / "plain.json"))
    assert meta["reply_cache"].startswith("off") and os.environ["REPLY_CACHE"] == "off"
    meta = R.run_evaluation(str(tickets_file(tmp_path)), str(tmp_path / "dev.json"), use_cache=True)
    assert meta["reply_cache"].startswith("on")
    os.environ["REPLY_CACHE"] = "off"


def test_progress_is_reported_after_every_ticket_without_changing_a_decision(tmp_path, fake):
    seen = []
    out = tmp_path / "run.json"
    R.run_evaluation(str(tickets_file(tmp_path)), str(out), progress=lambda *a: seen.append(a))
    assert [a[0] for a in seen] == [1, 2, 3, 4] and all(a[1] == 4 for a in seen)
    data = json.loads(out.read_text(encoding="utf-8"))
    assert {a[2]: a[3] for a in seen} == {r["ticket_id"]: r["action"] for r in data["results"]}


def test_a_broken_progress_report_never_stops_the_run(tmp_path, fake):
    def broken(*a):
        raise RuntimeError("the page went away")
    meta = R.run_evaluation(str(tickets_file(tmp_path)), str(tmp_path / "run.json"), progress=broken)
    assert json.loads((tmp_path / "run.json").read_text(encoding="utf-8"))["results"] and meta["run_id"]


def test_progress_gives_each_tickets_full_result_with_the_run_id(tmp_path, fake):
    """21 Nov 2026: the web page's ticket details use the full result the run reports after each ticket."""
    seen = []
    meta = R.run_evaluation(str(tickets_file(tmp_path)), str(tmp_path / "run.json"), progress=lambda *a: seen.append(a))
    results = {a[2]: a[5] for a in seen}
    assert all(r["run_id"] == meta["run_id"] for r in results.values())
    assert results["V-1"]["action"] == "auto_respond" and results["V-1"]["sent_text"] and results["V-1"]["guardrails"]


def test_the_decision_log_trail_and_check_for_the_web_page(tmp_path, fake):
    """The page's ticket details (every row for one ticket) and README step 10 on the page (run_check)."""
    meta = R.run_evaluation(str(tickets_file(tmp_path)), str(tmp_path / "run.json"))
    con = log.connect(fake)
    trail = log.ticket_trail(con, meta["run_id"], "V-1")
    assert [r["stage"] for r in trail][-1] == "outcome" and trail[0]["stage"] == "classification"
    assert isinstance(trail[-1]["requirement_ids"], list) and isinstance(trail[-1]["guardrails"], dict)
    check = log.run_check(con, meta["run_id"])
    assert check["tickets"] == check["outcomes"] == check["once"] == 4
    assert check["by_action"] == {"auto_respond": 1, "escalate": 3}


def test_the_report_names_every_measure_and_target_of_the_evaluation_framework(tmp_path, fake):
    R.run_evaluation(str(tickets_file(tmp_path)), str(tmp_path / "run.json"))
    md = (tmp_path / "run_metrics.md").read_text(encoding="utf-8")
    for measure, target in [("First contact resolution", "60% or better"), ("Mean time to first reply", "Under 5 minutes"),
                            ("Customer satisfaction", "4.0 or better"), ("Escalation rate", "30% or lower"),
                            ("Repeat contacts", "Halved"), ("Classification precision", "85% or better"),
                            ("Hallucination rate", "5% or lower"), ("Citation accuracy", "95% or better"),
                            ("Latency, 95th percentile", "Under 3 seconds"), ("Availability", "99.5% or better"),
                            ("Private data in outbound text", "Zero occurrences"),
                            ("Quality across customer groups", "Under five percentage points"),
                            ("Decision logging", "Complete coverage"), ("Confidence calibration", "within five points")]:
        assert measure in md and target in md, measure
    assert "## Why targets were missed" in md and "## Why some measures are not measured" in md
