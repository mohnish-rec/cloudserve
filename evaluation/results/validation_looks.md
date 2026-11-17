# Validation looks (record)

Every time the 80 validation tickets were run, and what happened because of it. Validation is for measurement only;
the system is built on the 500 development tickets.

| Date | Run | Where | Version | Changed because of it |
|---|---|---|---|---|
| 13 Nov 2026 | validation_run_7.json | real project, Groq free tier | before the 13-14 Nov walkthrough changes | nothing |
| 14 Nov 2026 17:38 | sandbox_validation_before_message_only.json | sandbox, OpenRouter (paid) | walkthrough decisions; learned layer reads subject and message | nothing |
| 14 Nov 2026 18:14 | sandbox_validation_message_only.json | sandbox, OpenRouter (paid) | walkthrough decisions; learned layer reads the message only | nothing |
| 15 Nov 2026 21:00 | sandbox_validation_read_cache.json | sandbox, OpenRouter (paid), reply cache read only (development answers reused, nothing stored) | as 14 Nov 18:14 plus the plan rule (15 Nov) | nothing |

The message-only change was decided on the 500 development tickets (scripts/compare_decision_text.py) before either
14 Nov validation run. Mohnish Grover, 14 Nov 2026: "we don't decide on that we just have a look at the results".
The reportable validation run is the single final run on Groq's free tier in the real project, with no changes afterwards.

The 15 Nov run tested whether development results carry over (Mohnish Grover: "we are testing if it replicates our development ticket results"). 35 of 57 replies came from the development cache, and all 35 had the same decision and the same reply as the fresh run of 14 Nov 18:14; the cache still held 486 entries afterwards (nothing stored). The one other difference, VAL-0051, came from the plan rule. Whether to ship a cache is decided on the development simulation (about half of a hidden-like set matches a development ticket exactly) and the team's answer, not on this run.
