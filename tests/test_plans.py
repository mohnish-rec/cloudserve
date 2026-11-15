"""The plan rule (15 Nov 2026, Mohnish Grover): an article that applies only to other plans than the customer's is
not sent; the ticket goes to a person with the draft. Fake classifier, search and models (no key needed)."""
import json

from src import plans
from src.ingest import normalise
from src.pipeline import process
from src.retrieve import Passage
from src.route import DRAFT_READY
from test_pipeline import FITS, Classifier, models  # same fakes as the pipeline tests

SSO = [Passage("DOC-AUTH-003", "Single sign-on configuration with SAML providers", "authentication",
               "Compare the assertion consumer service URL.", 0.7, 3, 1)]          # the real article: Business and Enterprise
REPLY = json.dumps({"answered": True, "sure": "sure", "summary": "SAML users bounced back", "unsure_about": "",
                    "sentences": [{"text": "Compare the assertion consumer service URL in your identity provider against "
                                           "the value shown on the SSO settings page.", "sources": [1]}]})


class Search:
    embedder = None

    def search(self, text):
        return SSO


def run(tier, tmp, monkeypatch, rule="on"):
    monkeypatch.setenv("PLAN_RULE", rule)
    t = normalise({"ticket_id": "P-1", "channel": "email", "subject": "", "received_at": "2026-11-15T09:00:00Z",
                   "body": "Users are bounced back to an error page after signing in with SAML.", "customer_id": "C",
                   "customer_tier": tier, "customer_region": "europe", "language_fluency": "fluent"})
    return process(t, Classifier(intent="sso_configuration"), Search(), call=models(REPLY, FITS),
                   sleep=lambda s: None, kill_switch_file=tmp / "off")


def test_reading_the_applies_to_line():
    assert plans.plan_limited("Business and Enterprise plans")
    assert not plans.plan_limited("All plans") and not plans.plan_limited("Container Service, Functions")
    arts = {"A": {"content": "# T\n\n**Applies to:** Business and Enterprise plans\n"}}
    assert plans.excluded("standard", ["A"], arts) == ("A", "Business and Enterprise plans")
    assert plans.excluded("business", ["A"], arts) is None
    assert plans.excluded("unknown", ["A"], arts) is not None          # cannot confirm: a person checks


def test_a_standard_customer_gets_a_person_with_the_draft(tmp_path, monkeypatch):
    o = run("standard", tmp_path, monkeypatch)
    assert o.action == "escalate" and o.label == DRAFT_READY and "plan rule" in o.reason
    assert "assertion consumer service URL" in o.handover["draft"]           # the person has the reply in hand


def test_a_business_customer_is_answered(tmp_path, monkeypatch):
    assert run("business", tmp_path, monkeypatch).action == "auto_respond"


def test_the_switch_turns_it_off(tmp_path, monkeypatch):
    assert run("standard", tmp_path, monkeypatch, rule="off").action == "auto_respond"


def test_on_by_default(monkeypatch):
    monkeypatch.delenv("PLAN_RULE")
    assert plans.enabled()
