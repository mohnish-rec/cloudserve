"""11 Nov 2026, PR-01 v1.6 (decided by Mohnish Grover after the v1.5 run): the code adds every Resolution step of each
article the model answers from, in the article's order, and shows Common causes under their own code-written line.
Every piece is still Ines's own words, exactly as written."""
import json

import pytest

import src.generate as G
from src.guardrails import tone_and_scope
from src.retrieve import Passage, load_documents

V16 = "PR-01_draft_reply_v1.6.md"
DOCS = {d["doc_id"]: d for d in load_documents()}
MIGRATION = ("If the release included a database migration, roll the migration back before the service, "
             "or the older code will encounter a schema it does not expect.")


@pytest.fixture
def v16(monkeypatch):
    real = G.load_prompt
    monkeypatch.setattr(G, "EXTRACTIVE", True)
    monkeypatch.setattr(G, "ALL_STEPS", True)
    monkeypatch.setattr(G, "load_prompt", lambda name=None: real(V16))


def choose(pieces):
    raw = json.dumps({"answered": True, "pieces": pieces, "sure": "sure", "summary": "s", "unsure_about": ""})
    return lambda messages, model: G.Reply(raw)


def passages(*doc_ids):
    return [Passage(d, DOCS[d]["title"], DOCS[d].get("category", ""), "x", 0.7, 1, i)
            for i, d in enumerate(doc_ids, 1)]


def steps(doc_id):
    return [t for c, t in G.article_pieces(DOCS[doc_id]["content"])[1] if c.startswith("R")]


def test_v16_prompt_switches_on_all_steps():
    text = (G.PROMPT_DIR / V16).read_text(encoding="utf-8")
    assert "**Version:** 1.6" in text and "**Steps:** all" in text and "**Mode:** extractive" in text


def test_one_chosen_step_brings_every_step_of_the_article_in_order_with_the_migration_step(v16):
    P = passages("DOC-DEPLOY-002")
    d = G.generate("Bad release, we need to go back", "rollback_request", P, call=choose(["1.R1"]), sleep=None)
    reply = G.with_notice(d, P)
    assert [s["piece"] for s in d.sentences] == ["1.R1", "1.R2", "1.R3", "1.R4"]
    assert MIGRATION in reply
    positions = [reply.index(s) for s in steps("DOC-DEPLOY-002")]
    assert positions == sorted(positions)


def test_causes_come_after_the_steps_under_their_own_line(v16):
    P = passages("DOC-PERF-003")
    d = G.generate("no connection available", "database_issue", P, call=choose(["1.C2", "1.R2"]), sleep=None)
    reply = G.with_notice(d, P)
    cause = dict(G.article_pieces(DOCS["DOC-PERF-003"]["content"])[1])["C2"]
    assert G.CAUSES in reply and f"{G.CAUSES}\n- {cause}" in reply
    assert reply.index(steps("DOC-PERF-003")[-1]) < reply.index(G.CAUSES)


def test_a_note_alone_from_a_second_article_does_not_bring_its_steps(v16):
    P = passages("DOC-DEPLOY-002", "DOC-DEPLOY-001")
    d = G.generate("roll back", "rollback_request", P, call=choose(["1.R2", "2.N1"]), sleep=None)
    reply = G.with_notice(d, P)
    assert all(s in reply for s in steps("DOC-DEPLOY-002"))
    assert not any(s in reply for s in steps("DOC-DEPLOY-001"))


def test_everything_is_still_the_articles_own_words(v16):
    P = passages("DOC-DATA-001")
    d = G.generate("export missing records", "data_export", P, call=choose(["1.R3", "1.C3", "1.N1"]), sleep=None)
    reply = G.with_notice(d, P)
    article = " ".join(DOCS["DOC-DATA-001"]["content"].split())
    for line in reply.splitlines():
        if line.startswith("- "):
            assert line[2:] in article, line


@pytest.mark.parametrize("doc_id", sorted(DOCS))
def test_every_article_complete_with_all_its_causes_passes_the_length_rule(v16, doc_id):
    P = passages(doc_id)
    codes = [c for c, _ in G.article_pieces(DOCS[doc_id]["content"])[1]]
    chosen = ["1.R1"] + ["1." + c for c in codes if not c.startswith("R")][:7]
    d = G.generate("question", "x", P, call=choose(chosen), sleep=None)
    check = tone_and_scope(G.with_notice(d, P))
    assert "too long" not in check.detail, (doc_id, check.detail)


def test_v15_behaviour_is_unchanged_when_the_switch_is_off(monkeypatch):
    real = G.load_prompt
    monkeypatch.setattr(G, "EXTRACTIVE", True)
    monkeypatch.setattr(G, "load_prompt", lambda name=None: real("PR-01_draft_reply_v1.5.md"))
    P = passages("DOC-DEPLOY-002")
    d = G.generate("roll back", "rollback_request", P, call=choose(["1.R1"]), sleep=None)
    assert [s["piece"] for s in d.sentences] == ["1.R1"] and G.CAUSES not in G.with_notice(d, P)
