"""11 Nov 2026, PR-01 v1.7 (agreed with Mohnish Grover after the v1.6 run): the main article is sent whole (every step,
Note and Common cause, minus Symptoms), word for word; a second article adds its steps only; the grounding checker sees
Common causes under the same line the customer sees."""
import json

import pytest

import src.generate as G
from src.guardrails import _shown, tone_and_scope
from src.retrieve import Passage, load_documents

V17 = "PR-01_draft_reply_v1.7.md"
DOCS = {d["doc_id"]: d for d in load_documents()}


@pytest.fixture
def v17(monkeypatch):
    real = G.load_prompt
    monkeypatch.setattr(G, "EXTRACTIVE", True)
    monkeypatch.setattr(G, "ALL_STEPS", True)
    monkeypatch.setattr(G, "WHOLE_ARTICLE", True)
    monkeypatch.setattr(G, "load_prompt", lambda name=None: real(V17))


def choose(pieces):
    raw = json.dumps({"answered": True, "pieces": pieces, "sure": "sure", "summary": "s", "unsure_about": ""})
    return lambda messages, model: G.Reply(raw)


def passages(*doc_ids):
    return [Passage(d, DOCS[d]["title"], DOCS[d].get("category", ""), "x", 0.7, 1, i)
            for i, d in enumerate(doc_ids, 1)]


def pieces(doc_id):
    return G.article_pieces(DOCS[doc_id]["content"])[1]


def test_v17_prompt_switches_on_the_whole_article():
    text = (G.PROMPT_DIR / V17).read_text(encoding="utf-8")
    assert "**Version:** 1.7" in text and "**Pieces:** whole article" in text and "**Steps:** all" in text


def test_the_decisive_note_now_reaches_the_customer(v17):
    """Q31: 'must be resumed manually' was in only 2 of 8 v1.6 replies."""
    P = passages("DOC-INT-002")
    d = G.generate("Log forwarding stopped and has not resumed", "integration_help", P, call=choose(["1.R1"]), sleep=None)
    reply = G.with_notice(d, P)
    assert "Forwarding pauses after one hour of consecutive failures and must be resumed manually" in reply


@pytest.mark.parametrize("doc_id", sorted(DOCS))
def test_the_whole_article_is_sent_word_for_word_and_fits_the_length_rule(v17, doc_id):
    P = passages(doc_id)
    d = G.generate("question", "x", P, call=choose(["1.R1"]), sleep=None)
    reply = G.with_notice(d, P)
    assert [s["piece"].split(".")[1] for s in d.sentences] == \
        [c for c, _ in pieces(doc_id) if c[0] == "R"] + [c for c, _ in pieces(doc_id) if c[0] == "N"] + \
        [c for c, _ in pieces(doc_id) if c[0] == "C"]
    article = " ".join(DOCS[doc_id]["content"].split())
    assert all(l[2:] in article for l in reply.splitlines() if l.startswith("- "))
    check = tone_and_scope(reply)
    assert "too long" not in check.detail, (doc_id, check.detail)


def test_a_second_article_adds_its_steps_only(v17):
    P = passages("DOC-DEPLOY-002", "DOC-DEPLOY-001")
    d = G.generate("roll back", "rollback_request", P, call=choose(["1.R1", "2.R1"]), sleep=None)
    second = [s["piece"] for s in d.sentences if s["piece"].startswith("2.")]
    assert second and all(".R" in p for p in second)
    assert any(".N" in s["piece"] for s in d.sentences if s["piece"].startswith("1."))


def test_the_checker_sees_causes_under_the_same_line_as_the_customer(v17):
    P = passages("DOC-PERF-003")
    d = G.generate("no connection available", "database_issue", P, call=choose(["1.R1"]), sleep=None)
    cause = next(s for s in d.sentences if ".C" in s["piece"])
    step = next(s for s in d.sentences if ".R" in s["piece"])
    assert _shown(cause).startswith(f'(listed under "{G.CAUSES}")') and _shown(step) == step["text"]
