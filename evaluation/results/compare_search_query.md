# Search on subject + message (now) vs the message alone

Development tickets: 500. Top 3 articles changed for 235 tickets.

| Measure (tickets whose labels name an article) | Subject + message | Message alone |
|---|---|---|
| Expected article in the top 3 | 346 of 357 | 340 of 357 |
| Expected article ranked first | 324 of 357 | 310 of 357 |

## Every ticket whose top 3 changed

| Ticket | Subject | Message (start) | Top 3 now | Top 3 on the message alone |
|---|---|---|---|---|
| DEV-0003 | Evidence for a compliance review | Our auditor has asked for access records covering the last six months. | DOC-SEC-003, DOC-DATA-001, DOC-DATA-003 | DOC-DATA-001, DOC-SEC-003, DOC-SEC-001 |
| DEV-0006 | Environment variable not being read | Where should secrets be stored so they do not appear in the logs? At t | DOC-DEPLOY-004, DOC-SEC-002, DOC-DEPLOY-001 | DOC-DEPLOY-004, DOC-SEC-002, DOC-DATA-003 |
| DEV-0008 | MFA code keeps getting rejected | Since around 14:00 yesterday I cannot get into the console at all. My  | DOC-AUTH-002, DOC-AUTH-001, DOC-ACCT-001 | DOC-AUTH-001, DOC-SEC-001, DOC-AUTH-002 |
| DEV-0014 | Help configuring single sign-on | We are setting up SAML with our identity provider and users are being  | DOC-AUTH-003, DOC-AUTH-002, DOC-SEC-001 | DOC-AUTH-003, DOC-SEC-001, DOC-AUTH-002 |
| DEV-0015 | Possible account compromise | A former employee appears to still have access three weeks after leavi | DOC-SEC-001, DOC-ACCT-001, DOC-AUTH-001 | DOC-SEC-001, DOC-AUTH-004, DOC-AUTH-001 |
| DEV-0016 | Need to rotate an exposed key | one of our engineers pushed key to a public repository by mistake. We  | DOC-AUTH-004, DOC-SEC-002, DOC-SEC-001 | DOC-SEC-001, DOC-INT-001, DOC-AUTH-004 |
| DEV-0017 | User cannot access a project | One of our developers cannot see a project she should have access to.  | DOC-ACCT-001, DOC-ACCT-002, DOC-AUTH-004 | DOC-ACCT-001, DOC-ACCT-002, DOC-AUTH-003 |
| DEV-0019 | Remove a departing team member | A team member left earlier today and I want to make sure their access  | DOC-ACCT-001, DOC-SEC-001, DOC-AUTH-004 | DOC-ACCT-001, DOC-AUTH-004, DOC-SEC-001 |
| DEV-0020 | SAML login returns an error page | New starters are not being created automatically when they log in thro | DOC-AUTH-003, DOC-AUTH-001, DOC-ONB-001 | DOC-AUTH-003, DOC-ONB-001, DOC-AUTH-002 |
| DEV-0021 | Evidence for a compliance review | Our policy requires two years of retention. What are our options given | DOC-SEC-003, DOC-DATA-003, DOC-DATA-002 | DOC-SEC-003, DOC-DATA-002, DOC-ONB-001 |
| DEV-0024 | Database restore taking hours | A restore we started over the weekend is still running. The database i | DOC-DATA-002, DOC-PERF-003, DOC-DATA-001 | DOC-DATA-002, DOC-DATA-001, DOC-PERF-003 |
| DEV-0027 | Pagination returns duplicates | What is the right way to pull a very large extract? Requesting a big p | DOC-API-002, DOC-DATA-001, DOC-PERF-003 | DOC-API-002, DOC-DATA-001, DOC-DEPLOY-002 |
| DEV-0028 | Evidence for a compliance review | Our auditor has asked for access records covering the last six months. | DOC-SEC-003, DOC-DATA-001, DOC-DATA-003 | DOC-DATA-001, DOC-SEC-003, DOC-SEC-001 |
| DEV-0030 | Bad release in production | We shipped a release yesterday morning that has broken checkout for a  | DOC-DEPLOY-002, DOC-DEPLOY-003, DOC-DATA-002 | DOC-DEPLOY-002, DOC-DATA-002, DOC-DEPLOY-003 |
| DEV-0031 | Hitting the rate limit unexpectedly | We started getting 429 responses at around two days ago. Our traffic h | DOC-API-001, DOC-BILL-003, DOC-PERF-003 | DOC-API-001, DOC-INT-002, DOC-PERF-001 |
| DEV-0036 | Health check keeps timing out | Every deployment fails at the health check stage. I have increased the | DOC-DEPLOY-001, DOC-PERF-001, DOC-ONB-001 | DOC-DEPLOY-001, DOC-ONB-001, DOC-INT-001 |
| DEV-0037 | Monitoring integration setup | Log forwarding to our external system stopped around 14:00 yesterday a | DOC-INT-002, DOC-SEC-003, DOC-DEPLOY-002 | DOC-INT-002, DOC-BILL-003, DOC-DEPLOY-002 |
| DEV-0039 | Config differs between environments | Where should secrets be stored so they do not appear in the logs? At t | DOC-DEPLOY-004, DOC-SEC-002, DOC-DEPLOY-001 | DOC-DEPLOY-004, DOC-SEC-002, DOC-DATA-003 |
| DEV-0044 | Usage allowance already consumed | our spend cap stop production workload overnight. We need it raised im | DOC-BILL-003, DOC-BILL-001, DOC-API-001 | DOC-BILL-003, DOC-API-001, DOC-BILL-002 |
| DEV-0046 | Invoice higher than expected | Our billing period does not seem to match the calendar month, which is | DOC-BILL-001, DOC-BILL-002, DOC-INT-002 | DOC-BILL-001, DOC-ACCT-002, DOC-BILL-002 |
| DEV-0049 | Monitoring integration setup | We are connecting our CI pipeline and are not sure whether to use a pe | DOC-INT-001, DOC-AUTH-004, DOC-SEC-002 | DOC-INT-001, DOC-SEC-002, DOC-AUTH-004 |
| DEV-0050 | Question about this month's charges | invoice showing service we not use. can you check and tell? | DOC-BILL-001, DOC-BILL-003, DOC-BILL-002 | DOC-BILL-001, DOC-BILL-002, DOC-INT-001 |
| DEV-0052 | Build fails in the pipeline | Every deployment fails at the health check stage. I have increased the | DOC-DEPLOY-001, DOC-DEPLOY-003, DOC-ONB-001 | DOC-DEPLOY-001, DOC-ONB-001, DOC-INT-001 |
| DEV-0053 | How do I revert to the previous revision | We shipped a release two days ago that has broken checkout for a porti | DOC-DEPLOY-002, DOC-DEPLOY-003, DOC-DATA-002 | DOC-DEPLOY-002, DOC-API-003, DOC-DATA-002 |
| DEV-0054 | MFA code keeps getting rejected | We changed the password on our shared account on Monday and now our au | DOC-AUTH-001, DOC-AUTH-002, DOC-SEC-001 | DOC-AUTH-001, DOC-SEC-001, DOC-AUTH-003 |
| DEV-0058 | Question about backup regions | One of our customers has asked for written confirmation of where their | DOC-DATA-003, DOC-DATA-002, DOC-ONB-002 | DOC-DATA-003, DOC-DATA-002, DOC-DATA-001 |
| DEV-0063 | User cannot access a project | One of our developers cannot see a project she should have access to.  | DOC-ACCT-001, DOC-ACCT-002, DOC-AUTH-004 | DOC-ACCT-001, DOC-ACCT-002, DOC-AUTH-003 |
| DEV-0064 | Unexpected overage charges | Our spend cap stopped a production workload overnight. We need it rais | DOC-BILL-003, DOC-BILL-001, DOC-API-001 | DOC-BILL-003, DOC-API-001, DOC-BILL-001 |
| DEV-0066 | Pagination returns duplicates | What is the right way to pull a very large extract? Requesting a big p | DOC-API-002, DOC-DATA-001, DOC-PERF-003 | DOC-API-002, DOC-DATA-001, DOC-DEPLOY-002 |
| DEV-0067 | Signature verification failing | signature verification fails for every delivery. We are computing sign | DOC-API-003, DOC-AUTH-003, DOC-INT-002 | DOC-API-003, DOC-INT-002, DOC-AUTH-002 |
| DEV-0068 | Database restore taking hours | We are getting errors saying no connection is available. This started  | DOC-PERF-003, DOC-DATA-002, DOC-DEPLOY-002 | DOC-PERF-003, DOC-DEPLOY-001, DOC-DEPLOY-002 |
| DEV-0071 | Signature verification failing | Our webhook endpoint has stopped receiving events since late last nigh | DOC-API-003, DOC-AUTH-004, DOC-DEPLOY-001 | DOC-API-003, DOC-DEPLOY-001, DOC-API-001 |
| DEV-0072 | Health check keeps timing out | Every deployment fails at the health check stage. I have increased the | DOC-DEPLOY-001, DOC-PERF-001, DOC-ONB-001 | DOC-DEPLOY-001, DOC-ONB-001, DOC-INT-001 |
| DEV-0074 | Usage allowance already consumed | We were throttled around 14:00 yesterday after a traffic increase and  | DOC-BILL-003, DOC-BILL-001, DOC-BILL-002 | DOC-BILL-003, DOC-BILL-002, DOC-INT-002 |
| DEV-0075 | Build fails in the pipeline | builds that work last week are now fail during dependency resolution.  | DOC-DEPLOY-003, DOC-INT-001, DOC-ONB-001 | DOC-DEPLOY-003, DOC-DEPLOY-002, DOC-SEC-002 |
| DEV-0076 | SAML login returns an error page | Single sign-on works for our engineering group but the finance group g | DOC-AUTH-003, DOC-AUTH-001, DOC-ACCT-001 | DOC-AUTH-003, DOC-AUTH-001, DOC-API-003 |
| DEV-0080 | Webhooks not arriving | Signature verification fails for every delivery. We are computing the  | DOC-API-003, DOC-AUTH-003, DOC-INT-002 | DOC-API-003, DOC-INT-002, DOC-AUTH-003 |
| DEV-0082 | Config differs between environments | our staging environment is picking up production configuration values. | DOC-DEPLOY-004, DOC-SEC-002, DOC-ACCT-002 | DOC-DEPLOY-004, DOC-SEC-002, DOC-DEPLOY-001 |
| DEV-0092 | Usage allowance already consumed | Our spend cap stopped a production workload overnight. We need it rais | DOC-BILL-003, DOC-BILL-001, DOC-API-001 | DOC-BILL-003, DOC-API-001, DOC-BILL-001 |
| DEV-0094 | Remove a departing team member | user left company. how i remove all his access including key he made? | DOC-ACCT-001, DOC-SEC-001, DOC-AUTH-004 | DOC-AUTH-004, DOC-ACCT-001, DOC-SEC-001 |
| DEV-0095 | Response times have doubled | service not isiceably slow during our afternoon peak and fine rest of  | DOC-PERF-001, DOC-PERF-002, DOC-INT-002 | DOC-PERF-001, DOC-PERF-002, DOC-DEPLOY-002 |
| DEV-0097 | Key committed to a public repo | one of our engineers believes their credentials may have been exposed  | DOC-SEC-001, DOC-SEC-002, DOC-AUTH-004 | DOC-SEC-001, DOC-SEC-002, DOC-INT-002 |
| DEV-0101 | Config differs between environments | i am having set environment variable but application not able to see i | DOC-DEPLOY-004, DOC-ACCT-002, DOC-DEPLOY-001 | DOC-DEPLOY-004, DOC-SEC-002, DOC-ONB-001 |
| DEV-0102 | Retention period question | Our auditor has asked for access records covering the last six months. | DOC-SEC-003, DOC-DATA-001, DOC-BILL-001 | DOC-DATA-001, DOC-SEC-003, DOC-SEC-001 |
| DEV-0103 | SAML login returns an error page | Single sign-on works for our engineering group but the finance group g | DOC-AUTH-003, DOC-AUTH-001, DOC-ACCT-001 | DOC-AUTH-003, DOC-AUTH-001, DOC-API-003 |
| DEV-0105 | Duplicate webhook deliveries | Our webhook endpoint has stopped receiving events since last Friday. T | DOC-API-003, DOC-INT-002, DOC-API-001 | DOC-API-003, DOC-DEPLOY-001, DOC-API-001 |
| DEV-0110 | Question about backup regions | We need our data to remain within the EU for a contract we are signing | DOC-DATA-003, DOC-DATA-002, DOC-ACCT-002 | DOC-DATA-003, DOC-DATA-001, DOC-ACCT-002 |
| DEV-0111 | API key returning 401 | one of our production keys start returning 401 at around two days ago  | DOC-AUTH-004, DOC-SEC-001, DOC-INT-001 | DOC-AUTH-004, DOC-INT-001, DOC-SEC-001 |
| DEV-0115 | No connections available error | We are getting errors saying no connection is available. This started  | DOC-PERF-003, DOC-DEPLOY-001, DOC-ONB-002 | DOC-PERF-003, DOC-DEPLOY-001, DOC-DEPLOY-002 |
| DEV-0116 | Config differs between environments | i am having set environment variable but the application not able to s | DOC-DEPLOY-004, DOC-ACCT-002, DOC-DEPLOY-001 | DOC-DEPLOY-004, DOC-SEC-002, DOC-ONB-001 |
| DEV-0121 | Key committed to a public repo | We have found activity in our audit log from an address none of us rec | DOC-SEC-001, DOC-SEC-002, DOC-SEC-003 | DOC-SEC-001, DOC-SEC-003, DOC-SEC-002 |
| DEV-0123 | Question about backup regions | One of our customers has asked for written confirmation of where their | DOC-DATA-003, DOC-DATA-002, DOC-ONB-002 | DOC-DATA-003, DOC-DATA-002, DOC-DATA-001 |
| DEV-0124 | Connecting our CI pipeline | Metrics arriving in our monitoring system lag behind what the console  | DOC-INT-002, DOC-PERF-001, DOC-INT-001 | DOC-INT-002, DOC-PERF-001, DOC-BILL-002 |
| DEV-0129 | Export missing recent records | Our export is missing records that were definitely created before I st | DOC-DATA-001, DOC-SEC-001, DOC-SEC-003 | DOC-DATA-001, DOC-SEC-001, DOC-API-002 |
| DEV-0133 | MFA code keeps getting rejected | I have been trying to sign in for the last about a week and keep getti | DOC-AUTH-002, DOC-AUTH-001, DOC-ACCT-001 | DOC-AUTH-001, DOC-AUTH-002, DOC-SEC-001 |
| DEV-0137 | Database restore taking hours | We are getting errors saying no connection is available. This started  | DOC-PERF-003, DOC-DATA-002, DOC-DEPLOY-002 | DOC-PERF-003, DOC-DEPLOY-001, DOC-DEPLOY-002 |
| DEV-0138 | Unexpected overage charges | Our spend cap stopped a production workload overnight. We need it rais | DOC-BILL-003, DOC-BILL-001, DOC-API-001 | DOC-BILL-003, DOC-API-001, DOC-BILL-001 |
| DEV-0140 | User cannot access a project | my team member not able to open project. i give permission already two | DOC-ACCT-001, DOC-ACCT-002, DOC-SEC-001 | DOC-ACCT-001, DOC-SEC-001, DOC-ACCT-002 |
| DEV-0144 | SSO works for some users only | we are setting up SAML with our identity provider and users being boun | DOC-AUTH-003, DOC-SEC-001, DOC-AUTH-002 | DOC-AUTH-003, DOC-AUTH-002, DOC-SEC-001 |
| DEV-0146 | Retention period question | Our auditor has asked for access records covering the last six months. | DOC-SEC-003, DOC-DATA-001, DOC-BILL-001 | DOC-DATA-001, DOC-SEC-003, DOC-SEC-001 |
| DEV-0150 | Please add per-project spend caps | we want to configure our own retention period rather than taking plan  | DOC-BILL-003, DOC-SEC-003, DOC-ACCT-002 | DOC-SEC-003, DOC-BILL-003, DOC-DATA-002 |
| DEV-0153 | How do I revert to the previous revision | We shipped a release late last night that has broken checkout for a po | DOC-DEPLOY-002, DOC-DEPLOY-003, DOC-DATA-002 | DOC-DEPLOY-002, DOC-API-003, DOC-DATA-002 |
| DEV-0155 | Help configuring single sign-on | Single sign-on works for our engineering group but the finance group g | DOC-AUTH-003, DOC-AUTH-002, DOC-AUTH-001 | DOC-AUTH-003, DOC-AUTH-001, DOC-API-003 |
| DEV-0160 | Remove a departing team member | A team member left around 14:00 yesterday and I want to make sure thei | DOC-ACCT-001, DOC-SEC-001, DOC-AUTH-004 | DOC-ACCT-001, DOC-AUTH-004, DOC-SEC-001 |
| DEV-0161 | Remove a departing team member | my team member not able to open project. i give permission already two | DOC-ACCT-001, DOC-SEC-001, DOC-AUTH-001 | DOC-ACCT-001, DOC-SEC-001, DOC-ACCT-002 |
| DEV-0164 | Key committed to a public repo | We have found activity in our audit log from an address none of us rec | DOC-SEC-001, DOC-SEC-002, DOC-SEC-003 | DOC-SEC-001, DOC-SEC-003, DOC-SEC-002 |
| DEV-0165 | Need audit logs for an auditor | We need to demonstrate that read access to customer records is logged. | DOC-SEC-003, DOC-SEC-001, DOC-DATA-001 | DOC-SEC-003, DOC-DATA-001, DOC-SEC-001 |
| DEV-0166 | How do I page through large results | What is the right way to pull a very large extract? Requesting a big p | DOC-API-002, DOC-DATA-001, DOC-PERF-003 | DOC-API-002, DOC-DATA-001, DOC-DEPLOY-002 |
| DEV-0167 | Pagination returns duplicates | Our cursor seems to stop working partway through a long iteration. Is  | DOC-API-002, DOC-PERF-003, DOC-INT-001 | DOC-API-002, DOC-INT-001, DOC-API-001 |
| DEV-0169 | Connection pool exhausted | restore is running from long time. database is 400 gb. is it normal? | DOC-PERF-003, DOC-DATA-002, DOC-PERF-001 | DOC-DATA-002, DOC-PERF-003, DOC-DEPLOY-002 |
| DEV-0171 | Health check keeps timing out | Every deployment fails at the health check stage. I have increased the | DOC-DEPLOY-001, DOC-PERF-001, DOC-ONB-001 | DOC-DEPLOY-001, DOC-ONB-001, DOC-INT-001 |
| DEV-0172 | Unexpected overage charges | Our spend cap stopped a production workload overnight. We need it rais | DOC-BILL-003, DOC-BILL-001, DOC-API-001 | DOC-BILL-003, DOC-API-001, DOC-BILL-001 |
| DEV-0174 | Getting started with first deployment | we are having just signed up and i not sure where to start. we having  | DOC-ONB-001, DOC-DEPLOY-001, DOC-AUTH-003 | DOC-ONB-002, DOC-DEPLOY-001, DOC-ONB-001 |
| DEV-0175 | Please add per-project spend caps | Are staged rollouts on the roadmap? We would like to move traffic grad | DOC-BILL-003, DOC-ACCT-002, DOC-ONB-002 |  |
| DEV-0177 | How do I page through large results | What is the right way to pull a very large extract? Requesting a big p | DOC-API-002, DOC-DATA-001, DOC-PERF-003 | DOC-API-002, DOC-DATA-001, DOC-DEPLOY-002 |
| DEV-0178 | Response times have doubled | latency has been climbing gradually over past couple of days. Nothing  | DOC-PERF-001, DOC-PERF-002, DOC-API-002 | DOC-PERF-001, DOC-AUTH-002, DOC-PERF-002 |
| DEV-0181 | Key stopped working overnight | One of our engineers pushed a key to a public repository by mistake. W | DOC-AUTH-004, DOC-SEC-001, DOC-SEC-002 | DOC-SEC-001, DOC-AUTH-004, DOC-INT-001 |
| DEV-0182 | How do I page through large results | Our cursor seems to stop working partway through a long iteration. Is  | DOC-API-002, DOC-API-001, DOC-PERF-003 | DOC-API-002, DOC-INT-001, DOC-API-001 |
| DEV-0186 | p95 latency is very high | Latency has been climbing gradually over the past most of the morning. | DOC-PERF-001, DOC-API-001, DOC-AUTH-002 | DOC-PERF-001, DOC-AUTH-002, DOC-API-001 |
| DEV-0187 | Evidence for a compliance review | our auditor has asked for access records covering last six months. Can | DOC-SEC-003, DOC-DATA-001, DOC-DATA-003 | DOC-DATA-001, DOC-SEC-003, DOC-SEC-001 |
| DEV-0188 | Where is our data stored | Are backups replicated outside our primary region? A compliance review | DOC-DATA-003, DOC-DATA-002, DOC-ONB-002 | DOC-DATA-003, DOC-DATA-002, DOC-SEC-003 |
| DEV-0190 | SSO works for some users only | Single sign-on works for our engineering group but the finance group g | DOC-AUTH-003, DOC-SEC-001, DOC-ACCT-001 | DOC-AUTH-003, DOC-AUTH-001, DOC-API-003 |
| DEV-0193 | Please add per-project spend caps | Are staged rollouts on the roadmap? We would like to move traffic grad | DOC-BILL-003, DOC-ACCT-002, DOC-ONB-002 |  |
| DEV-0194 | Connecting our CI pipeline | Log forwarding to our external system stopped last Friday and has not  | DOC-INT-002, DOC-INT-001, DOC-DEPLOY-002 | DOC-INT-002, DOC-DEPLOY-002, DOC-SEC-003 |
| DEV-0199 | Question about this month's charges | Our invoice this month is considerably higher than usual and I cannot  | DOC-BILL-001, DOC-BILL-003, DOC-BILL-002 | DOC-BILL-001, DOC-BILL-002, DOC-API-001 |
| DEV-0200 | Invoice higher than expected | Our billing period does not seem to match the calendar month, which is | DOC-BILL-001, DOC-BILL-002, DOC-INT-002 | DOC-BILL-001, DOC-ACCT-002, DOC-BILL-002 |
| DEV-0201 | Pagination returns duplicates | What is the right way to pull a very large extract? Requesting a big p | DOC-API-002, DOC-DATA-001, DOC-PERF-003 | DOC-API-002, DOC-DATA-001, DOC-DEPLOY-002 |
| DEV-0202 | Feature request: staged rollouts | We would like to configure our own retention period rather than taking | DOC-SEC-003, DOC-DATA-001, DOC-BILL-003 | DOC-SEC-003, DOC-BILL-003, DOC-DATA-002 |
| DEV-0203 | Usage allowance already consumed | Our spend cap stopped a production workload overnight. We need it rais | DOC-BILL-003, DOC-BILL-001, DOC-API-001 | DOC-BILL-003, DOC-API-001, DOC-BILL-001 |
| DEV-0207 | Question about the export endpoint | Our cursor seems to stop working partway through a long iteration. Is  | DOC-API-002, DOC-API-001, DOC-DATA-001 | DOC-API-002, DOC-INT-001, DOC-API-001 |
| DEV-0209 | No connections available error | restore is running from long time. database is 400 gb. is it normal? | DOC-PERF-003, DOC-DATA-002, DOC-ONB-002 | DOC-DATA-002, DOC-PERF-003, DOC-DEPLOY-002 |
| DEV-0210 | Possible account compromise | A former employee appears to still have access three weeks after leavi | DOC-SEC-001, DOC-ACCT-001, DOC-AUTH-001 | DOC-SEC-001, DOC-AUTH-004, DOC-AUTH-001 |
| DEV-0211 | Key committed to a public repo | we are having found activity in our audit log from address none of us  | DOC-SEC-001, DOC-SEC-002, DOC-SEC-003 | DOC-SEC-001, DOC-SEC-003, DOC-DATA-001 |
| DEV-0212 | Remove a departing team member | A team member left earlier today and I want to make sure their access  | DOC-ACCT-001, DOC-SEC-001, DOC-AUTH-004 | DOC-ACCT-001, DOC-AUTH-004, DOC-SEC-001 |
| DEV-0213 | Response times have doubled | The service is noticeably slow during our afternoon peak and fine the  | DOC-PERF-001, DOC-PERF-002, DOC-INT-002 | DOC-PERF-001, DOC-PERF-002, DOC-BILL-001 |
| DEV-0216 | Question about the export endpoint | Our cursor seems to stop working partway through a long iteration. Is  | DOC-API-002, DOC-API-001, DOC-DATA-001 | DOC-API-002, DOC-INT-001, DOC-API-001 |
| DEV-0217 | How do I page through large results | Our cursor seems to stop working partway through a long iteration. Is  | DOC-API-002, DOC-API-001, DOC-PERF-003 | DOC-API-002, DOC-INT-001, DOC-API-001 |
| DEV-0219 | Connecting our CI pipeline | Log forwarding to our external system stopped late last night and has  | DOC-INT-002, DOC-INT-001, DOC-DEPLOY-002 | DOC-INT-002, DOC-DEPLOY-002, DOC-SEC-003 |
| DEV-0221 | Hitting the rate limit unexpectedly | too many request error. we have 3 key so limit should be more no? plea | DOC-API-001, DOC-PERF-003, DOC-AUTH-004 | DOC-API-001, DOC-AUTH-004, DOC-PERF-003 |
| DEV-0223 | Connecting our CI pipeline | Metrics arriving in our monitoring system lag behind what the console  | DOC-INT-002, DOC-PERF-001, DOC-INT-001 | DOC-INT-002, DOC-PERF-001, DOC-BILL-002 |
| DEV-0224 | Build fails in the pipeline | Every deployment fails at the health check stage. I have increased the | DOC-DEPLOY-001, DOC-DEPLOY-003, DOC-ONB-001 | DOC-DEPLOY-001, DOC-ONB-001, DOC-INT-001 |
| DEV-0225 | Service slow at peak hours | Our response times have roughly doubled since last Friday with no depl | DOC-PERF-001, DOC-DEPLOY-002, DOC-INT-002 | DOC-PERF-001, DOC-INT-002, DOC-DEPLOY-002 |
| DEV-0226 | New to the platform, where to begin | Could you point me at the right starting place? I have created an acco | DOC-ONB-001 | DOC-AUTH-001, DOC-AUTH-003, DOC-ACCT-001 |
| DEV-0227 | Environment variable not being read | Where should secrets be stored so they do not appear in the logs? At t | DOC-DEPLOY-004, DOC-SEC-002, DOC-DEPLOY-001 | DOC-DEPLOY-004, DOC-SEC-002, DOC-DATA-003 |
| DEV-0228 | Invoice higher than expected | invoice showing service we not use. can you check and tell? | DOC-BILL-001, DOC-BILL-002, DOC-INT-002 | DOC-BILL-001, DOC-BILL-002, DOC-INT-001 |
| DEV-0229 | Duplicate webhook deliveries | We are receiving the same event several times. Is this expected behavi | DOC-API-003, DOC-SEC-003, DOC-BILL-001 | DOC-API-003, DOC-SEC-003, DOC-PERF-001 |
| DEV-0230 | Invalid credentials error | Since yesterday morning I cannot get into the console at all. My colle | DOC-AUTH-001, DOC-SEC-001, DOC-INT-002 | DOC-AUTH-001, DOC-AUTH-002, DOC-SEC-001 |
| DEV-0231 | Retention period question | Our auditor has asked for access records covering the last six months. | DOC-SEC-003, DOC-DATA-001, DOC-BILL-001 | DOC-DATA-001, DOC-SEC-003, DOC-SEC-001 |
| DEV-0232 | Duplicate webhook deliveries | we are receiving same event several times. Is this expect behaviour or | DOC-API-003, DOC-INT-002, DOC-SEC-003 | DOC-SEC-003, DOC-API-003, DOC-INT-002 |
| DEV-0233 | Migrating our app across | We are planning to migrate an existing application across. It currentl | DOC-ONB-002, DOC-DATA-003, DOC-ONB-001 | DOC-ONB-002, DOC-ONB-001, DOC-ACCT-002 |
| DEV-0236 | Health check keeps timing out | Builds that worked last week are now failing during dependency resolut | DOC-DEPLOY-001, DOC-DEPLOY-003, DOC-PERF-001 | DOC-DEPLOY-003, DOC-DEPLOY-002, DOC-PERF-001 |
| DEV-0237 | Please add per-project spend caps | We would like to configure our own retention period rather than taking | DOC-BILL-003, DOC-SEC-003, DOC-ACCT-002 | DOC-SEC-003, DOC-BILL-003, DOC-DATA-002 |
| DEV-0239 | Spend cap stopped our service | We were throttled yesterday morning after a traffic increase and it to | DOC-BILL-003, DOC-BILL-002, DOC-API-001 | DOC-BILL-003, DOC-BILL-002, DOC-INT-002 |
| DEV-0240 | Suspicious activity in audit log | One of our engineers believes their credentials may have been exposed  | DOC-SEC-001, DOC-SEC-002, DOC-SEC-003 | DOC-SEC-001, DOC-SEC-002, DOC-INT-002 |
| DEV-0241 | Response times have doubled | Latency has been climbing gradually over the past most of the morning. | DOC-PERF-001, DOC-API-001, DOC-PERF-002 | DOC-PERF-001, DOC-AUTH-002, DOC-API-001 |
| DEV-0247 | Question about this month's charges | Our billing period does not seem to match the calendar month, which is | DOC-BILL-001, DOC-BILL-002, DOC-ACCT-002 | DOC-BILL-001, DOC-ACCT-002, DOC-BILL-002 |
| DEV-0249 | Problem with the service | Following up on my previous message. Any update? | DOC-INT-001, DOC-DEPLOY-002, DOC-PERF-001 |  |
| DEV-0250 | Key stopped working overnight | A key can read fine but every write returns a permission error. I crea | DOC-AUTH-004, DOC-SEC-001, DOC-SEC-002 | DOC-AUTH-004, DOC-SEC-001, DOC-AUTH-001 |
| DEV-0251 | Getting started with first deployment | Could you point me at the right starting place? I have created an acco | DOC-ONB-001, DOC-AUTH-003, DOC-AUTH-001 | DOC-AUTH-001, DOC-AUTH-003, DOC-ACCT-001 |
| DEV-0252 | Hitting the rate limit unexpectedly | too many request error. we have 3 key so limit should be more no? plea | DOC-API-001, DOC-PERF-003, DOC-AUTH-004 | DOC-API-001, DOC-AUTH-004, DOC-PERF-003 |
| DEV-0254 | Possible account compromise | A former employee appears to still have access three weeks after leavi | DOC-SEC-001, DOC-ACCT-001, DOC-AUTH-001 | DOC-SEC-001, DOC-AUTH-004, DOC-AUTH-001 |
| DEV-0258 | Throughput drops after a few minutes | too many request error. we have 3 key so limit should be more no? plea | DOC-API-001, DOC-PERF-002, DOC-INT-002 | DOC-API-001, DOC-AUTH-004, DOC-PERF-003 |
| DEV-0260 | Need audit logs for an auditor | Our policy requires two years of retention. What are our options given | DOC-SEC-003, DOC-SEC-001, DOC-DATA-002 | DOC-SEC-003, DOC-DATA-002, DOC-ONB-001 |
| DEV-0261 | Webhooks not arriving | We are receiving the same event several times. Is this expected behavi | DOC-API-003, DOC-INT-002, DOC-SEC-003 | DOC-API-003, DOC-SEC-003, DOC-PERF-001 |
| DEV-0264 | Pagination returns duplicates | Our cursor seems to stop working partway through a long iteration. Is  | DOC-API-002, DOC-PERF-003, DOC-INT-001 | DOC-API-002, DOC-INT-001, DOC-API-001 |
| DEV-0265 | Evidence for a compliance review | Our auditor has asked for access records covering the last six months. | DOC-SEC-003, DOC-DATA-001, DOC-DATA-003 | DOC-DATA-001, DOC-SEC-003, DOC-SEC-001 |
| DEV-0266 | Permission changes not taking effect | One of our developers cannot see a project she should have access to.  | DOC-ACCT-001, DOC-ACCT-002, DOC-SEC-003 | DOC-ACCT-001, DOC-ACCT-002, DOC-AUTH-003 |
| DEV-0270 | Getting started with first deployment | We have just signed up and I am not sure where to start. We have a con | DOC-ONB-001, DOC-DEPLOY-001, DOC-AUTH-003 | DOC-DEPLOY-001, DOC-ONB-002, DOC-ONB-001 |
| DEV-0274 | Service slow at peak hours | Latency has been climbing gradually over the past most of the morning. | DOC-PERF-001, DOC-BILL-003, DOC-API-001 | DOC-PERF-001, DOC-AUTH-002, DOC-API-001 |
| DEV-0280 | Build fails in the pipeline | Our deployment reaches running and then rolls back after about a minut | DOC-DEPLOY-003, DOC-DEPLOY-001, DOC-ONB-001 | DOC-DEPLOY-001, DOC-ONB-001, DOC-DEPLOY-002 |
| DEV-0282 | Possible account compromise | one of our engineers believes their credentials may have been exposed  | DOC-SEC-001, DOC-SEC-002, DOC-INT-001 | DOC-SEC-001, DOC-SEC-002, DOC-INT-002 |
| DEV-0284 | Question about this month's charges | there charges on our invoice for a service i am not believe we use. Ca | DOC-BILL-001, DOC-BILL-003, DOC-BILL-002 | DOC-BILL-001, DOC-BILL-002, DOC-BILL-003 |
| DEV-0290 | p95 latency is very high | Our response times have roughly doubled since yesterday morning with n | DOC-PERF-001, DOC-DATA-003, DOC-INT-002 | DOC-PERF-001, DOC-ONB-001, DOC-INT-002 |
| DEV-0291 | Webhooks not arriving | We are receiving the same event several times. Is this expected behavi | DOC-API-003, DOC-INT-002, DOC-SEC-003 | DOC-API-003, DOC-SEC-003, DOC-PERF-001 |
| DEV-0293 | Please add per-project spend caps | Are staged rollouts on the roadmap? We would like to move traffic grad | DOC-BILL-003, DOC-ACCT-002, DOC-ONB-002 |  |
| DEV-0294 | Getting started with first deployment | We have just signed up and I am not sure where to start. We have a con | DOC-ONB-001, DOC-DEPLOY-001, DOC-AUTH-003 | DOC-DEPLOY-001, DOC-ONB-002, DOC-ONB-001 |
| DEV-0295 | Migrating our app across | can you please point me at the right starting place? i am having creat | DOC-DATA-003, DOC-AUTH-001, DOC-ONB-002 | DOC-AUTH-001, DOC-AUTH-003, DOC-ONB-001 |
| DEV-0296 | New to the platform, where to begin | can you please point me at right starting place? i am having created a | DOC-ONB-001 | DOC-AUTH-001, DOC-AUTH-003, DOC-ONB-001 |
| DEV-0300 | Key committed to a public repo | one of our engineers believes their credentials may have been exposed  | DOC-SEC-001, DOC-SEC-002, DOC-AUTH-004 | DOC-SEC-001, DOC-SEC-002, DOC-INT-002 |
| DEV-0304 | Bad release in production | We shipped a release two days ago that has broken checkout for a porti | DOC-DEPLOY-002, DOC-DEPLOY-003, DOC-API-003 | DOC-DEPLOY-002, DOC-API-003, DOC-DATA-002 |
| DEV-0305 | Help configuring single sign-on | Single sign-on works for our engineering group but the finance group g | DOC-AUTH-003, DOC-AUTH-002, DOC-AUTH-001 | DOC-AUTH-003, DOC-AUTH-001, DOC-API-003 |
| DEV-0306 | Signature verification failing | Our webhook endpoint has stopped receiving events since two days ago.  | DOC-API-003, DOC-AUTH-004, DOC-DEPLOY-001 | DOC-API-003, DOC-DEPLOY-001, DOC-API-001 |
| DEV-0307 | Duplicate webhook deliveries | Our webhook endpoint has stopped receiving events since last Friday. T | DOC-API-003, DOC-INT-002, DOC-API-001 | DOC-API-003, DOC-DEPLOY-001, DOC-API-001 |
| DEV-0310 | Migrating our app across | Could you point me at the right starting place? I have created an acco | DOC-AUTH-001, DOC-DATA-003, DOC-ONB-002 | DOC-AUTH-001, DOC-AUTH-003, DOC-ACCT-001 |
| DEV-0312 | Login fails after password change | My authenticator app codes are being rejected every time. I have tried | DOC-AUTH-002, DOC-AUTH-001, DOC-AUTH-003 | DOC-AUTH-002, DOC-AUTH-003, DOC-API-003 |
| DEV-0314 | Key stopped working overnight | One of our engineers pushed a key to a public repository by mistake. W | DOC-AUTH-004, DOC-SEC-001, DOC-SEC-002 | DOC-SEC-001, DOC-AUTH-004, DOC-INT-001 |
| DEV-0316 | Usage allowance already consumed | We were throttled around 14:00 yesterday after a traffic increase and  | DOC-BILL-003, DOC-BILL-001, DOC-BILL-002 | DOC-BILL-003, DOC-BILL-002, DOC-INT-002 |
| DEV-0320 | How do I page through large results | Our cursor seems to stop working partway through a long iteration. Is  | DOC-API-002, DOC-API-001, DOC-PERF-003 | DOC-API-002, DOC-INT-001, DOC-API-001 |
| DEV-0321 | Help configuring single sign-on | We are setting up SAML with our identity provider and users are being  | DOC-AUTH-003, DOC-AUTH-002, DOC-SEC-001 | DOC-AUTH-003, DOC-SEC-001, DOC-AUTH-002 |
| DEV-0325 | Connecting our CI pipeline | Metrics arriving in our monitoring system lag behind what the console  | DOC-INT-002, DOC-PERF-001, DOC-INT-001 | DOC-INT-002, DOC-PERF-001, DOC-BILL-002 |
| DEV-0330 | No connections available error | Our connection pool appears to be exhausting under moderate load. We h | DOC-PERF-003, DOC-AUTH-003, DOC-DEPLOY-001 | DOC-PERF-003, DOC-PERF-001, DOC-PERF-002 |
| DEV-0334 | Need to rotate an exposed key | one of our engineers pushed a key to a public repository by mistake. W | DOC-AUTH-004, DOC-SEC-002, DOC-SEC-001 | DOC-SEC-001, DOC-INT-001, DOC-AUTH-004 |
| DEV-0335 | Login fails after password change | My authenticator app codes are being rejected every time. I have tried | DOC-AUTH-002, DOC-AUTH-001, DOC-AUTH-003 | DOC-AUTH-002, DOC-AUTH-003, DOC-API-003 |
| DEV-0336 | Service slow at peak hours | latency has been climbing gradually over past several hours. Nothing i | DOC-PERF-001, DOC-PERF-002, DOC-DEPLOY-002 | DOC-PERF-001, DOC-AUTH-002, DOC-PERF-002 |
| DEV-0337 | No connections available error | We are getting errors saying no connection is available. This started  | DOC-PERF-003, DOC-DEPLOY-001, DOC-ONB-002 | DOC-PERF-003, DOC-DEPLOY-001, DOC-DEPLOY-002 |
| DEV-0340 | Export missing recent records | Our export is missing records that were definitely created before I st | DOC-DATA-001, DOC-SEC-001, DOC-SEC-003 | DOC-DATA-001, DOC-SEC-001, DOC-API-002 |
| DEV-0341 | Connecting our CI pipeline | log forwarding to our external system stop late last night and not res | DOC-INT-002, DOC-INT-001, DOC-SEC-002 | DOC-INT-002, DOC-DEPLOY-002, DOC-SEC-003 |
| DEV-0342 | Bad release in production | how do I revert to earlier revision? The release we put out this morni | DOC-DEPLOY-002, DOC-DEPLOY-001, DOC-AUTH-001 | DOC-DEPLOY-002, DOC-DEPLOY-001, DOC-DEPLOY-003 |
| DEV-0343 | Download link expired | I started an export late last night and it is still showing as queued. | DOC-DATA-001, DOC-API-002, DOC-INT-002 | DOC-DATA-001, DOC-INT-002, DOC-API-002 |
| DEV-0344 | Please add per-project spend caps | we want to configure our own retention period rather than taking plan  | DOC-BILL-003, DOC-SEC-003, DOC-ACCT-002 | DOC-SEC-003, DOC-BILL-003, DOC-DATA-002 |
| DEV-0348 | Need audit logs for an auditor | Our policy requires two years of retention. What are our options given | DOC-SEC-003, DOC-SEC-001, DOC-DATA-002 | DOC-SEC-003, DOC-DATA-002, DOC-ONB-001 |
| DEV-0350 | Deployment rolls back every time | Builds that worked last week are now failing during dependency resolut | DOC-DEPLOY-003, DOC-DEPLOY-002, DOC-DEPLOY-001 | DOC-DEPLOY-003, DOC-DEPLOY-002, DOC-SEC-002 |
| DEV-0351 | Need audit logs for an auditor | Our auditor has asked for access records covering the last six months. | DOC-SEC-003, DOC-SEC-001, DOC-DATA-001 | DOC-DATA-001, DOC-SEC-003, DOC-SEC-001 |
| DEV-0352 | User cannot access a project | One of our developers cannot see a project she should have access to.  | DOC-ACCT-001, DOC-ACCT-002, DOC-AUTH-004 | DOC-ACCT-001, DOC-ACCT-002, DOC-AUTH-003 |
| DEV-0353 | Build fails in the pipeline | Our deployment reaches running and then rolls back after about a minut | DOC-DEPLOY-003, DOC-DEPLOY-001, DOC-ONB-001 | DOC-DEPLOY-001, DOC-ONB-001, DOC-DEPLOY-002 |
| DEV-0354 | No connections available error | We are getting errors saying no connection is available. This started  | DOC-PERF-003, DOC-DEPLOY-001, DOC-ONB-002 | DOC-PERF-003, DOC-DEPLOY-001, DOC-DEPLOY-002 |
| DEV-0358 | New to the platform, where to begin | we are planning to migrate an existing application across. It currentl | DOC-ONB-002, DOC-ONB-001, DOC-DATA-002 | DOC-ONB-002, DOC-DATA-002, DOC-ONB-001 |
| DEV-0362 | Webhooks not arriving | Our webhook endpoint has stopped receiving events since on Monday. The | DOC-API-003, DOC-DEPLOY-001, DOC-INT-002 | DOC-API-003, DOC-DEPLOY-001, DOC-API-001 |
| DEV-0366 | Unexpected overage charges | We were throttled over the weekend after a traffic increase and it too | DOC-BILL-003, DOC-BILL-001, DOC-BILL-002 | DOC-BILL-003, DOC-BILL-002, DOC-INT-002 |
| DEV-0368 | Pagination returns duplicates | Our cursor seems to stop working partway through a long iteration. Is  | DOC-API-002, DOC-PERF-003, DOC-INT-001 | DOC-API-002, DOC-INT-001, DOC-API-001 |
| DEV-0370 | Possible account compromise | A former employee appears to still have access three weeks after leavi | DOC-SEC-001, DOC-ACCT-001, DOC-AUTH-001 | DOC-SEC-001, DOC-AUTH-004, DOC-AUTH-001 |
| DEV-0374 | Database restore taking hours | we get errors saying no connection is available. This start when we sc | DOC-DATA-002, DOC-PERF-003, DOC-DEPLOY-002 | DOC-PERF-003, DOC-AUTH-003, DOC-INT-001 |
| DEV-0376 | User cannot access a project | user left company. how i remove all his access including key he made? | DOC-ACCT-001, DOC-AUTH-004, DOC-SEC-001 | DOC-AUTH-004, DOC-ACCT-001, DOC-SEC-001 |
| DEV-0377 | Question about the export endpoint | What is the right way to pull a very large extract? Requesting a big p | DOC-API-002, DOC-DATA-001, DOC-API-001 | DOC-API-002, DOC-DATA-001, DOC-DEPLOY-002 |
| DEV-0378 | Database restore taking hours | connection not available error coming. we scale up service then proble | DOC-DATA-002, DOC-PERF-003, DOC-DEPLOY-001 | DOC-PERF-003, DOC-PERF-002, DOC-AUTH-003 |
| DEV-0381 | Please add per-project spend caps | Are staged rollouts on the roadmap? We would like to move traffic grad | DOC-BILL-003, DOC-ACCT-002, DOC-ONB-002 |  |
| DEV-0382 | Spend cap stopped our service | Our spend cap stopped a production workload overnight. We need it rais | DOC-BILL-003, DOC-BILL-001, DOC-BILL-002 | DOC-BILL-003, DOC-API-001, DOC-BILL-001 |
| DEV-0384 | How do I page through large results | Our cursor seems to stop working partway through a long iteration. Is  | DOC-API-002, DOC-API-001, DOC-PERF-003 | DOC-API-002, DOC-INT-001, DOC-API-001 |
| DEV-0385 | Usage allowance already consumed | We were throttled on Monday after a traffic increase and it took down  | DOC-BILL-003, DOC-BILL-001, DOC-BILL-002 | DOC-BILL-003, DOC-BILL-002, DOC-INT-002 |
| DEV-0388 | Need data to stay in the EU | Are backups replicated outside our primary region? A compliance review | DOC-DATA-003, DOC-DATA-002, DOC-ONB-002 | DOC-DATA-003, DOC-DATA-002, DOC-SEC-003 |
| DEV-0390 | User cannot access a project | One of our developers cannot see a project she should have access to.  | DOC-ACCT-001, DOC-ACCT-002, DOC-AUTH-004 | DOC-ACCT-001, DOC-ACCT-002, DOC-AUTH-003 |
| DEV-0391 | Suspicious activity in audit log | One of our engineers believes their credentials may have been exposed  | DOC-SEC-001, DOC-SEC-002, DOC-SEC-003 | DOC-SEC-001, DOC-SEC-002, DOC-INT-002 |
| DEV-0394 | Throughput drops after a few minutes | We started getting 429 responses at around around 14:00 yesterday. Our | DOC-API-001, DOC-PERF-001, DOC-INT-002 | DOC-API-001, DOC-PERF-001, DOC-PERF-003 |
| DEV-0401 | Export job stuck | I started an export last Friday and it is still showing as queued. It  | DOC-DATA-001, DOC-API-002, DOC-SEC-001 | DOC-DATA-001, DOC-INT-002, DOC-API-002 |
| DEV-0402 | Feature request: staged rollouts | We would like to configure our own retention period rather than taking | DOC-SEC-003, DOC-DATA-001, DOC-BILL-003 | DOC-SEC-003, DOC-BILL-003, DOC-DATA-002 |
| DEV-0403 | SSO works for some users only | Single sign-on works for our engineering group but the finance group g | DOC-AUTH-003, DOC-SEC-001, DOC-ACCT-001 | DOC-AUTH-003, DOC-AUTH-001, DOC-API-003 |
| DEV-0405 | Getting started with first deployment | we are having just signed up and i not sure where to start. we are hav | DOC-ONB-001, DOC-DEPLOY-001, DOC-AUTH-003 | DOC-ONB-002, DOC-DEPLOY-001, DOC-ONB-001 |
| DEV-0406 | Webhooks not arriving | We are receiving the same event several times. Is this expected behavi | DOC-API-003, DOC-INT-002, DOC-SEC-003 | DOC-API-003, DOC-SEC-003, DOC-PERF-001 |
| DEV-0409 | Cannot log in to the console | My authenticator app codes are being rejected every time. I have tried | DOC-AUTH-002, DOC-AUTH-001, DOC-AUTH-003 | DOC-AUTH-002, DOC-AUTH-003, DOC-API-003 |
| DEV-0410 | Config differs between environments | Our staging environment is picking up production configuration values. | DOC-DEPLOY-004, DOC-SEC-002, DOC-ACCT-002 | DOC-DEPLOY-004, DOC-SEC-002, DOC-DEPLOY-001 |
| DEV-0413 | Problem with the service | it not working. Please help. sorry for my english. | DOC-INT-001, DOC-ONB-001, DOC-PERF-001 |  |
| DEV-0414 | Spend cap stopped our service | Our spend cap stopped a production workload overnight. We need it rais | DOC-BILL-003, DOC-BILL-001, DOC-BILL-002 | DOC-BILL-003, DOC-API-001, DOC-BILL-001 |
| DEV-0415 | Question about this month's charges | There are charges on our invoice for a service I do not believe we use | DOC-BILL-001, DOC-BILL-003, DOC-BILL-002 | DOC-BILL-001, DOC-BILL-002, DOC-BILL-003 |
| DEV-0416 | Build fails in the pipeline | Builds that worked last week are now failing during dependency resolut | DOC-DEPLOY-003, DOC-ONB-001, DOC-INT-001 | DOC-DEPLOY-003, DOC-DEPLOY-002, DOC-PERF-001 |
| DEV-0417 | Help configuring single sign-on | Single sign-on works for our engineering group but the finance group g | DOC-AUTH-003, DOC-AUTH-002, DOC-AUTH-001 | DOC-AUTH-003, DOC-AUTH-001, DOC-API-003 |
| DEV-0419 | SAML login returns an error page | single sign-on works for our engineering group but finance group gets  | DOC-AUTH-003, DOC-AUTH-001, DOC-ACCT-001 | DOC-AUTH-003, DOC-ACCT-001, DOC-AUTH-002 |
| DEV-0422 | Question about the export endpoint | Our cursor seems to stop working partway through a long iteration. Is  | DOC-API-002, DOC-API-001, DOC-DATA-001 | DOC-API-002, DOC-INT-001, DOC-API-001 |
| DEV-0428 | New to the platform, where to begin | we are planning to migrate existing application across. It currently w | DOC-ONB-002, DOC-ONB-001, DOC-DATA-002 | DOC-ONB-002, DOC-DATA-002, DOC-ONB-001 |
| DEV-0429 | Export missing recent records | Our export is missing records that were definitely created before I st | DOC-DATA-001, DOC-SEC-001, DOC-SEC-003 | DOC-DATA-001, DOC-SEC-001, DOC-API-002 |
| DEV-0430 | Pagination returns duplicates | What is the right way to pull a very large extract? Requesting a big p | DOC-API-002, DOC-DATA-001, DOC-PERF-003 | DOC-API-002, DOC-DATA-001, DOC-DEPLOY-002 |
| DEV-0434 | How do I page through large results | What is the right way to pull a very large extract? Requesting a big p | DOC-API-002, DOC-DATA-001, DOC-PERF-003 | DOC-API-002, DOC-DATA-001, DOC-DEPLOY-002 |
| DEV-0437 | p95 latency is very high | The service is noticeably slow during our afternoon peak and fine the  | DOC-PERF-001, DOC-DATA-003, DOC-PERF-002 | DOC-PERF-001, DOC-PERF-002, DOC-BILL-001 |
| DEV-0438 | SSO works for some users only | New starters are not being created automatically when they log in thro | DOC-AUTH-003, DOC-ONB-001, DOC-SEC-001 | DOC-AUTH-003, DOC-ONB-001, DOC-AUTH-002 |
| DEV-0439 | Database restore taking hours | Our connection pool appears to be exhausting under moderate load. We h | DOC-PERF-003, DOC-DATA-002, DOC-ONB-002 | DOC-PERF-003, DOC-PERF-001, DOC-PERF-002 |
| DEV-0442 | Build fails in the pipeline | Our deployment reaches running and then rolls back after about a minut | DOC-DEPLOY-003, DOC-DEPLOY-001, DOC-ONB-001 | DOC-DEPLOY-001, DOC-ONB-001, DOC-DEPLOY-002 |
| DEV-0443 | New to the platform, where to begin | We have just signed up and I am not sure where to start. We have a con | DOC-ONB-001, DOC-ONB-002, DOC-DEPLOY-001 | DOC-DEPLOY-001, DOC-ONB-002, DOC-ONB-001 |
| DEV-0444 | How do I revert to the previous revision | We shipped a release around 14:00 yesterday that has broken checkout f | DOC-DEPLOY-002, DOC-DEPLOY-003, DOC-DATA-002 | DOC-DEPLOY-002, DOC-DATA-002, DOC-DEPLOY-003 |
| DEV-0448 | Need audit logs for an auditor | Our policy requires two years of retention. What are our options given | DOC-SEC-003, DOC-SEC-001, DOC-DATA-002 | DOC-SEC-003, DOC-DATA-002, DOC-ONB-001 |
| DEV-0449 | Build fails in the pipeline | Our deployment reaches running and then rolls back after about a minut | DOC-DEPLOY-003, DOC-DEPLOY-001, DOC-ONB-001 | DOC-DEPLOY-001, DOC-ONB-001, DOC-DEPLOY-002 |
| DEV-0450 | Help configuring single sign-on | Single sign-on works for our engineering group but the finance group g | DOC-AUTH-003, DOC-AUTH-002, DOC-AUTH-001 | DOC-AUTH-003, DOC-AUTH-001, DOC-API-003 |
| DEV-0451 | Database restore taking hours | restore we start earlier today is still run. database about four hundr | DOC-DATA-002, DOC-PERF-003, DOC-ONB-002 | DOC-DATA-002, DOC-DEPLOY-002, DOC-PERF-003 |
| DEV-0452 | Invoice higher than expected | Our invoice this month is considerably higher than usual and I cannot  | DOC-BILL-001, DOC-BILL-002, DOC-INT-002 | DOC-BILL-001, DOC-BILL-002, DOC-API-001 |
| DEV-0455 | Question about this month's charges | Our invoice this month is considerably higher than usual and I cannot  | DOC-BILL-001, DOC-BILL-003, DOC-BILL-002 | DOC-BILL-001, DOC-BILL-002, DOC-API-001 |
| DEV-0456 | Please add per-project spend caps | we want to configure our own retention period rather than taking the p | DOC-BILL-003, DOC-SEC-003, DOC-ACCT-002 | DOC-SEC-003, DOC-BILL-003, DOC-DATA-001 |
| DEV-0457 | Question about this month's charges | Our invoice this month is considerably higher than usual and I cannot  | DOC-BILL-001, DOC-BILL-003, DOC-BILL-002 | DOC-BILL-001, DOC-BILL-002, DOC-API-001 |
| DEV-0459 | User cannot access a project | One of our developers cannot see a project she should have access to.  | DOC-ACCT-001, DOC-ACCT-002, DOC-AUTH-004 | DOC-ACCT-001, DOC-ACCT-002, DOC-AUTH-003 |
| DEV-0460 | Permission changes not taking effect | A team member left over the weekend and I want to make sure their acce | DOC-ACCT-001, DOC-SEC-001, DOC-AUTH-004 | DOC-ACCT-001, DOC-AUTH-004, DOC-SEC-001 |
| DEV-0461 | How do I revert to the previous revision | We shipped a release yesterday morning that has broken checkout for a  | DOC-DEPLOY-002, DOC-DEPLOY-003, DOC-DATA-002 | DOC-DEPLOY-002, DOC-DATA-002, DOC-DEPLOY-003 |
| DEV-0462 | Getting started with first deployment | Could you point me at the right starting place? I have created an acco | DOC-ONB-001, DOC-AUTH-003, DOC-AUTH-001 | DOC-AUTH-001, DOC-AUTH-003, DOC-ACCT-001 |
| DEV-0465 | Webhooks not arriving | Our webhook endpoint has stopped receiving events since last Friday. T | DOC-API-003, DOC-DEPLOY-001, DOC-INT-002 | DOC-API-003, DOC-DEPLOY-001, DOC-API-001 |
| DEV-0466 | Where is our data stored | We need our data to remain within the EU for a contract we are signing | DOC-DATA-003, DOC-DATA-001, DOC-ONB-002 | DOC-DATA-003, DOC-DATA-001, DOC-ACCT-002 |
| DEV-0469 | Connecting our CI pipeline | log forwarding to our external system stop yesterday morning and not r | DOC-INT-002, DOC-INT-001, DOC-SEC-002 | DOC-INT-002, DOC-DEPLOY-002, DOC-SEC-003 |
| DEV-0470 | Suspicious activity in audit log | One of our engineers believes their credentials may have been exposed  | DOC-SEC-001, DOC-SEC-002, DOC-SEC-003 | DOC-SEC-001, DOC-SEC-002, DOC-INT-002 |
| DEV-0471 | SAML login returns an error page | new starters not being created automatically when they log in through  | DOC-AUTH-003, DOC-ONB-001, DOC-AUTH-001 | DOC-AUTH-003, DOC-ONB-001, DOC-AUTH-002 |
| DEV-0474 | Migrating our app across | can you please point me at right starting place? i am having created a | DOC-DATA-003, DOC-DEPLOY-002, DOC-ONB-002 | DOC-AUTH-001, DOC-AUTH-003, DOC-ONB-001 |
| DEV-0475 | Suspicious activity in audit log | one of our engineers believes their credentials may have been exposed  | DOC-SEC-001, DOC-SEC-002, DOC-SEC-003 | DOC-SEC-001, DOC-SEC-002, DOC-INT-002 |
| DEV-0480 | Build fails in the pipeline | Builds that worked last week are now failing during dependency resolut | DOC-DEPLOY-003, DOC-ONB-001, DOC-INT-001 | DOC-DEPLOY-003, DOC-DEPLOY-002, DOC-PERF-001 |
| DEV-0481 | How do I page through large results | When I page through results I am seeing some records twice and missing | DOC-API-002, DOC-DATA-001, DOC-API-001 | DOC-API-002, DOC-DATA-001, DOC-DATA-003 |
| DEV-0482 | Pagination returns duplicates | Our cursor seems to stop working partway through a long iteration. Is  | DOC-API-002, DOC-PERF-003, DOC-INT-001 | DOC-API-002, DOC-INT-001, DOC-API-001 |
| DEV-0484 | SSO works for some users only | We are setting up SAML with our identity provider and users are being  | DOC-AUTH-003, DOC-SEC-001, DOC-AUTH-004 | DOC-AUTH-003, DOC-SEC-001, DOC-AUTH-002 |
| DEV-0491 | Need to rotate an exposed key | A key can read fine but every write returns a permission error. I crea | DOC-AUTH-004, DOC-SEC-002, DOC-ACCT-001 | DOC-AUTH-004, DOC-SEC-001, DOC-AUTH-001 |
| DEV-0495 | p95 latency is very high | Latency has been climbing gradually over the past most of the morning. | DOC-PERF-001, DOC-API-001, DOC-AUTH-002 | DOC-PERF-001, DOC-AUTH-002, DOC-API-001 |
| DEV-0496 | Getting started with first deployment | We are planning to migrate an existing application across. It currentl | DOC-ONB-002, DOC-ONB-001, DOC-DEPLOY-001 | DOC-ONB-002, DOC-ONB-001, DOC-ACCT-002 |
| DEV-0497 | Locked out of my account | I have been trying to sign in for the last most of the morning and kee | DOC-AUTH-001, DOC-SEC-001, DOC-INT-002 | DOC-AUTH-001, DOC-INT-002, DOC-SEC-001 |
| DEV-0500 | Spend cap stopped our service | our spend cap stop production workload overnight. We need it raised im | DOC-BILL-003, DOC-API-001, DOC-BILL-001 | DOC-BILL-003, DOC-API-001, DOC-BILL-002 |
