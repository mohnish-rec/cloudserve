"""14 Nov 2026 (walkthrough, Q09): the second model wrongly said a word-for-word sentence was unsupported and blocked the
reply (DEV-0218, DEV-0285). A sentence copied exactly from its article is supported by construction, so that verdict is
set aside; the model's other verdict, whether the article fits the customer's situation, still blocks."""
import json
from pathlib import Path

import src.generate as G
import src.guardrails as GR

ROOT = Path(__file__).resolve().parent.parent
DOCS = {d["doc_id"]: d for d in json.loads((ROOT / "data" / "documentation.json").read_text(encoding="utf-8-sig"))}
NOTE = ("Repeated lockouts within a short period usually indicate an automated process still using an old password "
        "rather than a user error.")                                   # DOC-AUTH-001, the sentence blocked in DEV-0218
COPY = {"text": NOTE, "doc_ids": ("DOC-AUTH-001",), "sources": (1,), "verbatim": True}
STEP = {"text": "Clear cookies for the CloudServe domain, or open a private browsing window, then attempt the login again.",
        "doc_ids": ("DOC-AUTH-001",), "sources": (1,), "verbatim": True}


def test_an_exact_copy_is_recognised():
    assert GR.exact_copy(COPY, DOCS) and GR.exact_copy(STEP, DOCS)


def test_a_changed_or_unflagged_sentence_is_not_an_exact_copy():
    assert not GR.exact_copy({**COPY, "text": NOTE.replace("usually", "always")}, DOCS)
    assert not GR.exact_copy({**COPY, "verbatim": False}, DOCS)
    assert not GR.exact_copy({**COPY, "doc_ids": ("DOC-BILL-001",)}, DOCS)      # not in the article it cites


def _checker(monkeypatch, verdict):
    monkeypatch.setattr(G, "call_model", lambda messages, model, max_tokens=2000, role="writer": G.Reply(json.dumps(verdict)))
    monkeypatch.setattr(G, "provider", lambda role="writer": {"base_url": "x", "api_key": "k", "pin": ""})


def test_the_checker_cannot_block_an_exact_copy_as_unsupported(monkeypatch):
    _checker(monkeypatch, {"fits_situation": True, "unsupported_sentences": [2], "reason": "not supported"})
    c = GR.model_support("I cannot get into the console", [STEP, COPY], DOCS, call=G.call_model)
    assert c.passed and "exact copies" in c.detail


def test_the_checker_still_blocks_when_the_article_does_not_fit(monkeypatch):
    _checker(monkeypatch, {"fits_situation": False, "unsupported_sentences": [], "reason": "different problem"})
    assert not GR.model_support("My invoice is too high", [STEP, COPY], DOCS, call=G.call_model).passed


def test_the_checker_still_blocks_a_sentence_that_is_not_an_exact_copy(monkeypatch):
    _checker(monkeypatch, {"fits_situation": True, "unsupported_sentences": [1], "reason": "not in the article"})
    changed = {**STEP, "text": "Your account has been unlocked for you."}
    assert not GR.model_support("I cannot get into the console", [changed, COPY], DOCS, call=G.call_model).passed
