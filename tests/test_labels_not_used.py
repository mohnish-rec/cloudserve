"""13 Nov 2026 (Mohnish Grover): the system decides every ticket from the customer's message alone; the labels are
only used afterwards, to measure the run. Dataset Guide, "What each label is for": every label is listed under
"Use it to measure" (intent: classification precision; expected_route: routing accuracy; must_not_auto_respond: a
safety check), and the Project Brief asks the system to PREDICT intent and urgency. The hidden set "uses the same
schema", so it may carry labels: these tests show that would make no difference to any decision."""
import copy
import json
import re
from dataclasses import fields
from pathlib import Path

from src.ingest import Ticket, normalise

ROOT = Path(__file__).resolve().parent.parent
DEV = json.loads((ROOT / "data" / "development_tickets.json").read_text(encoding="utf-8-sig"))
LABEL_FIELDS = ("intent", "urgency", "expected_route", "answerable_from_docs", "expected_doc_ids",
                "must_not_auto_respond")


def test_the_ticket_the_system_works_with_has_no_labels_or_history():
    names = {f.name for f in fields(Ticket)}
    assert not names & {"labels", "history", *LABEL_FIELDS}


def test_removing_the_labels_changes_nothing_the_system_receives():
    for i, raw in enumerate(DEV, start=1):
        bare = {k: v for k, v in raw.items() if k not in ("labels", "history")}
        assert normalise(raw, i) == normalise(bare, i), raw["ticket_id"]


def test_wrong_labels_change_nothing_the_system_receives():
    """Every label reversed (a person instead of automatic, must-not flipped, another type): the same ticket."""
    for i, raw in enumerate(DEV, start=1):
        bad = copy.deepcopy(raw)
        lab = bad["labels"]
        lab["expected_route"] = "auto_respond" if lab["expected_route"] != "auto_respond" else "escalate"
        lab["must_not_auto_respond"] = not lab["must_not_auto_respond"]
        lab["intent"], lab["urgency"], lab["expected_doc_ids"] = "unclear_request", "low", ["DOC-NONE"]
        assert normalise(raw, i) == normalise(bad, i), raw["ticket_id"]


def test_only_the_report_reads_the_label_fields():
    """No part of the decision path (classify, safety, search, route, write, guardrails) names a label field."""
    pattern = re.compile(r"[\"'](labels|history|expected_route|must_not_auto_respond|expected_doc_ids|"
                         r"answerable_from_docs)[\"']")
    readers = sorted(p.name for p in (ROOT / "src").glob("*.py") if pattern.search(p.read_text(encoding="utf-8")))
    assert readers == ["report.py"]
