"""Ingest (FR-01): every channel comes through in the same shape, and odd input never crashes it."""
import json
from dataclasses import fields
from pathlib import Path

from src.ingest import CHANNELS, Ticket, is_blocked, load_tickets, normalise

ROOT = Path(__file__).resolve().parent.parent


def test_all_four_channels_come_through_in_the_same_shape():
    tickets = load_tickets(ROOT / "data" / "validation_tickets.json")
    assert len(tickets) == 80
    assert {t.channel for t in tickets} == set(CHANNELS)
    for t in tickets:
        assert isinstance(t, Ticket) and t.text and not t.issues


def test_original_text_and_channel_are_kept():
    raw = {"ticket_id": "T-1", "channel": "email", "subject": "  Login\tproblem ",
           "body": "Cannot\n\nsign in", "customer_tier": "business",
           "customer_region": "europe", "language_fluency": "fluent"}
    t = normalise(raw)
    assert t.original_subject == "  Login\tproblem " and t.original_body == "Cannot\n\nsign in"
    assert t.subject == "Login problem" and t.body == "Cannot sign in" and t.channel == "email"
    assert t.text == "Login problem. Cannot sign in"


def test_chat_tickets_without_a_subject_use_the_body():
    t = normalise({"ticket_id": "T-2", "channel": "chat", "subject": "", "body": "help"})
    assert t.text == "help"


def test_missing_fields_empty_body_and_odd_characters_never_crash():
    for raw in [{}, None, "not a ticket", {"body": None}, {"body": "​\u0000  "},
                {"channel": "Live Chat", "body": "café – résumé \U0001F600"}]:
        t = normalise(raw, position=7)
        assert isinstance(t, Ticket)
    assert "empty body" in normalise({"body": "   "}).issues
    assert normalise({}, position=7).ticket_id == "UNKNOWN-0007"
    assert normalise({"channel": "Live Chat", "body": "x"}).channel == "chat"


def test_customer_name_and_answer_key_never_enter_the_ticket():
    names = {f.name for f in fields(Ticket)}
    assert "customer_name" not in names
    assert not names & {"labels", "history"}
    raw = json.loads((ROOT / "data" / "development_tickets.json").read_text(encoding="utf-8"))[0]
    assert raw["customer_name"] not in json.dumps(normalise(raw).__dict__)


def test_data_quality_checks_record_each_problem(tmp_path):
    t = normalise({"ticket_id": "T-3", "channel": "email", "body": "hi",
                   "customer_tier": "platinum", "customer_region": "mars",
                   "language_fluency": "fluent", "received_at": "yesterday"})
    assert "invalid customer_tier 'platinum'" in t.issues
    assert "invalid customer_region 'mars'" in t.issues
    assert "unreadable received_at" in t.issues
    assert t.customer_tier == "unknown" and not is_blocked(t)
    assert is_blocked(normalise({"ticket_id": "T-4", "body": ""}))
    f = tmp_path / "dup.json"
    f.write_text(json.dumps([{"ticket_id": "A", "body": "x"}, {"ticket_id": "A", "body": "y"}]))
    first, second = load_tickets(f)
    assert "duplicate ticket_id" not in first.issues and "duplicate ticket_id" in second.issues
