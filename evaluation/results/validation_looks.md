# Validation looks (record)

Every time the 80 validation tickets were run, and what happened because of it. Validation is for measurement only;
the system is built on the 500 development tickets.

| Date | Run | Where | Version | Changed because of it |
|---|---|---|---|---|
| 13 Nov 2026 | validation_run_7.json | real project, Groq free tier | before the 13-14 Nov walkthrough changes | nothing |
| 14 Nov 2026 17:38 | sandbox_validation_before_message_only.json | sandbox, OpenRouter (paid) | walkthrough decisions; learned layer reads subject and message | nothing |
| 14 Nov 2026 18:14 | sandbox_validation_message_only.json | sandbox, OpenRouter (paid) | walkthrough decisions; learned layer reads the message only | nothing |

The message-only change was decided on the 500 development tickets (scripts/compare_decision_text.py) before either
14 Nov validation run. Mohnish Grover, 14 Nov 2026: "we don't decide on that we just have a look at the results".
The reportable validation run is the single final run on Groq's free tier in the real project, with no changes afterwards.
