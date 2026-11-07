"""Classify (FR-02) and safety rules (FR-03). TF-IDF only, so no model download is needed."""
import pytest

from src.classify import Classification, TicketClassifier, question_groups
from src.safety import check, check_text

TRAIN = [
    ("How do I revert to an earlier revision?", "rollback_request", "high"),
    ("Please roll back my release to the previous version", "rollback_request", "high"),
    ("rollback the deploy from yesterday", "rollback_request", "medium"),
    ("I cannot log in, my password is rejected", "authentication_failure", "medium"),
    ("login fails with invalid credentials", "authentication_failure", "medium"),
    ("sign in keeps saying wrong password", "authentication_failure", "low"),
    ("Why is my invoice higher this month?", "billing_query", "low"),
    ("question about the charges on my invoice", "billing_query", "low"),
    ("billing period does not match the calendar month", "billing_query", "medium"),
]


@pytest.fixture(scope="module")
def model():
    texts, intents, urgencies = zip(*TRAIN)
    return TicketClassifier("tfidf").fit(list(texts), list(intents), list(urgencies))


def test_every_ticket_gets_type_urgency_confidence_and_three_alternatives(model):
    c = model.classify("my password does not work when I log in")
    assert isinstance(c, Classification) and c.intent == "authentication_failure"
    assert c.urgency in {"high", "medium", "low"}
    assert 0 <= c.confidence <= 1 and 0 <= c.urgency_confidence <= 1
    assert len(c.alternatives) == 3 and c.alternatives[0][0] == c.intent
    assert sum(p for _, p in c.alternatives) <= 1.0001


def test_empty_or_broken_input_gives_the_defined_fallback(model):
    for text in ["", "   ", None]:
        c = model.classify(text)
        assert c.fallback and c.intent == "unclear_request" and c.confidence == 0.0
    broken = TicketClassifier("tfidf")          # never trained: must not raise
    assert broken.classify("hello").fallback


def test_same_ticket_same_answer(model):
    assert model.classify("roll back my release") == model.classify("roll back my release")


def test_saved_model_loads_and_answers_the_same(model, tmp_path):
    path = tmp_path / "classifier.joblib"
    model.save(path, metadata={"note": "test"})
    again = TicketClassifier.load(path)
    assert again.classify("invoice is higher") == model.classify("invoice is higher")
    assert (tmp_path / "classifier.json").exists()


def test_identical_questions_share_a_group():
    g = question_groups(["It is not working.", "it is not working, please help fast",
                         "How do I export data?"])
    assert g[0] == g[1] != g[2]


@pytest.mark.parametrize("text, rule", [
    ("Need to rotate an exposed key. One of our production keys started returning 401", "leaked key or credentials"),
    ("We accidentally pushed our API key to a public repo", "leaked key or credentials"),
    ("We found activity in our audit log from an address none of us recognise", "security incident"),
    ("A former employee appears to still have access", "security incident"),
    ("A customer asked for written confirmation of where their data is physically stored", "data location"),
    ("We need our data to remain within the EU for a contract", "data location"),
    ("Are backups replicated outside our primary region?", "data location"),
    ("I want a refund for last month", "billing dispute"),
    ("There are charges for a service I do not believe we use", "billing dispute"),
    ("Our auditor has asked for access records", "compliance"),
    ("Are staged rollouts on the roadmap?", "feature request"),
])
def test_word_rules_catch_person_only_tickets(text, rule):
    assert rule in check_text(text)


@pytest.mark.parametrize("text", [
    "How do I rotate an API key safely?",
    "How do I revert to an earlier revision?",
    "Why is my invoice higher this month?",
    "How do I export my data to CSV?",
])
def test_word_rules_leave_ordinary_questions_alone(text):
    assert check_text(text) == []


def test_classifier_type_alone_is_enough_to_send_to_a_person():
    result = check("It is not working.", predicted_type="unclear_request")
    assert result.must_go_to_person and "type: unclear_request" in result.reasons
    assert not check("How do I export my data?", predicted_type="data_export").must_go_to_person
