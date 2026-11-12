"""11 Nov, PR-01 v1.4: the reply quotes the articles word for word. The model only chooses labelled pieces."""
import json

import pytest

import src.generate as G
from src.retrieve import Passage, load_documents

DOCS = {d["doc_id"]: d for d in load_documents()}
P = [Passage("DOC-DATA-001", "Exporting account data and scheduled extracts", "data", "x", 0.7, 3, 1),
     Passage("DOC-DEPLOY-002", "Rolling back a failed release", "deployment", "x", 0.5, 1, 2)]


@pytest.fixture
def extractive(monkeypatch):
    real = G.load_prompt
    monkeypatch.setattr(G, "EXTRACTIVE", True)
    monkeypatch.setattr(G, "load_prompt", lambda name=None: real("PR-01_draft_reply_v1.4.md"))


def fake(text):
    return lambda messages, model: G.Reply(text)


def answer(pieces, answered=True):
    return json.dumps({"answered": answered, "pieces": pieces, "sure": "sure", "summary": "Export queued", "unsure_about": ""})


def test_every_piece_of_every_article_is_an_exact_copy_of_the_article():
    for d in DOCS.values():
        _, pieces = G.article_pieces(d["content"])
        assert any(code.startswith("R") for code, _ in pieces), d["doc_id"]
        flat = " ".join(d["content"].split())
        assert all(text in flat for _, text in pieces), d["doc_id"]


def test_the_reply_is_the_articles_own_words(extractive):
    d = G.generate("My export has been queued for hours", "data_export", P, call=fake(answer(["1.R1"])), sleep=None)
    step = "Check the exports page for job status. Jobs covering more than a million records commonly take several minutes."
    assert d.ok and d.sentences[0]["text"] == step and d.sentences[0]["piece"] == "1.R1"
    text = G.with_notice(d, P)
    assert f"- {step}" in text                                  # one whole step, one bullet, word for word
    assert 'From our help article "Exporting account data and scheduled extracts":' in text


def test_a_label_that_does_not_exist_is_never_sent(extractive):
    for bad in (["1.R9"], ["4.R1"], ["Check the exports page"], [f"1.R{i}" for i in range(1, 10)]):
        assert not G.generate("export", "data_export", P, call=fake(answer(bad)), sleep=None).ok


def test_not_answered_goes_to_a_person(extractive):
    d = G.generate("roadmap?", "feature_request", P, call=fake(answer([], answered=False)), sleep=None)
    assert not d.ok and d.reply == G.NO_ANSWER


def test_the_writer_sees_labelled_pieces_and_never_the_symptoms_as_choices(extractive):
    text = G.number_pieces(G.articles_for(P))
    assert "1.R2  Request a fresh link from the exports page if the original has expired." in text
    assert "Symptoms (for matching only, never chosen): An export has not completed" in text
    assert "1.S" not in text
