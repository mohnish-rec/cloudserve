"""14 Nov 2026: the rules from Mohnish Grover's walkthrough of all 500 development tickets (67 questions,
evaluation/human_review/dev_walkthrough.json). Each rule is tested on the customers' own wording, on rewordings, and on
the neighbouring questions it must NOT catch."""
import pytest

from src import safety


@pytest.fixture(autouse=True)
def final_rules(monkeypatch):
    monkeypatch.setenv("NARROW_RULES", "on")
    monkeypatch.setenv("QUESTION_RULES", "on")


# Q05: a key the customer exposed by mistake is answered (revoke first, replace, check the audit log)
@pytest.mark.parametrize("text", [
    "One of our engineers pushed a key to a public repository by mistake. We need to replace it without taking the service down. What is the correct order of operations?",
    "one of our engineers pushed key to a public repository by mistake. We need to replace it without taking service down.",
    "Need to rotate an exposed key. A key can read fine but every write returns a permission error.",
    "We accidentally committed an API key to GitHub. How do we rotate it?"])
def test_a_key_exposed_by_mistake_is_answered(text):
    assert not safety.check(text, "api_key_issue").must_go_to_person


# ...but any sign that a key or credential was used, stolen or breached still goes to a person
@pytest.mark.parametrize("text, ptype", [
    ("One of our engineers believes their credentials may have been exposed in a breach at another service. What should we be doing right now?", "security_incident"),
    ("One of our engineers believes their credentials may have been exposed in a breach at another service.", "api_key_issue"),
    ("We pushed a key to a public repository and someone has already used it to create resources.", "api_key_issue"),
    ("Our key was committed to GitHub and we see activity from an address none of us recognise.", "api_key_issue"),
    ("A key was pushed to a public repo and we think it has been stolen.", "api_key_issue"),
    ("We have found activity in our audit log from an address none of us recognise, going back to earlier today.", "security_incident")])
def test_any_sign_of_use_still_goes_to_a_person(text, ptype):
    assert safety.check(text, ptype).must_go_to_person


@pytest.mark.parametrize("text", [
    "I have been trying to sign in for the last a couple of days and keep getting an invalid credentials message. I am certain the password is correct because I use a password manager.",
    "i cannot login since last Friday. password is correct i am sure. please help fast, it is blocking my work."])
def test_q12_invalid_credentials_with_a_correct_password_goes_to_a_person(text):
    r = safety.check(text, "authentication_failure")
    assert r.must_go_to_person and any("(Q12)" in x for x in r.reasons)


@pytest.mark.parametrize("text", [
    "A restore we started two days ago is still running. The database is about four hundred gigabytes. Is this a normal duration or has something stalled?",
    "restore is running from long time. database is 400 gb. is it normal?",
    "restore we start earlier today is still run. database about four hundred gigabytes."])
def test_q27_a_restore_still_running_goes_to_a_person(text):
    r = safety.check(text, "database_issue")
    assert r.must_go_to_person and any("(Q27)" in x for x in r.reasons)


def test_q41_throttled_and_wanting_overage_goes_to_a_person():
    r = safety.check("We were throttled on Monday after a traffic increase and it took down part of our product. "
                     "We would rather pay overage than be stopped. How do we change that?", "quota_or_overage")
    assert r.must_go_to_person and any("(Q41)" in x for x in r.reasons)


# The neighbouring questions these rules must not catch
@pytest.mark.parametrize("text, ptype", [
    ("Since yesterday morning I cannot get into the console at all. My colleague on the same team signs in without any trouble.", "authentication_failure"),   # Q09
    ("My authenticator app codes are being rejected every time. I have tried generating new ones several times.", "authentication_failure"),                   # Q10
    ("Database restore taking hours. We are getting errors saying no connection is available. This started when we scaled up our service.", "database_issue"),  # Q25
    ("Our spend cap stopped a production workload overnight. We need it raised immediately.", "quota_or_overage"),                                              # Q40
    ("Overage charges appeared on our invoice that we were not expecting.", "quota_or_overage"),                                                                # Q42
    ("We started getting 429 responses at around two days ago. We have several keys, so I had assumed our limit would be higher.", "rate_limit"),             # Q43a
    ("Where should secrets be stored so they do not appear in the logs? At the moment ours are being printed at startup.", "configuration_help")])            # Q16
def test_neighbouring_questions_are_not_caught(text, ptype):
    assert not safety.check(text, ptype).must_go_to_person
