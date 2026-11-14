"""11 Nov: the reply a customer sees. Steps grouped under the article they came from; no [n] numbers;
the rare step backed by two articles names the second as "(also in: ...)"; the log can follow every citation."""
import re

from src.generate import Draft, assemble, render, with_notice
from src.guardrails import MAX_WORDS, tone_and_scope
from src.pipeline import citation_trail

TEAM, KEYS = "DOC-ACCT-001", "DOC-AUTH-004"


def _draft(*items):
    s = tuple({"text": t, "sources": tuple(range(1, len(d) + 1)), "doc_ids": tuple(d)} for t, d in items)
    return Draft(ok=True, answered=True, reply=assemble(s), sentences=s, cited_doc_ids=tuple(dict.fromkeys(x for _, d in items for x in d)))


def test_each_step_sits_under_the_article_it_came_from_with_no_numbers():
    text = with_notice(_draft(("Remove the user from the team.", [TEAM]), ("Rotate the key.", [KEYS])))
    lines = text.splitlines()
    assert lines[0] == "Thanks for getting in touch. Here is what to do:"
    a, b = lines.index('From our help article "Managing team members, roles and permissions":'), \
        lines.index('From our help article "API key rotation and scope management":')
    assert lines[a + 1] == "- Remove the user from the team." and lines[b + 1] == "- Rotate the key." and a < b
    assert "[1]" not in text and "[2]" not in text and "help articles named above" in text


def test_a_step_from_two_articles_goes_under_the_first_and_names_the_other():
    text = render(_draft(("Revoke the keys the user created.", [TEAM, KEYS])))
    assert '- Revoke the keys the user created. (also in: "API key rotation and scope management")' in text
    assert text.count("From our help article") == 1


def test_one_article_says_article_not_articles():
    assert "help article named above" in with_notice(_draft(("Select roll back.", ["DOC-DEPLOY-002"])))


def test_the_new_layout_adds_nothing_to_the_length_count():
    """The limit must stay as strict as before: the same content counts the same, however it is laid out."""
    long = " ".join(["word"] * MAX_WORDS) + "."
    one = tone_and_scope(with_notice(_draft((long, [TEAM]), ("Short step.", [TEAM]))))
    two = tone_and_scope(with_notice(_draft((long, [TEAM, KEYS]), ("Short step.", [KEYS]))))   # headings, also-in
    # 14 Nov (reply setting R1): two articles may be longer, so compare the counted words, not the verdict
    n = lambda c: re.search(r"\((\d+) words", c.detail)
    long2 = tone_and_scope(with_notice(_draft((" ".join(["word"] * 330) + ".", [TEAM, KEYS]), ("Short step.", [KEYS]))))
    long1 = tone_and_scope(with_notice(_draft((" ".join(["word"] * 330) + ".", [TEAM]), ("Short step.", [TEAM]))))
    assert not one.passed and two.passed
    assert n(long1).group(1) == n(long2).group(1)                                               # same word count
    assert tone_and_scope(with_notice(_draft(("Select roll back on that revision.", [TEAM])))).passed


def test_every_citation_can_be_followed_to_its_passage_and_the_sentences_it_supports():
    d = _draft(("Remove the user from the team.", [TEAM]), ("Revoke the keys.", [TEAM, KEYS]))
    sources = ({"doc_id": KEYS, "rank": 1, "score": 0.71, "keyword": 2.0, "passage": "Rotate keys..."},
               {"doc_id": TEAM, "rank": 2, "score": 0.64, "keyword": 1.0, "passage": "Remove members..."})
    trail = {t["doc_id"]: t for t in citation_trail(d, sources)}
    assert trail[TEAM]["score"] == 0.64 and trail[TEAM]["passages"] == ["Remove members..."]
    assert trail[TEAM]["sentences"] == ["1. Remove the user from the team.", "2. Revoke the keys."]
    assert trail[KEYS]["sentences"] == ["2. Revoke the keys."] and trail[KEYS]["title"] == "API key rotation and scope management"
