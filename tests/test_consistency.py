"""12 Nov 2026, acceptance criterion A5: "the same input produces the same routing decision". Within one run the same
model input gets the same answer (the run memory in src/generate.py), checked after the saved cache and kept only for
answers that were read successfully. Found in the final development run: two identical tickets (DEV-0156, DEV-0399)
got different decisions because the hosted models are not perfectly repeatable."""
import src.generate as G

MSG = [{"role": "user", "content": "user left company. how i remove all his access including key he made?"}]


def _model(monkeypatch, answers):
    calls = []

    def fake(messages, model, max_tokens=2000, role="writer"):
        calls.append(1)
        return G.Reply(answers[len(calls) - 1])
    monkeypatch.setattr(G, "call_model", fake)
    monkeypatch.setattr(G, "provider", lambda role="writer": {"base_url": "x", "api_key": "k", "pin": ""})
    monkeypatch.setenv("REPLY_CACHE", "off")
    return calls


def test_the_same_input_in_one_run_gets_the_same_answer_without_a_second_call(monkeypatch):
    calls = _model(monkeypatch, ["first answer", "a different answer"])
    a, model, _ = G.call_with_fallback(MSG, call=G.call_model)
    G.remember(a, model)                         # the answer was read successfully
    b, _, n = G.call_with_fallback(MSG, call=G.call_model)
    assert str(b) == "first answer" and n == 0 and len(calls) == 1


def test_an_answer_that_could_not_be_read_is_not_remembered(monkeypatch):
    calls = _model(monkeypatch, ["garbled", "good answer"])
    G.call_with_fallback(MSG, call=G.call_model)  # not passed to remember(): it could not be read
    b, _, _ = G.call_with_fallback(MSG, call=G.call_model)
    assert str(b) == "good answer" and len(calls) == 2


def test_a_different_input_is_a_new_call(monkeypatch):
    calls = _model(monkeypatch, ["one", "two"])
    a, m, _ = G.call_with_fallback([{"role": "user", "content": "ticket A"}], call=G.call_model)
    G.remember(a, m)
    b, _, _ = G.call_with_fallback([{"role": "user", "content": "ticket B"}], call=G.call_model)
    assert str(b) == "two" and len(calls) == 2


def test_fake_models_in_tests_never_use_the_run_memory():
    G.call_with_fallback([{"role": "user", "content": "x"}], call=lambda m, mod: G.Reply("fake"), sleep=None)
    assert G._RUN_MEMO == {}


def test_the_checker_verdict_is_reused_and_counted_as_no_call(monkeypatch):
    """The second identical ticket reuses the checker's verdict from run memory and is logged as 0 model calls."""
    import src.guardrails as GR
    calls = _model(monkeypatch, ['{"fits_situation": true, "unsupported_sentences": [], "reason": "ok"}'] * 2)
    arts = {"KB-1": {"title": "Remove a user", "content": "Go to Settings then Users."}}
    sents = [{"text": "Go to Settings then Users.", "doc_ids": ("KB-1",), "sources": (1,)}]
    first = GR.model_support("remove a user", sents, arts, call=G.call_model)
    second = GR.model_support("remove a user", sents, arts, call=G.call_model)
    assert first.passed and second.passed and len(calls) == 1
    assert not first.memo and second.memo
