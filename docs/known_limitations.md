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
