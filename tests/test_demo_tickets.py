"""17 Nov 2026: the demo tickets in the README cover every channel and carry no answer key (Build Specification,
section 06, steps 13 and 14).

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
"""
import json
from pathlib import Path

from src.ingest import load_tickets

FILE = Path(__file__).resolve().parent.parent / "data" / "samples" / "demo_tickets.json"


def test_one_ticket_per_channel_and_a_guardrail_ticket():
    raw = json.loads(FILE.read_text(encoding="utf-8"))
    assert {t["channel"] for t in raw} == {"email", "chat", "docs_comment", "forum"}
    assert any(t["ticket_id"] == "RT-01" for t in raw)
    assert not any("labels" in t or "history" in t for t in raw)


def test_the_demo_file_loads_like_any_ticket_file():
    assert len(load_tickets(FILE)) == 7
