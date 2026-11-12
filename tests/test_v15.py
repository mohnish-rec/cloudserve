"""11 Nov 2026, PR-01 v1.5: complete replies. The model is told to include every Resolution step of the chosen article,
keeping steps that begin with "If". These tests check the prompt says so, and that a complete reply is still copied word
for word and still passes the length rule (tone and scope) for every one of the 29 articles."""
import json

import pytest

import src.generate as G
from src.guardrails import tone_and_scope
from src.retrieve import Passage, load_documents

V15 = "PR-01_draft_reply_v1.5.md"
DOCS = {d["doc_id"]: d for d in load_documents()}


@pytest.fixture
def v15(monkeypatch):
    real = G.load_prompt
    monkeypatch.setattr(G, "EXTRACTIVE", True)
    monkeypatch.setattr(G, "load_prompt", lambda name=None: real(V15))


def choose(pieces):
    raw = json.dumps({"answered": True, "pieces": pieces, "sure": "sure", "summary": "s", "unsure_about": ""})
    return lambda messages, model: G.Reply(raw)


def passage(doc_id):
    d = DOCS[doc_id]
    return [Passage(doc_id, d["title"], d.get("category", ""), "x", 0.7, 1, 1)]


def test_v15_is_extractive_and_asks_for_every_resolution_step():
    text = (G.PROMPT_DIR / V15).read_text(encoding="utf-8")
    assert "**Mode:** extractive" in text and "**Version:** 1.5" in text
    assert "Include every Resolution step" in text and 'Keep steps that begin with "If"' in text
    system, user = G.load_prompt(V15)
    assert "{passages}" in user and "{ticket}" in user and "word for word" in system


def test_the_rollback_reply_keeps_the_database_migration_step_word_for_word(v15):
    d = G.generate("Bad release, we need to go back", "rollback_request", passage("DOC-DEPLOY-002"),
                   call=choose(["1.R1", "1.R2", "1.R3", "1.R4"]), sleep=None)
    reply = G.with_notice(d, passage("DOC-DEPLOY-002"))
    step = ("If the release included a database migration, roll the migration back before the service, "
            "or the older code will encounter a schema it does not expect.")
    assert d.ok and step in reply


@pytest.mark.parametrize("doc_id", sorted(DOCS))
def test_a_complete_reply_from_any_article_passes_the_length_rule(v15, doc_id):
    _, pieces = G.article_pieces(DOCS[doc_id]["content"])
    order = [c for c, _ in pieces if c.startswith("R")] + [c for c, _ in pieces if not c.startswith("R")]
    labels = ["1." + c for c in order][:8]
    d = G.generate("question", "x", passage(doc_id), call=choose(labels), sleep=None)
    reply = G.with_notice(d, passage(doc_id))
    assert d.ok, doc_id
    check = tone_and_scope(reply)
    assert "too long" not in check.detail, (doc_id, check.detail)


def test_a_complete_proration_reply_mentions_refunds_so_it_goes_to_a_person(v15):
    """Found 11 Nov by the test above: DOC-BILL-002 steps 3 and 4 explain the refund policy in Ines's words. The tone
    guardrail cannot tell policy from a promise, so the reply is blocked and a person answers. Kept on purpose
    (Governance Framework: commitments about refunds are not the system's to make)."""
    d = G.generate("why was my upgrade charged like this?", "billing_query", passage("DOC-BILL-002"),
                   call=choose(["1.R1", "1.R2", "1.R3", "1.R4"]), sleep=None)
    check = tone_and_scope(G.with_notice(d, passage("DOC-BILL-002")))
    assert not check.passed and "refund" in check.detail


def test_every_piece_appears_exactly_as_written_in_the_article_with_nothing_added(v15):
    """A Common cause is a list item without a full stop in the article; the reply must not add one."""
    d = G.generate("export is missing records", "data_export", passage("DOC-DATA-001"),
                   call=choose(["1.R1", "1.C3", "1.N1"]), sleep=None)
    reply = G.with_notice(d, passage("DOC-DATA-001"))
    _, pieces = G.article_pieces(DOCS["DOC-DATA-001"]["content"])
    text = dict(pieces)
    for code in ("R1", "C3", "N1"):
        assert f"- {text[code]}\n" in reply + "\n", code
    assert "- The export captured a snapshot taken when the job started\n" in reply
