"""Routing (FR-06, FR-07, FR-13, FR-16) and the decision log (FR-10). No models needed."""
import sqlite3
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError

from src import logging_store as log
from src.classify import Classification
from src.retrieve import Passage
from src.route import AUTO, DRAFT_READY, ESCALATE, SPECIALIST, queue_key, route
from src.safety import check

ROOT = Path(__file__).resolve().parent.parent
ARTICLE = [Passage("DOC-DEPLOY-003", "Rolling back", "deployments", "To roll back...", 0.71, 3.2, 1)]


def c(conf=0.97, intent="rollback_request", urgency="medium", fallback=False):
    return Classification(intent, conf, urgency, 0.6, ((intent, conf),), fallback, "")


@pytest.fixture
def off(tmp_path):
    return tmp_path / "kill_switch"          # does not exist: kill switch off


def test_confident_safe_ticket_with_an_article_is_answered(off):
    d = route("How do I revert to an earlier revision?", c(), check("How do I revert?"), ARTICLE,
              kill_switch_file=off, threshold=0.85)
    assert d.action == AUTO and d.label == "" and "DOC-DEPLOY-003" in d.reason


def test_just_under_the_threshold_gives_draft_ready(off):
    d = route("roll back please", c(0.70), check("roll back please"), ARTICLE, kill_switch_file=off, threshold=0.85)
    assert d.action == ESCALATE and d.label == DRAFT_READY and "70%" in d.reason


def test_safety_rule_or_no_article_or_low_confidence_needs_a_specialist(off):
    text = "One of our engineers pushed a key to a public repository"
    assert route(text, c(), check(text), ARTICLE, kill_switch_file=off).label == SPECIALIST
    assert route("roll back", c(), check("roll back"), [], kill_switch_file=off).label == SPECIALIST
    assert route("roll back", c(0.30), check("roll back"), ARTICLE, kill_switch_file=off).label == SPECIALIST
    assert route("", c(0.0, "unclear_request", fallback=True), check(""), [], kill_switch_file=off).label == SPECIALIST


def test_every_reason_is_listed_in_plain_words(off):
    text = "We need our data to remain within the EU"
    d = route(text, c(0.40, "data_residency"), check(text, "data_residency"), [], kill_switch_file=off)
    assert "safety rule" in d.reason and "no help article" in d.reason and "40%" in d.reason
    assert {"FR-03", "FR-05", "FR-06", "FR-07"} <= set(d.requirement_ids)


def test_same_input_same_decision(off):
    args = ("roll back my deploy", c(), check("roll back my deploy"), ARTICLE)
    assert route(*args, kill_switch_file=off) == route(*args, kill_switch_file=off)


def test_kill_switch_stops_automatic_replies_mid_run_without_a_restart(off):
    args = ("roll back my deploy", c(), check("roll back my deploy"), ARTICLE)
    assert route(*args, kill_switch_file=off).action == AUTO
    off.write_text("on")                                  # switched on between two tickets
    d = route(*args, kill_switch_file=off)
    assert d.action == ESCALATE and "kill switch" in d.reason and "FR-16" in d.requirement_ids
    off.unlink()
    assert route(*args, kill_switch_file=off).action == AUTO


def test_urgent_words_security_and_waiting_tickets_move_up_the_queue(off):
    calm = route("roll back please", c(urgency="low"), check("roll back"), ARTICLE, kill_switch_file=off)
    loud = route("Production is down for all our users", c(urgency="low"), check("x"), ARTICLE, kill_switch_file=off)
    leak = "pushed a key to a public repository"
    sec = route(leak, c(urgency="low"), check(leak), ARTICLE, kill_switch_file=off)
    now = datetime(2026, 11, 7, 12, 0, tzinfo=timezone.utc)
    old = route("roll back", c(urgency="low"), check("roll back"), ARTICLE, kill_switch_file=off,
                received_at=(now - timedelta(minutes=100)).isoformat(), now=now)
    assert calm.priority == "low" and loud.priority == "high" and sec.priority == "high"
    assert old.near_breach and old.priority == "high"
    assert queue_key(old) < queue_key(loud) < queue_key(calm)


@pytest.fixture
def db(tmp_path, monkeypatch):
    url = f"sqlite:///{(tmp_path / 'decisions.db').as_posix()}"
    monkeypatch.setenv("DATABASE_URL", url)
    subprocess.run([sys.executable, "scripts/setup_decision_log.py"], cwd=ROOT,
                   env={**__import__("os").environ, "DATABASE_URL": url}, check=True, capture_output=True)
    con = log.connect(url)
    yield con
    con.close()


def record(**kw):
    base = dict(run_id="r1", ticket_id="DEV-0001", stage="routing", input_summary="chat ticket, 90 characters",
                action_taken="escalate", label=SPECIALIST, reason="Sent to a person because no article matched.",
                requirement_ids=["FR-06"])
    return log.DecisionRecord(**{**base, **kw})


def test_decisions_are_written_and_read_back_with_their_reason(db):
    log.write(record(), db)
    log.write(record(ticket_id="DEV-0002", action_taken="auto_respond", label="", confidence=0.93,
                     threshold=0.85, sources_used=[{"doc_id": "DOC-DEPLOY-003", "score": 0.71}]), db)
    rows = log.read(db, "r1", "routing")
    assert [r["ticket_id"] for r in rows] == ["DEV-0001", "DEV-0002"]
    assert all(r["reason"] and r["decision_id"] for r in rows)


def test_a_record_that_breaks_the_schema_is_refused(db):
    for bad in (dict(label="maybe"), dict(confidence=1.7), dict(action_taken="ignore"), dict(reason="")):
        with pytest.raises(ValidationError):
            record(**bad)
    assert sqlite3.connect(":memory:") and log.read(db, "r1") == []
