# Message check: keep an article only if the message alone also finds it

Development tickets: 500. Articles would change for **83** tickets (an article removed; nothing is ever added).

| Measure (tickets whose labels name an article) | Now | With the message check |
|---|---|---|
| Expected article among the articles the writer reads | 346 of 357 | 341 of 357 |
| Expected article first | 324 of 357 | 324 of 357 |
| Tickets where an expected article would be removed | | **10** |

## Every ticket whose articles would change

| Ticket | Question | Subject | Message (start) | Now | With the check | Removed | Expected (labels) |
|---|---|---|---|---|---|---|---|
| DEV-0003 | Q53a | Evidence for a compliance review | Our auditor has asked for access records covering the last s | DOC-SEC-003, DOC-DATA-001, DOC-DATA-003 | DOC-SEC-003, DOC-DATA-001 | DOC-DATA-003 | DOC-SEC-003 |
| DEV-0006 | Q16 | Environment variable not being read | Where should secrets be stored so they do not appear in the  | DOC-DEPLOY-004, DOC-SEC-002, DOC-DEPLOY-001 | DOC-DEPLOY-004, DOC-SEC-002 | DOC-DEPLOY-001 | DOC-ACCT-002, DOC-DEPLOY-004 |
| DEV-0020 | Q49 | SAML login returns an error page | New starters are not being created automatically when they l | DOC-AUTH-003, DOC-AUTH-001, DOC-ONB-001 | DOC-AUTH-003, DOC-ONB-001 | DOC-AUTH-001 | DOC-AUTH-003 |
| DEV-0028 | Q53a | Evidence for a compliance review | Our auditor has asked for access records covering the last s | DOC-SEC-003, DOC-DATA-001, DOC-DATA-003 | DOC-SEC-003, DOC-DATA-001 | DOC-DATA-003 | DOC-SEC-003 |
| DEV-0031 | Q43a | Hitting the rate limit unexpectedly | We started getting 429 responses at around two days ago. Our | DOC-API-001, DOC-BILL-003, DOC-PERF-003 | DOC-API-001, DOC-PERF-003 | DOC-BILL-003 | - |
| DEV-0036 | Q28 | Health check keeps timing out | Every deployment fails at the health check stage. I have inc | DOC-DEPLOY-001, DOC-PERF-001, DOC-ONB-001 | DOC-DEPLOY-001, DOC-ONB-001 | DOC-PERF-001 | DOC-DEPLOY-001 |
| DEV-0039 | Q16 | Config differs between environments | Where should secrets be stored so they do not appear in the  | DOC-DEPLOY-004, DOC-SEC-002, DOC-DEPLOY-001 | DOC-DEPLOY-004, DOC-SEC-002 | DOC-DEPLOY-001 | - |
| DEV-0046 | Q15 | Invoice higher than expected | Our billing period does not seem to match the calendar month | DOC-BILL-001, DOC-BILL-002, DOC-INT-002 | DOC-BILL-001, DOC-BILL-002 | DOC-INT-002 | DOC-BILL-001, DOC-BILL-002 |
| DEV-0050 | Q14 | Question about this month's charges | invoice showing service we not use. can you check and tell? | DOC-BILL-001, DOC-BILL-003, DOC-BILL-002 | DOC-BILL-001, DOC-BILL-002 | DOC-BILL-003 | DOC-BILL-001, DOC-BILL-002 |
| DEV-0054 | Q11 | MFA code keeps getting rejected | We changed the password on our shared account on Monday and  | DOC-AUTH-001, DOC-AUTH-002, DOC-SEC-001 | DOC-AUTH-001, DOC-SEC-001 | DOC-AUTH-002 | DOC-AUTH-001 |
| DEV-0068 | Q25 | Database restore taking hours | We are getting errors saying no connection is available. Thi | DOC-PERF-003, DOC-DATA-002, DOC-DEPLOY-002 | DOC-PERF-003, DOC-DEPLOY-002 | DOC-DATA-002 | DOC-PERF-003 |
| DEV-0072 | Q28 | Health check keeps timing out | Every deployment fails at the health check stage. I have inc | DOC-DEPLOY-001, DOC-PERF-001, DOC-ONB-001 | DOC-DEPLOY-001, DOC-ONB-001 | DOC-PERF-001 | DOC-DEPLOY-001 |
| DEV-0075 | Q30 | Build fails in the pipeline | builds that work last week are now fail during dependency re | DOC-DEPLOY-003, DOC-INT-001, DOC-ONB-001 | DOC-DEPLOY-003, DOC-INT-001 | DOC-ONB-001 | DOC-DEPLOY-001 |
| DEV-0097 | Q53g | Key committed to a public repo | one of our engineers believes their credentials may have bee | DOC-SEC-001, DOC-SEC-002, DOC-AUTH-004 | DOC-SEC-001, DOC-SEC-002 | DOC-AUTH-004 | - |
| DEV-0110 | Q23 | Question about backup regions | We need our data to remain within the EU for a contract we a | DOC-DATA-003, DOC-DATA-002, DOC-ACCT-002 | DOC-DATA-003, DOC-ACCT-002 | DOC-DATA-002 | - |
| DEV-0124 | Q33 | Connecting our CI pipeline | Metrics arriving in our monitoring system lag behind what th | DOC-INT-002, DOC-PERF-001, DOC-INT-001 | DOC-INT-002, DOC-PERF-001 | DOC-INT-001 **(expected!)** | DOC-INT-001, DOC-INT-002 |
| DEV-0137 | Q25 | Database restore taking hours | We are getting errors saying no connection is available. Thi | DOC-PERF-003, DOC-DATA-002, DOC-DEPLOY-002 | DOC-PERF-003, DOC-DEPLOY-002 | DOC-DATA-002 **(expected!)** | DOC-DATA-002, DOC-PERF-003 |
| DEV-0150 | Q53e | Please add per-project spend caps | we want to configure our own retention period rather than ta | DOC-BILL-003, DOC-SEC-003, DOC-ACCT-002 | DOC-BILL-003, DOC-SEC-003 | DOC-ACCT-002 | - |
| DEV-0167 | Q07a | Pagination returns duplicates | Our cursor seems to stop working partway through a long iter | DOC-API-002, DOC-PERF-003, DOC-INT-001 | DOC-API-002, DOC-INT-001 | DOC-PERF-003 | DOC-API-002, DOC-API-003 |
| DEV-0171 | Q28 | Health check keeps timing out | Every deployment fails at the health check stage. I have inc | DOC-DEPLOY-001, DOC-PERF-001, DOC-ONB-001 | DOC-DEPLOY-001, DOC-ONB-001 | DOC-PERF-001 | DOC-DEPLOY-001 |
| DEV-0178 | Q37 | Response times have doubled | latency has been climbing gradually over past couple of days | DOC-PERF-001, DOC-PERF-002, DOC-API-002 | DOC-PERF-001, DOC-PERF-002 | DOC-API-002 | DOC-PERF-001 |
| DEV-0182 | Q07a | How do I page through large results | Our cursor seems to stop working partway through a long iter | DOC-API-002, DOC-API-001, DOC-PERF-003 | DOC-API-002, DOC-API-001 | DOC-PERF-003 | DOC-API-002 |
| DEV-0190 | Q47 | SSO works for some users only | Single sign-on works for our engineering group but the finan | DOC-AUTH-003, DOC-SEC-001, DOC-ACCT-001 | DOC-AUTH-003, DOC-ACCT-001 | DOC-SEC-001 | DOC-AUTH-003 |
| DEV-0194 | Q31 | Connecting our CI pipeline | Log forwarding to our external system stopped last Friday an | DOC-INT-002, DOC-INT-001, DOC-DEPLOY-002 | DOC-INT-002, DOC-DEPLOY-002 | DOC-INT-001 **(expected!)** | DOC-INT-001, DOC-INT-002 |
| DEV-0200 | Q15 | Invoice higher than expected | Our billing period does not seem to match the calendar month | DOC-BILL-001, DOC-BILL-002, DOC-INT-002 | DOC-BILL-001, DOC-BILL-002 | DOC-INT-002 | DOC-BILL-001 |
| DEV-0207 | Q07a | Question about the export endpoint | Our cursor seems to stop working partway through a long iter | DOC-API-002, DOC-API-001, DOC-DATA-001 | DOC-API-002, DOC-API-001 | DOC-DATA-001 | DOC-API-002 |
| DEV-0216 | Q07a | Question about the export endpoint | Our cursor seems to stop working partway through a long iter | DOC-API-002, DOC-API-001, DOC-DATA-001 | DOC-API-002, DOC-API-001 | DOC-DATA-001 | DOC-API-002 |
| DEV-0217 | Q07a | How do I page through large results | Our cursor seems to stop working partway through a long iter | DOC-API-002, DOC-API-001, DOC-PERF-003 | DOC-API-002, DOC-API-001 | DOC-PERF-003 | DOC-API-002, DOC-API-003 |
| DEV-0219 | Q31 | Connecting our CI pipeline | Log forwarding to our external system stopped late last nigh | DOC-INT-002, DOC-INT-001, DOC-DEPLOY-002 | DOC-INT-002, DOC-DEPLOY-002 | DOC-INT-001 **(expected!)** | DOC-INT-001, DOC-INT-002 |
| DEV-0223 | Q33 | Connecting our CI pipeline | Metrics arriving in our monitoring system lag behind what th | DOC-INT-002, DOC-PERF-001, DOC-INT-001 | DOC-INT-002, DOC-PERF-001 | DOC-INT-001 **(expected!)** | DOC-INT-001 |
| DEV-0227 | Q16 | Environment variable not being read | Where should secrets be stored so they do not appear in the  | DOC-DEPLOY-004, DOC-SEC-002, DOC-DEPLOY-001 | DOC-DEPLOY-004, DOC-SEC-002 | DOC-DEPLOY-001 | DOC-ACCT-002, DOC-DEPLOY-004 |
| DEV-0228 | Q14 | Invoice higher than expected | invoice showing service we not use. can you check and tell? | DOC-BILL-001, DOC-BILL-002, DOC-INT-002 | DOC-BILL-001, DOC-BILL-002 | DOC-INT-002 | DOC-BILL-001, DOC-BILL-002 |
| DEV-0233 | Q35 | Migrating our app across | We are planning to migrate an existing application across. I | DOC-ONB-002, DOC-DATA-003, DOC-ONB-001 | DOC-ONB-002, DOC-ONB-001 | DOC-DATA-003 | DOC-ONB-001 |
| DEV-0237 | Q53e | Please add per-project spend caps | We would like to configure our own retention period rather t | DOC-BILL-003, DOC-SEC-003, DOC-ACCT-002 | DOC-BILL-003, DOC-SEC-003 | DOC-ACCT-002 | - |
| DEV-0240 | Q53g | Suspicious activity in audit log | One of our engineers believes their credentials may have bee | DOC-SEC-001, DOC-SEC-002, DOC-SEC-003 | DOC-SEC-001, DOC-SEC-002 | DOC-SEC-003 | - |
| DEV-0250 | Q06 | Key stopped working overnight | A key can read fine but every write returns a permission err | DOC-AUTH-004, DOC-SEC-001, DOC-SEC-002 | DOC-AUTH-004, DOC-SEC-001 | DOC-SEC-002 | DOC-AUTH-004 |
| DEV-0251 | Q34 | Getting started with first deployment | Could you point me at the right starting place? I have creat | DOC-ONB-001, DOC-AUTH-003, DOC-AUTH-001 | DOC-AUTH-003, DOC-AUTH-001 | DOC-ONB-001 **(expected!)** | DOC-ONB-001, DOC-ONB-002 |
| DEV-0258 | Q43a | Throughput drops after a few minutes | too many request error. we have 3 key so limit should be mor | DOC-API-001, DOC-PERF-002, DOC-INT-002 | DOC-API-001 | DOC-PERF-002, DOC-INT-002 | DOC-API-001 |
| DEV-0260 | Q53b | Need audit logs for an auditor | Our policy requires two years of retention. What are our opt | DOC-SEC-003, DOC-SEC-001, DOC-DATA-002 | DOC-SEC-003, DOC-DATA-002 | DOC-SEC-001 | DOC-SEC-003 |
| DEV-0264 | Q07a | Pagination returns duplicates | Our cursor seems to stop working partway through a long iter | DOC-API-002, DOC-PERF-003, DOC-INT-001 | DOC-API-002, DOC-INT-001 | DOC-PERF-003 | DOC-API-002 |
| DEV-0265 | Q53a | Evidence for a compliance review | Our auditor has asked for access records covering the last s | DOC-SEC-003, DOC-DATA-001, DOC-DATA-003 | DOC-SEC-003, DOC-DATA-001 | DOC-DATA-003 | DOC-SEC-003 |
| DEV-0266 | Q01 | Permission changes not taking effect | One of our developers cannot see a project she should have a | DOC-ACCT-001, DOC-ACCT-002, DOC-SEC-003 | DOC-ACCT-001, DOC-ACCT-002 | DOC-SEC-003 | - |
| DEV-0274 | Q37 | Service slow at peak hours | Latency has been climbing gradually over the past most of th | DOC-PERF-001, DOC-BILL-003, DOC-API-001 | DOC-PERF-001, DOC-API-001 | DOC-BILL-003 | DOC-PERF-001, DOC-PERF-002 |
| DEV-0280 | Q29 | Build fails in the pipeline | Our deployment reaches running and then rolls back after abo | DOC-DEPLOY-003, DOC-DEPLOY-001, DOC-ONB-001 | DOC-DEPLOY-001, DOC-ONB-001 | DOC-DEPLOY-003 | - |
| DEV-0282 | Q53g | Possible account compromise | one of our engineers believes their credentials may have bee | DOC-SEC-001, DOC-SEC-002, DOC-INT-001 | DOC-SEC-001, DOC-SEC-002 | DOC-INT-001 | DOC-SEC-001, DOC-SEC-002 |
| DEV-0290 | Q38 | p95 latency is very high | Our response times have roughly doubled since yesterday morn | DOC-PERF-001, DOC-DATA-003, DOC-INT-002 | DOC-PERF-001, DOC-INT-002 | DOC-DATA-003 | DOC-PERF-001, DOC-PERF-002 |
| DEV-0295 | Q34 | Migrating our app across | can you please point me at the right starting place? i am ha | DOC-DATA-003, DOC-AUTH-001, DOC-ONB-002 | DOC-AUTH-001 | DOC-DATA-003, DOC-ONB-002 | DOC-ONB-001 |
| DEV-0310 | Q34 | Migrating our app across | Could you point me at the right starting place? I have creat | DOC-AUTH-001, DOC-DATA-003, DOC-ONB-002 | DOC-AUTH-001 | DOC-DATA-003, DOC-ONB-002 **(expected!)** | DOC-ONB-001, DOC-ONB-002 |
| DEV-0320 | Q07a | How do I page through large results | Our cursor seems to stop working partway through a long iter | DOC-API-002, DOC-API-001, DOC-PERF-003 | DOC-API-002, DOC-API-001 | DOC-PERF-003 | DOC-API-002 |
| DEV-0325 | Q33 | Connecting our CI pipeline | Metrics arriving in our monitoring system lag behind what th | DOC-INT-002, DOC-PERF-001, DOC-INT-001 | DOC-INT-002, DOC-PERF-001 | DOC-INT-001 | - |
| DEV-0330 | Q26 | No connections available error | Our connection pool appears to be exhausting under moderate  | DOC-PERF-003, DOC-AUTH-003, DOC-DEPLOY-001 | DOC-PERF-003, DOC-DEPLOY-001 | DOC-AUTH-003 | DOC-PERF-003 |
| DEV-0341 | Q31 | Connecting our CI pipeline | log forwarding to our external system stop late last night a | DOC-INT-002, DOC-INT-001, DOC-SEC-002 | DOC-INT-002 | DOC-INT-001, DOC-SEC-002 **(expected!)** | DOC-INT-001 |
| DEV-0342 | Q45 | Bad release in production | how do I revert to earlier revision? The release we put out  | DOC-DEPLOY-002, DOC-DEPLOY-001, DOC-AUTH-001 | DOC-DEPLOY-002, DOC-DEPLOY-001 | DOC-AUTH-001 | - |
| DEV-0344 | Q53e | Please add per-project spend caps | we want to configure our own retention period rather than ta | DOC-BILL-003, DOC-SEC-003, DOC-ACCT-002 | DOC-BILL-003, DOC-SEC-003 | DOC-ACCT-002 | - |
| DEV-0348 | Q53b | Need audit logs for an auditor | Our policy requires two years of retention. What are our opt | DOC-SEC-003, DOC-SEC-001, DOC-DATA-002 | DOC-SEC-003, DOC-DATA-002 | DOC-SEC-001 | DOC-SEC-003 |
| DEV-0353 | Q29 | Build fails in the pipeline | Our deployment reaches running and then rolls back after abo | DOC-DEPLOY-003, DOC-DEPLOY-001, DOC-ONB-001 | DOC-DEPLOY-001, DOC-ONB-001 | DOC-DEPLOY-003 | - |
| DEV-0368 | Q07a | Pagination returns duplicates | Our cursor seems to stop working partway through a long iter | DOC-API-002, DOC-PERF-003, DOC-INT-001 | DOC-API-002, DOC-INT-001 | DOC-PERF-003 | DOC-API-002, DOC-API-003 |
| DEV-0374 | Q25 | Database restore taking hours | we get errors saying no connection is available. This start  | DOC-DATA-002, DOC-PERF-003, DOC-DEPLOY-002 | DOC-PERF-003 | DOC-DATA-002, DOC-DEPLOY-002 | - |
| DEV-0377 | Q08 | Question about the export endpoint | What is the right way to pull a very large extract? Requesti | DOC-API-002, DOC-DATA-001, DOC-API-001 | DOC-API-002, DOC-DATA-001 | DOC-API-001 | DOC-API-002 |
| DEV-0378 | Q25 | Database restore taking hours | connection not available error coming. we scale up service t | DOC-DATA-002, DOC-PERF-003, DOC-DEPLOY-001 | DOC-PERF-003, DOC-DEPLOY-001 | DOC-DATA-002 | DOC-PERF-003 |
| DEV-0384 | Q07a | How do I page through large results | Our cursor seems to stop working partway through a long iter | DOC-API-002, DOC-API-001, DOC-PERF-003 | DOC-API-002, DOC-API-001 | DOC-PERF-003 | - |
| DEV-0385 | Q41 | Usage allowance already consumed | We were throttled on Monday after a traffic increase and it  | DOC-BILL-003, DOC-BILL-001, DOC-BILL-002 | DOC-BILL-003, DOC-BILL-002 | DOC-BILL-001 | DOC-BILL-003 |
| DEV-0391 | Q53g | Suspicious activity in audit log | One of our engineers believes their credentials may have bee | DOC-SEC-001, DOC-SEC-002, DOC-SEC-003 | DOC-SEC-001, DOC-SEC-002 | DOC-SEC-003 | DOC-SEC-001 |
| DEV-0394 | Q43a | Throughput drops after a few minutes | We started getting 429 responses at around around 14:00 yest | DOC-API-001, DOC-PERF-001, DOC-INT-002 | DOC-API-001, DOC-PERF-001 | DOC-INT-002 | DOC-API-001 |
| DEV-0403 | Q47 | SSO works for some users only | Single sign-on works for our engineering group but the finan | DOC-AUTH-003, DOC-SEC-001, DOC-ACCT-001 | DOC-AUTH-003, DOC-ACCT-001 | DOC-SEC-001 | DOC-AUTH-003 |
| DEV-0416 | Q30 | Build fails in the pipeline | Builds that worked last week are now failing during dependen | DOC-DEPLOY-003, DOC-ONB-001, DOC-INT-001 | DOC-DEPLOY-003 | DOC-ONB-001, DOC-INT-001 | DOC-DEPLOY-001 |
| DEV-0422 | Q07a | Question about the export endpoint | Our cursor seems to stop working partway through a long iter | DOC-API-002, DOC-API-001, DOC-DATA-001 | DOC-API-002, DOC-API-001 | DOC-DATA-001 | DOC-API-002 |
| DEV-0437 | Q39 | p95 latency is very high | The service is noticeably slow during our afternoon peak and | DOC-PERF-001, DOC-DATA-003, DOC-PERF-002 | DOC-PERF-001, DOC-PERF-002 | DOC-DATA-003 | DOC-PERF-001, DOC-PERF-002 |
| DEV-0439 | Q26 | Database restore taking hours | Our connection pool appears to be exhausting under moderate  | DOC-PERF-003, DOC-DATA-002, DOC-ONB-002 | DOC-PERF-003 | DOC-DATA-002, DOC-ONB-002 | - |
| DEV-0442 | Q29 | Build fails in the pipeline | Our deployment reaches running and then rolls back after abo | DOC-DEPLOY-003, DOC-DEPLOY-001, DOC-ONB-001 | DOC-DEPLOY-001, DOC-ONB-001 | DOC-DEPLOY-003 | - |
| DEV-0448 | Q53b | Need audit logs for an auditor | Our policy requires two years of retention. What are our opt | DOC-SEC-003, DOC-SEC-001, DOC-DATA-002 | DOC-SEC-003, DOC-DATA-002 | DOC-SEC-001 | DOC-SEC-003 |
| DEV-0449 | Q29 | Build fails in the pipeline | Our deployment reaches running and then rolls back after abo | DOC-DEPLOY-003, DOC-DEPLOY-001, DOC-ONB-001 | DOC-DEPLOY-001, DOC-ONB-001 | DOC-DEPLOY-003 | DOC-DEPLOY-001 |
| DEV-0456 | Q53e | Please add per-project spend caps | we want to configure our own retention period rather than ta | DOC-BILL-003, DOC-SEC-003, DOC-ACCT-002 | DOC-BILL-003, DOC-SEC-003 | DOC-ACCT-002 | - |
| DEV-0462 | Q34 | Getting started with first deployment | Could you point me at the right starting place? I have creat | DOC-ONB-001, DOC-AUTH-003, DOC-AUTH-001 | DOC-AUTH-003, DOC-AUTH-001 | DOC-ONB-001 **(expected!)** | DOC-ONB-001 |
| DEV-0469 | Q31 | Connecting our CI pipeline | log forwarding to our external system stop yesterday morning | DOC-INT-002, DOC-INT-001, DOC-SEC-002 | DOC-INT-002 | DOC-INT-001, DOC-SEC-002 **(expected!)** | DOC-INT-001, DOC-INT-002 |
| DEV-0470 | Q53g | Suspicious activity in audit log | One of our engineers believes their credentials may have bee | DOC-SEC-001, DOC-SEC-002, DOC-SEC-003 | DOC-SEC-001, DOC-SEC-002 | DOC-SEC-003 | - |
| DEV-0471 | Q49 | SAML login returns an error page | new starters not being created automatically when they log i | DOC-AUTH-003, DOC-ONB-001, DOC-AUTH-001 | DOC-AUTH-003, DOC-ONB-001 | DOC-AUTH-001 | DOC-AUTH-003 |
| DEV-0475 | Q53g | Suspicious activity in audit log | one of our engineers believes their credentials may have bee | DOC-SEC-001, DOC-SEC-002, DOC-SEC-003 | DOC-SEC-001, DOC-SEC-002 | DOC-SEC-003 | DOC-SEC-001 |
| DEV-0480 | Q30 | Build fails in the pipeline | Builds that worked last week are now failing during dependen | DOC-DEPLOY-003, DOC-ONB-001, DOC-INT-001 | DOC-DEPLOY-003 | DOC-ONB-001, DOC-INT-001 | - |
| DEV-0481 | Q07b | How do I page through large results | When I page through results I am seeing some records twice a | DOC-API-002, DOC-DATA-001, DOC-API-001 | DOC-API-002, DOC-DATA-001 | DOC-API-001 | DOC-API-002 |
| DEV-0482 | Q07a | Pagination returns duplicates | Our cursor seems to stop working partway through a long iter | DOC-API-002, DOC-PERF-003, DOC-INT-001 | DOC-API-002, DOC-INT-001 | DOC-PERF-003 | DOC-API-002, DOC-API-003 |
| DEV-0491 | Q06 | Need to rotate an exposed key | A key can read fine but every write returns a permission err | DOC-AUTH-004, DOC-SEC-002, DOC-ACCT-001 | DOC-AUTH-004 | DOC-SEC-002, DOC-ACCT-001 | DOC-AUTH-004 |
| DEV-0496 | Q35 | Getting started with first deployment | We are planning to migrate an existing application across. I | DOC-ONB-002, DOC-ONB-001, DOC-DEPLOY-001 | DOC-ONB-002, DOC-ONB-001 | DOC-DEPLOY-001 | DOC-ONB-001, DOC-ONB-002 |
