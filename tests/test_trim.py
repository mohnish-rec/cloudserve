"""10 Nov, experiment 1B (on by default from 12 Nov): trim instead of block."""
from src.generate import Draft, assemble
from src.guardrails import Check, Report, trim

S = [{"text": f"Sentence number {i}.", "sources": [1], "doc_ids": ["DOC-A"]} for i in range(1, 5)]


def _draft(n=4):
    s = tuple(S[:n])
    return Draft(ok=True, answered=True, reply=assemble(s), sentences=s, cited_doc_ids=("DOC-A",))


def _report(*checks):
    return Report(checks=[Check("private_data", True, "none found"), *checks])


def test_one_unsupported_sentence_is_removed():
    short = trim(_draft(), _report(Check("grounding_model", False, "sentences [2] not supported", bad=(2,), trimmable=True)))
    assert [s["text"] for s in short.sentences] == ["Sentence number 1.", "Sentence number 3.", "Sentence number 4."]
    assert "number 2" not in short.reply


def test_a_wrong_article_is_never_trimmed():
    c = Check("grounding_model", False, "the article does not fit the situation; sentences [1] not supported",
              bad=(1,), trimmable=False)
    assert trim(_draft(), _report(c)) is None


def test_private_data_or_any_other_check_is_never_trimmed():
    words = Check("grounding_words", False, "sentences 2", bad=(2,), trimmable=True)
    for other in ("private_data", "instruction_integrity", "tone_and_scope", "confidence_floor"):
        assert trim(_draft(), _report(words, Check(other, False, "blocked"))) is None


def test_a_check_that_errored_is_never_trimmed():
    assert trim(_draft(), _report(Check("grounding_model", False, "the check failed", error=True, bad=(1,),
                                        trimmable=True))) is None


def test_more_than_half_removed_is_not_enough_to_send():
    c = Check("grounding_words", False, "sentences 1, 2, 3", bad=(1, 2, 3), trimmable=True)
    assert trim(_draft(), _report(c)) is None


def test_both_grounding_checks_together_can_be_trimmed():
    a = Check("grounding_words", False, "sentences 1", bad=(1,), trimmable=True)
    b = Check("grounding_model", False, "sentences [4] not supported", bad=(4,), trimmable=True)
    assert len(trim(_draft(), _report(a, b)).sentences) == 2
