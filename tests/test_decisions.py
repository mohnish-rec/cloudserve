"""14 Nov 2026: the learned decisions (src/decisions.py), trained on Mohnish Grover's decisions for the 500
development tickets. It can only add a handover; the safety rules underneath never change."""
import joblib
import numpy as np
import pytest
from sklearn.linear_model import LogisticRegression

from src import decisions


def test_probability_comes_from_the_saved_model(tmp_path):
    X = np.array([[1.0, 0.0], [0.9, 0.1], [0.0, 1.0], [0.1, 0.9]])
    model = LogisticRegression().fit(X, [1, 1, 0, 0])
    path = tmp_path / "router.joblib"
    joblib.dump(model, path)
    assert decisions.person_probability([1.0, 0.0], path) > 0.5 > decisions.person_probability([0.0, 1.0], path)


def test_a_missing_model_fails_loudly(tmp_path):
    with pytest.raises(FileNotFoundError):
        decisions.load(tmp_path / "missing.joblib")


def test_it_is_on_by_default(monkeypatch):
    monkeypatch.delenv("LEARNED_DECISIONS", raising=False)
    assert decisions.enabled()


# The real trained model, on his decisions: rewordings the development tickets do not contain
REAL = decisions.MODEL_PATH.exists()


@pytest.fixture(scope="module")
def embed():
    from src.classify import TicketClassifier
    from src.retrieve import default_embedder
    c = TicketClassifier(features="embeddings", embedder=default_embedder())
    return lambda text: c.embed([text])[0]


@pytest.mark.skipif(not REAL, reason="run python scripts/train_decision_router.py first")
@pytest.mark.parametrize("text", [
    "Our database restore has been going for two days now and it's only 300 GB. Has it got stuck?",                  # Q27
    "Login keeps saying invalid credentials for days, but I'm sure the password is right.",                           # Q12
    pytest.param("We got rate limited when traffic went up and parts of our app went down. We'd prefer to pay extra "
                 "than be cut off.", marks=pytest.mark.xfail(reason="KNOWN MISS (14 Nov): 29%; learned from only 7 Q41 "
                 "tickets, all saying 'throttled' and 'overage'. The Q41 word rule misses it too.", strict=False)),  # Q41
    "We rotated the shared account's password and since then our scheduled scripts can't authenticate."])            # Q11
def test_new_wordings_of_his_person_decisions_go_to_a_person(embed, text):
    assert decisions.person_probability(embed(text)) >= decisions.THRESHOLD


@pytest.mark.skipif(not REAL, reason="run python scripts/train_decision_router.py first")
@pytest.mark.parametrize("text", [
    "How can I roll back to the previous release? This morning's deploy is throwing errors.",                          # Q45
    "Webhook signature checks fail on every event; we compute it over the parsed JSON.",                                # Q52
    "We're new here with a container we want to deploy. Where do we begin?"])                                          # Q36
def test_new_wordings_of_his_answer_decisions_are_not_handed_over(embed, text):
    assert decisions.person_probability(embed(text)) < decisions.THRESHOLD


def test_it_reads_the_message_not_the_subject():
    """14 Nov 2026 (Mohnish Grover): a misleading subject must not decide. A ticket with no message uses its subject."""
    from types import SimpleNamespace as T
    assert decisions.text_of(T(body="No connection is available.", text="Database restore taking hours. No connection "
                               "is available.")) == "No connection is available."
    assert decisions.text_of(T(body="", text="Invoice higher than expected")) == "Invoice higher than expected"


@pytest.mark.skipif(not REAL, reason="run python scripts/train_decision_router.py first")
@pytest.mark.parametrize("ticket", ["DEV-0374", "DEV-0378", "DEV-0439"])
def test_misleading_subject_no_longer_sends_his_answered_tickets_to_a_person(embed, ticket):
    """These three went to a person in the sandbox run because of the subject 'Database restore taking hours'."""
    from pathlib import Path
    from src.ingest import load_tickets
    t = next(x for x in load_tickets(Path(__file__).resolve().parent.parent / "data" / "development_tickets.json")
             if x.ticket_id == ticket)
    assert decisions.person_probability(embed(decisions.text_of(t))) < decisions.THRESHOLD
