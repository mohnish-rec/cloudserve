# Known limitations (for the report)

Found while building and testing on the 500 development tickets. Each one is recorded, not fixed, for the reason given.

## 1. A subject line that contradicts the message (14 Nov 2026)

**What happens.** The search reads the subject and the message together. When the subject points at a different
problem from the message, the subject can pull in an extra article. Example: subject "Database restore taking hours",
message about connection errors after scaling up.

| Ticket | Fluency | Reply |
|---|---|---|
| DEV-0068, DEV-0137, DEV-0439 | fluent | connection pool article only (right) |
| DEV-0374, DEV-0378 | non-fluent | restore article first, then the connection pool article |
| VAL-0078 (seen when looking at validation; nothing changed because of it) | non-fluent | restore article first, then the connection pool article |

**Effect.** The customer still gets every step that solves the problem, copied exactly from the article, but second,
and without that article's causes and note. Non-fluent customers are answered at the same rate, but this reply is
less clear for them: a short or non-fluent message is outweighed by its subject. The same subject problem sends
DEV-0295, DEV-0310 and DEV-0474 ("Migrating our app across") the migration article, and DEV-0170 (no subject) was
found the permissions article, which the checker blocked.

**Why it is not fixed.** Two fixes were tested on all 500 development tickets and not built:
- search on the message alone (13 Nov, scripts/compare_search_query.py): 5 tickets better, 4 worse;
- "message check", keep an article only if the message alone also finds it (14 Nov, scripts/compare_message_check.py):
  fixed DEV-0374, DEV-0378 and DEV-0439 but removed a needed article from 10 tickets, including the getting-started
  article from DEV-0251 and DEV-0462.
For many tickets the subject is the more accurate part. Mohnish Grover, 14 Nov 2026: "lets keep how it was" and
"keep that in the report".

**What still protects the customer.** The checker blocks a reply whose article does not fit (DEV-0170), and the
reply invites the customer to reply if it did not solve the problem; a repeat question goes to a person (follow-up rule).

## 2. Replies can vary slightly between separate runs (15 Nov 2026)

**What happens.** The same input always gets the same decision (A5): all 500 development decisions were identical
across two runs (14 and 15 Nov). Within one run, identical tickets also get the identical reply (the run memory).
Between separate runs with the reply cache off, the writer occasionally chooses a different article mix:
5 of 357 replies changed between two runs (e.g. DEV-0089, Q39: one article in one run, two in the other).

**Identical messages with different subjects.** Of 59 groups of identical messages answered automatically, 52 got the
same articles; in the other 7 the subject line pulled in a different article (see limitation 1). In Q02 ("remove all
his access including key he made") the one-article reply still contains the whole answer: "Remove a departing user
rather than only changing their password, and revoke any API keys they created."

**Why it is not changed.** The reply cache (D-025) makes runs reproducible and is used for development runs, as the
Build Specification encourages ("Cache model responses during development"). Validation and final runs keep it off so
they stay a fresh test. Mohnish Grover, 15 Nov 2026: "we dont need caching on validation tickets as we only them for
testing and not training".

## 3. A Common cause can describe another customer's situation (15 Nov 2026)

**What happens.** Since PR-01 v1.7 (11 Nov) the main article's Common causes are always included, because for some
questions a cause is the answer (Q01: "The role was granted at project scope rather than organisation scope").
For others a cause is noise: in Q41 the reply would include "Overage protection is disabled, so usage continued beyond
the allowance", the opposite of the customer's situation. Mohnish Grover, 15 Nov 2026: "send it to a person because of
the noise" (Q41 stays with a person).

## 4. The learned decisions layer cannot spot a brand-new "person" question (14 Nov 2026)

**What happens.** It learned Mohnish Grover's decisions on the development tickets: 384 of 384 matched, also on
unseen wordings (scripts/learn_decisions.py, test A). A question it has never seen at all is not recognised as one
for a person (test B: 0 of 25). Daniel's safety rules and the zero-tolerance types still apply underneath.

## 5. Q41 in other words is missed (14 Nov 2026)

**What happens.** Q41 ("throttled… rather pay overage") goes to a person. Reworded ("We got rate limited… We'd prefer
to pay extra than be cut off"), neither the Q41 word rule nor the learned layer (29%) catches it, so it would be
answered from the billing article. Kept as an expected-to-fail test (tests/test_decisions.py), so the gap stays visible.

## 6. Speed on the free tier (12-15 Nov 2026)

**What happens.** The target is under 3 seconds for 95% of tickets (NFR-01). On Groq's free tier the 95th percentile
was 10.4 s for 80 tickets and 306 s for 500 (waiting through rate limits); even on the paid route in the sandbox it
was about 5 s. Median is under 1 second because tickets for a person need no model call.

## 7. Some article wording is meant for a support agent (11-15 Nov 2026)

**What happens.** A few steps are written to the agent ("Ask the user to check…"); copied word for word under the rule
"Never change Ines's words", they read oddly to a customer. Found in 6 replies of the latest 500-ticket run
(DEV-0008, DEV-0176, DEV-0281, DEV-0312, DEV-0335, DEV-0409; scripts/check_replies.py).

## Fixed

- **Plan-limited articles answered for Standard customers (fixed 15 Nov 2026).** Articles that apply to Business and
  Enterprise plans only were sent to Standard customers (Q31, Q47, Q48, Q49: 16 tickets). The plan rule (src/plans.py)
  now sends these to a person with the draft. Mohnish Grover: "It should be a general rule because if the standard
  plan customers cannot get their answers with it then it will be useless". Run sandbox_dev500_plan_rule: 16 of 16
  to a person with the draft, nothing else changed by it, all three fairness gaps under 5 points.
