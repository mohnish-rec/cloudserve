"""The FastAPI application (src/api.py): same pipeline as the unattended run, fake classifier, search and models
(no key needed). Called through app.state.handle, the function the POST /tickets route runs."""
from src.api import create_app
from test_pipeline import FITS, REPLY, Classifier, Search, models  # same fakes as the pipeline tests

TICKET = {"ticket_id": "API-1", "channel": "email", "subject": "", "body": "How do I roll back to an earlier revision?",
          "received_at": "2026-11-14T09:00:00Z", "customer_id": "C-9", "customer_tier": "business",
          "customer_region": "europe", "language_fluency": "fluent"}


def app_for(tmp, conf=0.97, intent="rollback_request"):
    return create_app(Classifier(conf, intent), Search(), write_log=False, call=models(REPLY, FITS),
                      sleep=lambda s: None, kill_switch_file=tmp / "off")


def test_the_api_has_the_health_and_tickets_routes(tmp_path):
    paths = {r.path for r in app_for(tmp_path).routes}
    assert {"/health", "/tickets", "/docs"} <= paths


def test_a_safe_ticket_is_answered_with_the_same_result_fields_as_the_run(tmp_path):
    r = app_for(tmp_path).state.handle(TICKET)
    assert r["action"] == "auto_respond" and "written automatically" in r["sent_text"]
    assert {"reason", "handover", "type", "confidence", "cited", "guardrails", "run_id"} <= set(r)


def test_a_security_ticket_goes_to_a_person(tmp_path):
    t = {**TICKET, "ticket_id": "API-2", "body": "Someone used our leaked API key to delete projects."}
    r = app_for(tmp_path, intent="security_incident").state.handle(t)
    assert r["action"] == "escalate" and r["handover"]


def test_labels_sent_to_the_api_are_ignored(tmp_path):
    t = {**TICKET, "labels": {"expected_route": "escalate", "must_not_auto_respond": True}}
    assert app_for(tmp_path).state.handle(t)["action"] == "auto_respond"


def test_a_broken_classifier_fails_closed_to_a_person(tmp_path):
    class Broken:
        def classify(self, text):
            raise RuntimeError("model file missing")
    app = create_app(Broken(), Search(), write_log=False, kill_switch_file=tmp_path / "off")
    r = app.state.handle(TICKET)
    assert r["action"] == "escalate" and "unexpected error" in r["reason"]


def test_healthz_and_readyz_exist(tmp_path):
    """FR-17 (17 Nov 2026): /healthz says the process is alive; /readyz lists anything missing."""
    paths = {r.path for r in app_for(tmp_path).routes}
    assert {"/healthz", "/readyz"} <= paths


def test_readiness_lists_what_is_missing(tmp_path, monkeypatch):
    from src.api import readiness
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("WRITER_API_KEY", raising=False)
    missing = readiness(tmp_path)                    # an empty folder: nothing is in place
    assert any("classifier model" in m for m in missing) and any("AI key" in m for m in missing)


def test_the_web_page_and_the_file_run_routes_are_there(tmp_path):
    paths = {r.path for r in app_for(tmp_path).routes}
    assert {"/", "/runs", "/runs/{job_id}", "/live-charts", "/kill-switch", "/demo-tickets",
            "/decision-log/{log_run_id}/{ticket_id}", "/runs/{job_id}/tickets/{ticket_id}", "/runs/{job_id}/check",
            "/runs/{job_id}/download/{kind}", "/limits", "/limits/check"} <= paths


def test_the_web_page_kill_switch_creates_and_deletes_the_same_file(tmp_path, monkeypatch):
    """FR-16 from the web page: the button makes the same file as the README's command, and every change is written
    down with the time."""
    from src.api import KillSwitchIn
    monkeypatch.delenv("KILL_SWITCH", raising=False)
    switch = tmp_path / "storage" / "kill_switch"
    app = create_app(Classifier(), Search(), write_log=False, call=models(REPLY, FITS), sleep=lambda s: None,
                     kill_switch_file=switch)
    flip = next(r.endpoint for r in app.routes if getattr(r, "path", "") == "/kill-switch")
    assert app.state.handle(dict(TICKET))["action"] == "auto_respond"
    assert flip(KillSwitchIn(on=True))["kill_switch_on"] is True and switch.exists()
    assert app.state.handle(dict(TICKET, ticket_id="API-2", customer_id="C-10"))["reason"].count("kill switch")
    assert flip(KillSwitchIn(on=False))["kill_switch_on"] is False and not switch.exists()
    history = (tmp_path / "storage" / "kill_switch_history.txt").read_text(encoding="utf-8")
    assert "turned on from the web page" in history and "turned off from the web page" in history


def test_the_demo_tickets_route_sends_no_labels(tmp_path):
    demo = next(r.endpoint for r in app_for(tmp_path).routes if getattr(r, "path", "") == "/demo-tickets")()
    assert len(demo) == 7 and all("labels" not in t for t in demo)
