"""14 Nov 2026 (Mohnish Grover): "If an automatic answer did not solve the problem, the follow-up goes to a person with
a draft." The same customer writing again on the same type within 7 days goes to a person, with the earlier reply as
the draft; anything else is handled as usual."""
from src import followups
from src.ingest import normalise
from src.pipeline import process
from test_pipeline import FITS, REPLY, Classifier, Search, models  # same fakes as the pipeline tests


def ticket(tid, when, customer="C-1", body="How do I roll back to an earlier revision?"):
    return normalise({"ticket_id": tid, "channel": "email", "subject": "", "body": body, "received_at": when,
                      "customer_id": customer, "customer_tier": "business", "customer_region": "europe",
                      "language_fluency": "fluent"})


def handle(t, intent="rollback_request", tmp=None):
    return process(t, Classifier(intent=intent), Search(), call=models(REPLY, FITS), sleep=lambda s: None,
                   kill_switch_file=(tmp / "off") if tmp else None)


def test_a_follow_up_within_7_days_goes_to_a_person_with_the_earlier_reply(tmp_path):
    first = handle(ticket("T-1", "2026-11-01T09:00:00Z"), tmp=tmp_path)
    assert first.action == "auto_respond"
    again = handle(ticket("T-2", "2026-11-04T09:00:00Z", body="I tried those steps and it still fails."), tmp=tmp_path)
    assert again.action == "escalate" and "follow-up" in again.reason and "T-1" in again.reason
    assert again.handover["earlier_reply"] == first.sent_text          # the person sees what was already sent
    assert again.handover["draft"] == ""                                # 16 Nov: not something to send again


def test_a_different_customer_type_or_week_is_not_a_follow_up(tmp_path):
    handle(ticket("T-1", "2026-11-01T09:00:00Z"), tmp=tmp_path)
    assert handle(ticket("T-2", "2026-11-03T09:00:00Z", customer="C-2"), tmp=tmp_path).action == "auto_respond"
    assert handle(ticket("T-3", "2026-11-03T09:00:00Z"), intent="webhook_issue", tmp=tmp_path).action == "auto_respond"
    assert handle(ticket("T-4", "2026-11-12T09:00:00Z"), tmp=tmp_path).action == "auto_respond"   # 11 days later


def test_a_ticket_sent_to_a_person_is_not_remembered(tmp_path):
    handle(ticket("T-1", "2026-11-01T09:00:00Z", body="I want a refund for last month"), intent="billing_query", tmp=tmp_path)
    assert followups.earlier(ticket("T-2", "2026-11-02T09:00:00Z"), "billing_query") is None
