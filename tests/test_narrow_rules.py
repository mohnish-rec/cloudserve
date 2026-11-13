"""10 Nov (on by default from 12 Nov): narrowed safety rules. Questions are answered; requests and every zero-tolerance case stay with a person."""
import pytest

from src.safety import check


@pytest.fixture(autouse=True)
def narrow(monkeypatch):
    monkeypatch.setenv("NARROW_RULES", "on")


@pytest.mark.parametrize("text", ["Where is our data physically stored?",
                                  "Are backups replicated outside our primary region?",
                                  "There are charges on our invoice for a service we do not use. Could you explain?"])
def test_questions_are_no_longer_held_back(text):
    assert not check(text, "data_residency").must_go_to_person


@pytest.mark.parametrize("text", ["Please move our data to the EU region", "Can we change our region to Frankfurt?",
                                  "Delete all our data please", "I want a refund", "We were charged twice",
                                  "I am disputing this invoice", "I want my money back"])
def test_requests_and_disputes_still_go_to_a_person(text):
    assert check(text, "billing_query").must_go_to_person


@pytest.mark.parametrize("ptype", ["security_incident", "compliance_request", "feature_request", "unclear_request"])
def test_every_must_not_type_still_goes_to_a_person(ptype):
    assert check("anything at all", ptype).must_go_to_person


@pytest.mark.parametrize("text", ["We pushed an API key to a public GitHub repository by mistake",
                                  "Someone logged into our account from an unknown country"])
def test_security_word_rules_are_untouched(text):
    assert check(text, "api_key_issue").must_go_to_person


def test_the_final_settings_apply_with_nothing_set(monkeypatch):
    """12 Nov: narrowed rules and question rules are on by default, so a fresh machine (the hidden-set run)
    gets Mohnish's decisions with no settings line: data location to a person (Daniel's rule), including
    backup replication (Q24, 13 Nov), and refunds to a person."""
    monkeypatch.delenv("NARROW_RULES")
    monkeypatch.delenv("QUESTION_RULES")
    assert check("Where is our data physically stored?", "data_residency").must_go_to_person
    assert check("Are backups replicated outside our primary region?", "data_residency").must_go_to_person
    assert check("I want a refund", "billing_query").must_go_to_person
