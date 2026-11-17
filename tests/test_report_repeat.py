"""17 Nov 2026: the metrics report counts repeat contacts (Evaluation Framework, Business outcomes).

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
"""
from types import SimpleNamespace as NS

from src.report import repeat_contacts


def test_follow_ups_and_the_baseline_are_counted():
    outcomes = [NS(reason="Sent to a person because follow-up: the same customer had an automatic reply", action="escalate"),
                NS(reason="Answered automatically", action="auto_respond"),
                NS(reason="Answered automatically", action="auto_respond")]
    raw = {"A": {"history": {"repeat_contact": True}}, "B": {"history": {"repeat_contact": False}},
           "C": {"history": {"repeat_contact": False}}}
    line = repeat_contacts(outcomes, raw)
    assert "1 of 3 tickets" in line and "1 of them went to a person" in line and "1 of 3 (33.3%)" in line


def test_a_file_without_history_still_gets_the_count():
    line = repeat_contacts([NS(reason="Answered automatically", action="auto_respond")], {"A": {}})
    assert "0 of 1 tickets" in line and "Baseline" not in line
