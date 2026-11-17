# Prompt register

Every prompt the system or its evaluation uses, with its version and status (Setup Guide, project structure:
"README.md: the register, with versions"; Module 2: prompts are versioned like code, with one active version and a
one-line rollback). Each prompt file holds its full change history (what changed, why, and the result).

Owner of every prompt: Mohnish Grover. Written with Claude (Anthropic).

## Prompts that run inside the system (`build/`)

| ID | Version | File | Status | Purpose | Requirements | Model | Temperature |
|---|---|---|---|---|---|---|---|
| PR-01 | **1.7** (11 Nov 2026) | `build/PR-01_draft_reply_v1.7.md` | **Active** (the default in `src/generate.py`) | Choose which pieces of the help articles answer the ticket; the code copies them word for word, the whole main article without its Symptoms list | FR-05, FR-07, NFR-04 | openai/gpt-oss-20b (backup openai/gpt-oss-120b) | 0 |
| PR-01 | 1.6 (11 Nov 2026) | `build/PR-01_draft_reply_v1.6.md` | Retired | Every Resolution step added by the code; the model chose any Common cause or Note | FR-05 | same | 0 |
| PR-01 | 1.5 (11 Nov 2026) | `build/PR-01_draft_reply_v1.5.md` | Retired | Every Resolution step asked for in the prompt | FR-05 | same | 0 |
| PR-01 | 1.4 (11 Nov 2026) | `build/PR-01_draft_reply_v1.4.md` | Retired | First word-for-word version: the model chooses numbered pieces | FR-05 | same | 0 |
| PR-01 | 1.3 (9 Nov 2026) | `build/PR-01_draft_reply_v1.3.md` | Retired (kept for the tests that check sentence mode) | Only steps that address this customer's problem | FR-05 | same | 0 |
| PR-01 | 1.2 (8 Nov 2026) | `build/PR-01_draft_reply.md` | Retired (the rollback version) | The model writes its own sentences, each with a required list of sources | FR-05 | same | 0 |
| PR-02 | **1.0** (8 Nov 2026) | `build/PR-02_grounding_check.md` | **Active** | The second model checks that the article fits the situation and every sentence is supported (guardrail "grounding_model") | FR-09, FR-05 | qwen/qwen3.8-27b (a different model family from the writer) | 0 |

**Changing the active reply prompt (and rolling back)** is one setting: `PR01_FILE`, e.g.
`PR01_FILE=PR-01_draft_reply.md` returns to v1.2. Every run records the prompt versions it used in its results file
and metrics report.

## Prompts used to evaluate the system (`evaluation/`)

| ID | Version | File | Status | Purpose | Requirements |
|---|---|---|---|---|---|
| PR-03 | 3 (12 Nov 2026), plus a separate "project" version | `evaluation/PR-03_review_rubric.md` | Active | The marking rules for reviewing replies (human reviewers and an AI reviewer), so both judge by the same words; the text lives in `scripts/review_rubric.py` | Evaluation Framework: hallucination rate, customer-satisfaction proxy, citation accuracy |

## How each version was tested

Each version was tested on the development tickets before it became active; the results are in the "Change history"
table inside each prompt file and in `docs/decision_log.md`. The latest checks of v1.7 on the 500 development tickets
(`scripts/check_replies.py`, 14-15 Nov 2026): every Resolution step of every cited article sent (367 of 367), no reply
with only one step, the database-migration step in every rollback reply (28 of 28), no bullet changed from the article,
no forbidden claim (`scripts/reference_check.py`: 0).
