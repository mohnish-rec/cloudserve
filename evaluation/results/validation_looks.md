# Validation looks (record)

Every time the 80 validation tickets were run, and what happened because of it. Validation is for measurement only;
the system is built on the 500 development tickets.

Every run of the 80 validation tickets is listed here: 14 so far, and the final run to come (course team, 17 Nov 2026: "Running validation
multiple times is fine. Make sure you document all runs and avoid using validation results to directly tune your
system."; Dataset Guide: "Check yourself against the 80 validation tickets as often as you want"). Completed 17 Nov
2026 from the result files; the runs of 8-12 Nov were missing from the first version of this record.

| # | Date (UTC) | Run | Where | System version | Changed because of it |
|---|---|---|---|---|---|
| 1 | 8 Nov 02:42 | validation_run.json | real project, Groq free tier | PR-01 v1.2 (first baseline) | Nothing written for a validation ticket. Results were read ticket by ticket (disclosed in D-026) |
| 2 | 9 Nov 15:50 | validation_run_2.json | real project, Groq free tier | PR-01 v1.2 with the D-022 fix | Nothing: a check of a fix found on development tickets |
| 3 | 10 Nov 18:47 | validation_run_3.json | sandbox, OpenRouter (paid) | PR-01 v1.3, trim, narrowed rules | Nothing in the system |
| 4 | 11 Nov 13:30 | validation_run_4.json (and a citation audit) | sandbox, paid | PR-01 v1.4 | Nothing in the system. Type-aware search, tested an hour later, came from development run v14 (11 Nov 11:50) |
| 5 | 12 Nov 01:07 | validation_run_5.json (AI check with rubric v1, fairness audit) | sandbox, paid | PR-01 v1.7 | The AI check's 1 out of 5 for VAL-0008 led to the score descriptions in rubric v2's question C. **Removed 17 Nov** (rubric v4). Nothing in the system |
| 6 | 12 Nov 01:25 | validation_v15.json (re-run of an older version) | sandbox, paid | PR-01 v1.5 | Six rollback replies scored 5 out of 5 without the migration step, which led to rubric v3. **Rubric v3 removed 17 Nov.** Nothing in the system (PR-01 v1.7 was already final) |
| 7 | 12 Nov 01:31 | validation_v16.json (re-run of an older version) | sandbox, paid | PR-01 v1.6 | Nothing |
| 8 | 12 Nov 02:33 | validation_run_6_WRONG_SETTINGS_v1.6.json | sandbox, paid | PR-01 v1.6 by mistake | Nothing: re-run with the right settings (run 9) |
| 9 | 12 Nov 03:18 | validation_run_6.json (and a scorecard) | sandbox, paid | PR-01 v1.7 | Nothing |
| 10 | 12 Nov 04:58 | validation_run_7.json | real project, Groq free tier | PR-01 v1.7, final design of 12 Nov | Nothing |
| 11 | 14 Nov 17:38 | sandbox_validation_before_message_only.json | sandbox, paid | walkthrough decisions; learned layer reads subject and message | Nothing |
| 12 | 14 Nov 18:14 | sandbox_validation_message_only.json | sandbox, paid | walkthrough decisions; learned layer reads the message only | Nothing |
| 13 | 15 Nov 21:04 | sandbox_validation_read_cache.json | sandbox, paid, reply cache read only (development answers reused, nothing stored) | as run 12 plus the plan rule | Nothing |
| 14 | 17 Nov 23:44 | sandbox_validation_frozen_17nov.json | sandbox, paid, no cache | the frozen final system (as the final development run) | Nothing: a look before the reportable run, to compare the paid and free routes (Mohnish Grover, 17 Nov: "I'll do first on sandbox and later on the free tier too so that we can compare them as well") |
| 15 | (to come) | the final validation run (reportable) | real project, Groq free tier, no cache | the frozen final system | Nothing will be changed after it |

Checked on 17 Nov 2026: every rule and setting in the system has its own development-ticket evidence (no rule,
prompt or test names a validation ticket), and the only things validation shaped, rubric v2's score descriptions and
rubric v3, were removed on 17 Nov. The file evaluation/samples/mixed_sets_120.json (12 Nov, in the sandbox) mixes 42
validation tickets into 120-ticket samples; it was used only to measure, never to build.

The message-only change was decided on the 500 development tickets (scripts/compare_decision_text.py) before either
14 Nov validation run. Mohnish Grover, 14 Nov 2026: "we don't decide on that we just have a look at the results".
The reportable validation run is the single final run on Groq's free tier in the real project, with no changes afterwards.

The 15 Nov run tested whether development results carry over (Mohnish Grover: "we are testing if it replicates our development ticket results"). 35 of 57 replies came from the development cache, and all 35 had the same decision and the same reply as the fresh run of 14 Nov 18:14; the cache still held 486 entries afterwards (nothing stored). The one other difference, VAL-0051, came from the plan rule. Whether to ship a cache is decided on the development simulation (about half of a hidden-like set matches a development ticket exactly) and the team's answer, not on this run.
