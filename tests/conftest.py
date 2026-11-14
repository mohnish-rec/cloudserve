"""Shared test settings (10-11 Nov 2026).

1. The experiment switches (NARROW_RULES, TRIM_UNSUPPORTED, REPLY_CACHE, TYPE_AWARE_SEARCH, QUESTION_RULES) are set off
   for every test, so each test checks the behaviour it names on purpose; a test that needs a switch sets it itself.
2. The writer's mode is fixed per test: sentence mode (PR-01 v1.3) unless a test asks for extractive mode (v1.4).
   The prompt file is chosen when the program starts (PR01_FILE), so without this the terminal's setting would decide.
Found 10 and 11 Nov: with settings on in the terminal, tests failed for the wrong reason.
"""
import pytest

import src.generate as G

SWITCHES = ("NARROW_RULES", "TRIM_UNSUPPORTED", "REPLY_CACHE", "TYPE_AWARE_SEARCH", "QUESTION_RULES",
            "LEARNED_DECISIONS")
SENTENCE_PROMPT = "PR-01_draft_reply_v1.3.md"


@pytest.fixture(autouse=True)
def _switches_off(monkeypatch):
    for name in SWITCHES:                  # 12 Nov: the defaults are on, so each is set off, not just cleared
        monkeypatch.setenv(name, "off")


@pytest.fixture(autouse=True)
def _sentence_mode(monkeypatch):
    real = G.load_prompt
    monkeypatch.setattr(G, "EXTRACTIVE", False)
    monkeypatch.setattr(G, "ALL_STEPS", False)        # PR-01 v1.6: only tests that ask for it
    monkeypatch.setattr(G, "WHOLE_ARTICLE", False)    # PR-01 v1.7: only tests that ask for it
    monkeypatch.setattr(G, "load_prompt", lambda name=None: real(name or SENTENCE_PROMPT))


@pytest.fixture(autouse=True)
def _fresh_run_memory(monkeypatch):
    """A5 run memory (12 Nov): each test starts as a new run, so tests cannot affect each other."""
    monkeypatch.setattr(G, "_RUN_MEMO", {})
