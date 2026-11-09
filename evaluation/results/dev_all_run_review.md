# Review: dev_all_run.json

89 guardrail blocks, 73 slip-throughs, 39 should-be-automatic tickets sent to a person.

## 1. Guardrail blocks: right block or false alarm?

### DEV-0011 · authentication_failure · key says escalate

**Ticket:** We changed the password on our shared account over the weekend and now our automated jobs are all failing to authenticate. The console works fine with the new password.

**Blocked by:** {'grounding_model': 'block: the article does not fit the situation; sentences [1] not supported (The article addresses interactive console and CLI login failures, not automated job authentication failures, and the specific command provided is for CLI token refresh, not automated job credential up)'}

**The blocked reply:** Thanks for getting in touch. Run `cloudserve auth logout` followed by `cloudserve auth login` to discard the cached token and authenticate with the new password [1].

**Your verdict:** right block / false alarm

### DEV-0012 · data_export · key says auto_respond

**Ticket:** I started an export late last night and it is still showing as queued. It covers about two million records. Should I cancel and try again?

**Blocked by:** {'grounding_words': 'block: sentences 3 (29% of its words in the article)'}

**The blocked reply:** Thanks for getting in touch. Check the exports page to see the current job status [1]. Large exports covering more than a million records commonly take several minutes to complete [1]. If the export remains queued for an extended period, you can cancel it and start a new job, but it is usually not necessary to cancel unless it has stalled [1]. Once the job completes, request a fresh download link from the exports page if the original link has expired [1].

**Your verdict:** right block / false alarm

### DEV-0018 · api_usage_question · key says auto_respond

**Ticket:** Pagination returns duplicates how to get all data? page size big is reject. small is very slow.

**Blocked by:** {'grounding_words': 'block: sentences 3 (a number not in the article)'}

**The blocked reply:** Thanks for getting in touch. Use cursor pagination instead of offset pagination to avoid duplicates when the collection changes while iterating [1]. Pass the next_cursor value from each response as the cursor parameter of the following request, and stop when it is null [1]. Keep the page size at or below two hundred; larger requests are rejected rather than truncated [1]. For very large extracts, use the export endpoint, which runs asynchronously and returns a download link [1].

**Your verdict:** right block / false alarm

### DEV-0019 · account_access · key says auto_respond

**Ticket:** Remove a departing team member A team member left earlier today and I want to make sure their access is fully removed, including anything they may have created.

**Blocked by:** {'grounding_model': 'block: sentences [3] not supported (The article states pending invitations expire after seven days but does not instruct the user to verify that no pending invitations remain as a step in removing a departing user.)'}

**The blocked reply:** Thanks for getting in touch. Remove the departing user from the team members page [1]. Revoke any API keys that the user created [1]. Verify that no pending invitations remain for that user [1].

**Your verdict:** right block / false alarm

### DEV-0022 · data_export · key says auto_respond

**Ticket:** Export missing recent records The download link from our export has expired and I cannot find a way to generate a new one. Is the file still available?

**Blocked by:** {'grounding_model': 'block: sentences [3] not supported (The article states the file is retained for seven days generally, but does not specify that this period starts after the job completes.)'}

**The blocked reply:** Thanks for getting in touch. Check the exports page to see the current job status [1]. If the original download link has expired, request a fresh link from the exports page [1]. Remember that the export file is kept for seven days after the job completes [1]. Note that the export reflects the data snapshot taken when the job started, so records created during processing are not included [1]. For recurring needs, set up a scheduled export that delivers the file to object storage instead of generating it manually [1].

**Your verdict:** right block / false alarm

### DEV-0024 · database_issue · key says escalate

**Ticket:** Database restore taking hours A restore we started over the weekend is still running. The database is about four hundred gigabytes. Is this a normal duration or has something stalled?

**Blocked by:** {'grounding_words': 'block: sentences 1 (a number not in the article), 2 (25% of its words in the article), 3 (42% of its words in the article)'}

**The blocked reply:** Thanks for getting in touch. A restore of a 400-gigabyte database should take roughly 40 minutes, based on the guideline of ten minutes per hundred gigabytes [1]. If the restore is still running after several hours, it may indicate a stall or an unusually high load on the instance [1]. Verify the restore progress on the database management console and ensure the instance is not under heavy load from other operations [1].

**Your verdict:** right block / false alarm

### DEV-0026 · api_usage_question · key says auto_respond

**Ticket:** When I page through results I am seeing some records twice and missing others entirely. The collection does change while I iterate. Am I doing this the wrong way?

**Blocked by:** {'grounding_words': 'block: sentences 3 (a number not in the article)'}

**The blocked reply:** Thanks for getting in touch. Use cursor pagination for collections that may change while iterating [1]. Pass the next_cursor value from each response as the cursor parameter of the following request, and stop when it is null [1]. Keep the page size at or below two hundred to avoid request rejection [1].

**Your verdict:** right block / false alarm

### DEV-0027 · api_usage_question · key says auto_respond

**Ticket:** Pagination returns duplicates What is the right way to pull a very large extract? Requesting a big page size gets rejected and iterating page by page takes hours.

**Blocked by:** {'grounding_words': 'block: sentences 3 (a number not in the article)'}

**The blocked reply:** Thanks for getting in touch. Use cursor pagination for large extracts to avoid duplicates and timeouts [1]. Pass the next_cursor value from each response as the cursor parameter of the following request, and stop when it is null [1]. Keep the page size at or below two hundred to avoid rejection [1]. For very large extracts, use the export endpoint, which runs asynchronously and returns a download link [1].

**Your verdict:** right block / false alarm

### DEV-0051 · api_key_issue · key says escalate

**Ticket:** A key can read fine but every write returns a permission error. I created it myself and I thought I gave it full access.

**Blocked by:** {'grounding_model': 'block: sentences [3] not supported (The article advises reviewing scopes and rotating keys, but does not explicitly instruct creating a new key specifically to fix a scope exclusion on an existing key.)'}

**The blocked reply:** Thanks for getting in touch. Check the API keys page for the key's status and expiry [1]. Review the scopes attached to the key to ensure it has write permissions and is not limited to read-only [1]. If the key was issued with a scope that excludes the write endpoint, create a new key with the appropriate scopes and use it for write operations [1].

**Your verdict:** right block / false alarm

### DEV-0054 · authentication_failure · key says auto_respond

**Ticket:** MFA code keeps getting rejected We changed the password on our shared account on Monday and now our automated jobs are all failing to authenticate. The console works fine with the new password.

**Blocked by:** {'grounding_model': 'block: the article does not fit the situation; sentences [1, 2] not supported (The cited article DOC-AUTH-001 addresses credential caching and lockouts, not MFA clock drift or recovery codes, which are covered in the uncited DOC-AUTH-002.)'}

**The blocked reply:** Thanks for getting in touch. Ask the user to verify that automatic time synchronisation is enabled on the device generating the MFA code, as clock drift is the most common cause of rejection [2]. If the device is lost or the user cannot generate a valid code, advise signing in with a recovery code and then re-enrolling a new device from the security page [2]. For the automated jobs that are failing, run `cloudserve auth logout` followed by `cloudserve auth login` to discard any cached tokens and authenticate with the new password [1].

**Your verdict:** right block / false alarm

### DEV-0055 · api_usage_question · key says auto_respond

**Ticket:** When I page through results I am seeing some records twice and missing others entirely. The collection does change while I iterate. Am I doing this the wrong way?

**Blocked by:** {'grounding_words': 'block: sentences 3 (a number not in the article)'}

**The blocked reply:** Thanks for getting in touch. Use cursor pagination for collections that may change while iterating [1]. Pass the next_cursor value from each response as the cursor parameter of the following request, and stop when it is null [1]. Keep the page size at or below two hundred to avoid request rejection [1].

**Your verdict:** right block / false alarm

### DEV-0060 · data_export · key says auto_respond

**Ticket:** Export missing recent records i start export two days ago and it still showing as queued. It covers about two million records. please tell what to do.

**Blocked by:** {'grounding_model': 'block: sentences [2] not supported (The article states large exports take several minutes, but does not support the claim that a job queued for two days is still processing.)'}

**The blocked reply:** Thanks for getting in touch. Check the exports page to view the current job status; large exports covering more than a million records can take several minutes [1]. If the export remains queued after a couple of days, it may still be processing; large jobs are queued and processed asynchronously [1]. Once the job completes, request a fresh download link from the exports page if the original link has expired; the file is retained for seven days [1]. Remember that the export reflects the snapshot taken when the job started, so records created during processing are not included [1]. For recurring needs, consider configuring a scheduled export delivered to object storage instead of generating them manually [1].

**Your verdict:** right block / false alarm

### DEV-0066 · api_usage_question · key says auto_respond

**Ticket:** Pagination returns duplicates What is the right way to pull a very large extract? Requesting a big page size gets rejected and iterating page by page takes hours.

**Blocked by:** {'grounding_words': 'block: sentences 3 (a number not in the article)'}

**The blocked reply:** Thanks for getting in touch. Use cursor pagination for large extracts to avoid duplicates and timeouts [1]. Pass the next_cursor value from each response as the cursor parameter of the following request, and stop when it is null [1]. Keep the page size at or below two hundred to avoid rejection [1]. For very large extracts, use the export endpoint, which runs asynchronously and returns a download link [1].

**Your verdict:** right block / false alarm

### DEV-0088 · database_issue · key says auto_respond

**Ticket:** A restore we started yesterday morning is still running. The database is about four hundred gigabytes. Is this a normal duration or has something stalled?

**Blocked by:** {'grounding_words': 'block: sentences 3 (a number not in the article)'}

**The blocked reply:** Thanks for getting in touch. Identify the point you need to restore to [1]. Restore into a new database instance rather than over the existing one, so the current state is preserved while you verify the restore [1]. Allow roughly ten minutes per hundred gigabytes for the restore, and considerably longer where the instance is also under load [1]. Verify the restored data before switching traffic, and keep the original instance until that verification is complete [1].

**Your verdict:** right block / false alarm

### DEV-0094 · account_access · key says auto_respond

**Ticket:** Remove a departing team member user left company. how i remove all his access including key he made?

**Blocked by:** {'grounding_model': "block: sentences [4] not supported (The article instructs to revoke API keys but does not specify deleting them from the 'API keys page'.)"}

**The blocked reply:** Thanks for getting in touch. Check the effective permissions view for the user to confirm their current access [1]. Confirm the user’s invitation was accepted and that they are listed as a team member [1]. Remove the departing user from the team rather than only changing their password [1]. Revoke any API keys that the user created by deleting them from the API keys page [1].

**Your verdict:** right block / false alarm

### DEV-0096 · onboarding · key says auto_respond

**Ticket:** we planning to migrate existing application across. It currently writes uploaded files to local disk.

**Blocked by:** {'grounding_words': 'block: sentences 3 (a number not in the article)'}

**The blocked reply:** Thanks for getting in touch. Externalise configuration before migrating, moving any file-based settings to environment variables or secrets [1]. Identify the uploaded files stored on the local disk and move them to object storage or the managed database first [1]. Run the new deployment in parallel with the existing one and shift a small share of traffic before fully committing to the move [1]. Plan the database migration separately from the application migration to avoid diagnosing failures [1].

**Your verdict:** right block / false alarm

### DEV-0104 · data_export · key says auto_respond

**Ticket:** Our export is missing records that were definitely created before I started the job. Is there something about how the snapshot works that I am misunderstanding?

**Blocked by:** {'grounding_model': "block: the article does not fit the situation; sentences [3] not supported (The article states the snapshot is taken when the job starts, meaning records created before the job should be included, so the customer's issue of missing pre-existing records is not addressed by the)"}

**The blocked reply:** Thanks for getting in touch. Check the exports page for the job status to confirm it completed [1]. Remember that the export captures a snapshot taken when the job started, so any records created during processing are not included [1]. If you need records that may change during export, configure a scheduled export delivered to object storage instead of generating them manually [1].

**Your verdict:** right block / false alarm

### DEV-0126 · authentication_failure · key says escalate

**Ticket:** Invalid credentials error we change password on our shared account around 14:00 yesterday and now our automated jobs all fail to authenticate. console works fine with new password. please help fast.

**Blocked by:** {'grounding_model': "block: the article does not fit the situation; sentences [3] not supported (The article's CLI resolution applies to interactive command-line usage, not automated jobs, and the article does not provide specific instructions for re-authenticating automated processes.)"}

**The blocked reply:** Thanks for getting in touch. Check whether the account is locked by visiting the security page in the console; a locked account shows a red banner and unlocks automatically after thirty minutes [1]. Clear cookies for the CloudServe domain or use a private browsing window and then try logging in again [1]. For the automated jobs, run `cloudserve auth logout` followed by `cloudserve auth login` to discard any cached token and re-authenticate with the new password [1].

**Your verdict:** right block / false alarm

### DEV-0129 · data_export · key says auto_respond

**Ticket:** Export missing recent records Our export is missing records that were definitely created before I started the job. Is there something about how the snapshot works that I am misunderstanding?

**Blocked by:** {'grounding_model': "block: the article does not fit the situation; sentences [1, 2, 4] not supported (The customer's issue is about records created before the job start being missing, which the article does not address, and the reply includes unrelated troubleshooting steps for incomplete exports or e)"}

**The blocked reply:** Thanks for getting in touch. Check the exports page for the job status, as large exports may take several minutes to complete [1]. If the download link has expired, request a fresh link from the exports page; the file remains available for seven days [1]. Remember that the export captures a snapshot taken when the job started, so records created during processing are not included [1]. For recurring needs, configure a scheduled export delivered to object storage instead of generating them manually [1].

**Your verdict:** right block / false alarm

### DEV-0145 · api_key_issue · key says auto_respond

**Ticket:** A key can read fine but every write returns a permission error. I created it myself and I thought I gave it full access.

**Blocked by:** {'grounding_model': 'block: sentences [3] not supported (The article advises creating a replacement key for rotation or exposure, not specifically for fixing missing write permissions on an existing key.)'}

**The blocked reply:** Thanks for getting in touch. Check the API keys page for the key's status and expiry to ensure it is not revoked or expired [1]. Review the scopes attached to the key because a read-only scope will allow reads but block writes [1]. If the key lacks write permissions, create a replacement key with the appropriate full-access scope, deploy it, confirm traffic has moved, then revoke the old key [1]. If the key was exposed, revoke it immediately rather than waiting for the rotation window [1].

**Your verdict:** right block / false alarm

### DEV-0160 · account_access · key says escalate

**Ticket:** Remove a departing team member A team member left around 14:00 yesterday and I want to make sure their access is fully removed, including anything they may have created.

**Blocked by:** {'grounding_words': 'block: sentences 4 (56% of its words in the article)'}

**The blocked reply:** Thanks for getting in touch. Check the effective permissions view for the user to see all direct roles and group memberships combined [1]. Confirm that any invitation for the user was accepted, as pending invitations expire after seven days [1]. Remove the departing user from the team rather than only changing their password, and revoke any API keys they created [1]. Prefer using group membership for access control so future reviews are simpler [1].

**Your verdict:** right block / false alarm

### DEV-0162 · database_issue · key says escalate

**Ticket:** restore we start earlier today is still run. The database is about four hundred gigabytes. waiting for your reply.

**Blocked by:** {'grounding_words': 'block: sentences 3 (a number not in the article)'}

**The blocked reply:** Thanks for getting in touch. Identify the point you need to restore to, as point-in-time recovery covers any moment within the retention window rather than only backup times [1]. Restore into a new database instance rather than over the existing one, so the current state is preserved while you verify the restore [1]. Allow roughly ten minutes per hundred gigabytes for the restore, and considerably longer where the instance is also under load [1]. Verify the restored data before switching traffic, and keep the original instance until that verification is complete [1].

**Your verdict:** right block / false alarm

### DEV-0166 · api_usage_question · key says auto_respond

**Ticket:** How do I page through large results What is the right way to pull a very large extract? Requesting a big page size gets rejected and iterating page by page takes hours.

**Blocked by:** {'grounding_words': 'block: sentences 3 (a number not in the article)'}

**The blocked reply:** Thanks for getting in touch. Use cursor pagination for any data that may change while you iterate [1]. Pass the next_cursor value from each response as the cursor parameter of the following request, and stop when it is null [1]. Keep the page size at or below two hundred, as larger requests are rejected [1]. For very large extracts, use the export endpoint, which runs asynchronously and returns a download link [1].

**Your verdict:** right block / false alarm

### DEV-0167 · api_usage_question · key says auto_respond

**Ticket:** Pagination returns duplicates Our cursor seems to stop working partway through a long iteration. Is there an expiry we should be handling?

**Blocked by:** {'grounding_words': 'block: sentences 3 (a number not in the article)'}

**The blocked reply:** Thanks for getting in touch. Use cursor pagination for any query that may change while iterating [1]. Pass the next_cursor value from each response as the cursor parameter of the following request, and stop when it is null [1]. Keep the page size at or below two hundred to avoid rejections [1]. For very large extracts, use the export endpoint, which runs asynchronously and returns a download link [1]. Cursors expire after one hour, so long-running iterations should handle expiry by restarting from a recorded checkpoint [1].

**Your verdict:** right block / false alarm

### DEV-0169 · database_issue · key says escalate

**Ticket:** Connection pool exhausted restore is running from long time. database is 400 gb. is it normal?

**Blocked by:** {'grounding_words': 'block: sentences 7 (a number not in the article)'}

**The blocked reply:** Thanks for getting in touch. Calculate the total possible connections as pool size multiplied by maximum instances and compare it against your plan's connection limit [1]. Reduce the per-instance pool size rather than raising the limit [1]. Look for queries that hold a transaction open across a network call to another service, as these commonly cause connection leaks [1]. Consider using a connection proxy if you need to keep a high instance count, so pooling occurs once rather than per instance [1]. Identify the point in time you need to restore to, using point-in-time recovery within the retention window [2]. Restore into a new database instance instead of overwriting the existing one to preserve the current state while you verify the restore [2]. Allow roughly ten minutes per hundred gigabytes for the restore, and expect longer if the instance is under load [2]. Verify the restored data before switching traffic and keep the original instance until verification is complete [2].

**Your verdict:** right block / false alarm

### DEV-0176 · authentication_failure · key says auto_respond

**Ticket:** My authenticator app codes are being rejected every time. I have tried generating new ones several times. I do have access to the device, it just will not accept the code.

**Blocked by:** {'grounding_model': 'block: sentences [2, 3] not supported (The customer explicitly states they have access to the device, making the recovery steps for lost devices or missing recovery codes irrelevant to their specific situation.)'}

**The blocked reply:** Thanks for getting in touch. Check that automatic time synchronisation is enabled on the device generating the code [1]. If the device is lost, sign in with a recovery code and re-enrol a new device from the security page [1]. If no recovery codes are available, an account administrator can reset multi-factor authentication for that user from the team members page [1].

**Your verdict:** right block / false alarm

### DEV-0177 · api_usage_question · key says auto_respond

**Ticket:** How do I page through large results What is the right way to pull a very large extract? Requesting a big page size gets rejected and iterating page by page takes hours.

**Blocked by:** {'grounding_words': 'block: sentences 3 (a number not in the article)'}

**The blocked reply:** Thanks for getting in touch. Use cursor pagination for any query that may change while iterating [1]. Pass the next_cursor value from each response as the cursor parameter of the following request, and stop when it is null [1]. Keep the page size at or below two hundred to avoid rejection [1]. For very large extracts, use the export endpoint, which runs asynchronously and returns a download link [1].

**Your verdict:** right block / false alarm

### DEV-0182 · api_usage_question · key says auto_respond

**Ticket:** How do I page through large results Our cursor seems to stop working partway through a long iteration. Is there an expiry we should be handling?

**Blocked by:** {'grounding_words': 'block: sentences 3 (a number not in the article)'}

**The blocked reply:** Thanks for getting in touch. Use cursor pagination for any query that may change while iterating [1]. Pass the next_cursor value from each response as the cursor parameter of the following request, and stop when it is null [1]. Keep the page size at or below two hundred; larger requests are rejected rather than truncated [1]. For very large extracts, use the export endpoint, which runs asynchronously and returns a download link [1]. Cursors expire after one hour, so long-running iterations should handle expiry by restarting from a recorded checkpoint [1].

**Your verdict:** right block / false alarm

### DEV-0185 · data_export · key says auto_respond

**Ticket:** Export job stuck Our export is missing records that were definitely created before I started the job. Is there something about how the snapshot works that I am misunderstanding?

**Blocked by:** {'grounding_model': "block: the article does not fit the situation; sentences [1, 2, 4] not supported (The customer reports missing records created before the job started, which contradicts the article's explanation that only records created during processing are excluded, and the other sentences addre)"}

**The blocked reply:** Thanks for getting in touch. Check the exports page for the job status, as large exports may take several minutes to complete [1]. If the download link has expired, request a fresh link from the exports page; the file is retained for seven days [1]. Remember that the export captures a snapshot taken when the job started, so records created during processing are not included [1]. For recurring needs, consider configuring a scheduled export delivered to object storage instead of generating them manually [1].

**Your verdict:** right block / false alarm

### DEV-0198 · integration_help · key says auto_respond

**Ticket:** Monitoring integration setup Metrics arriving in our monitoring system lag behind what the console shows by a couple of minutes. Is that expected?

**Blocked by:** {'grounding_model': 'error: the check failed: all models failed after 6 calls (last: qwen/qwen3.8-27b: ReadTimeout)'}

**The blocked reply:** Thanks for getting in touch. Check the forwarding status page to see the last successful delivery and any errors returned by the destination [1]. Expect a delay of up to two minutes on metrics, as they are aggregated before being sent [1]. Apply a level filter at the source so that debug output is not forwarded, which is usually the reason volume is higher than expected [1]. Verify the destination credential separately if delivery has stopped entirely, as expired credentials are the most common cause [1].

**Your verdict:** right block / false alarm

### DEV-0201 · api_usage_question · key says auto_respond

**Ticket:** Pagination returns duplicates What is the right way to pull a very large extract? Requesting a big page size gets rejected and iterating page by page takes hours.

**Blocked by:** {'grounding_words': 'block: sentences 3 (a number not in the article)'}

**The blocked reply:** Thanks for getting in touch. Use cursor pagination for large extracts to avoid duplicates and timeouts [1]. Pass the next_cursor value from each response as the cursor parameter of the following request, and stop when it is null [1]. Keep the page size at or below two hundred to avoid rejection [1]. For very large extracts, use the export endpoint, which runs asynchronously and returns a download link [1].

**Your verdict:** right block / false alarm

### DEV-0206 · authentication_failure · key says auto_respond

**Ticket:** We changed the password on our shared account yesterday morning and now our automated jobs are all failing to authenticate. The console works fine with the new password.

**Blocked by:** {'grounding_model': "block: the article does not fit the situation; sentences [1, 2, 3] not supported (The article addresses interactive console/CLI login failures, whereas the customer's issue is automated jobs failing to authenticate, which the article only mentions in a note as a cause of lockouts, )"}

**The blocked reply:** Thanks for getting in touch. Confirm whether the account is locked by checking the security page of the console [1]. Clear cookies for the CloudServe domain or open a private browsing window, then attempt the login again [1]. If the CLI is failing, run `cloudserve auth logout` followed by `cloudserve auth login` to discard the cached token [1].

**Your verdict:** right block / false alarm

### DEV-0207 · api_usage_question · key says auto_respond

**Ticket:** Question about the export endpoint Our cursor seems to stop working partway through a long iteration. Is there an expiry we should be handling?

**Blocked by:** {'grounding_words': 'block: sentences 3 (a number not in the article)'}

**The blocked reply:** Thanks for getting in touch. Use cursor pagination for any query that may change while iterating [1]. Pass the next_cursor value from each response as the cursor parameter of the following request, and stop when it is null [1]. Keep the page size at or below two hundred; larger requests are rejected rather than truncated [1]. Cursors expire after one hour, so long-running iterations should handle expiry by restarting from a recorded checkpoint [1]. For very large extracts, use the export endpoint, which runs asynchronously and returns a download link [1].

**Your verdict:** right block / false alarm

### DEV-0209 · database_issue · key says auto_respond

**Ticket:** No connections available error restore is running from long time. database is 400 gb. is it normal?

**Blocked by:** {'grounding_words': 'block: sentences 5 (a number not in the article)'}

**The blocked reply:** Thanks for getting in touch. Calculate the total possible connections as pool size multiplied by maximum instances and compare it against your plan's connection limit [1]. Reduce the per-instance pool size rather than raising the limit, as a large number of small pools is usually the wrong shape for a scaled service [1]. Look for queries that hold a transaction open across a network call to another service, which is the most common cause of leaks of this kind [1]. Consider a connection proxy if the instance count must remain high, so that pooling happens once rather than per instance [1]. Allow roughly ten minutes per hundred gigabytes for the restore, and considerably longer where the instance is also under load [2].

**Your verdict:** right block / false alarm

### DEV-0212 · account_access · key says auto_respond

**Ticket:** Remove a departing team member A team member left earlier today and I want to make sure their access is fully removed, including anything they may have created.

**Blocked by:** {'grounding_model': 'block: sentences [3] not supported (The article states pending invitations expire after seven days but does not instruct the user to verify that no pending invitations remain as a step in removing a departing user.)'}

**The blocked reply:** Thanks for getting in touch. Remove the departing user from the team members page [1]. Revoke any API keys that the user created [1]. Verify that no pending invitations remain for that user [1].

**Your verdict:** right block / false alarm

### DEV-0216 · api_usage_question · key says auto_respond

**Ticket:** Question about the export endpoint Our cursor seems to stop working partway through a long iteration. Is there an expiry we should be handling?

**Blocked by:** {'grounding_words': 'block: sentences 3 (a number not in the article)'}

**The blocked reply:** Thanks for getting in touch. Use cursor pagination for any query that may change while iterating [1]. Pass the next_cursor value from each response as the cursor parameter of the following request, and stop when it is null [1]. Keep the page size at or below two hundred; larger requests are rejected rather than truncated [1]. Cursors expire after one hour, so long-running iterations should handle expiry by restarting from a recorded checkpoint [1]. For very large extracts, use the export endpoint, which runs asynchronously and returns a download link [1].

**Your verdict:** right block / false alarm

### DEV-0217 · api_usage_question · key says auto_respond

**Ticket:** How do I page through large results Our cursor seems to stop working partway through a long iteration. Is there an expiry we should be handling?

**Blocked by:** {'grounding_words': 'block: sentences 3 (a number not in the article)'}

**The blocked reply:** Thanks for getting in touch. Use cursor pagination for any query that may change while iterating [1]. Pass the next_cursor value from each response as the cursor parameter of the following request, and stop when it is null [1]. Keep the page size at or below two hundred; larger requests are rejected rather than truncated [1]. For very large extracts, use the export endpoint, which runs asynchronously and returns a download link [1]. Cursors expire after one hour, so long-running iterations should handle expiry by restarting from a recorded checkpoint [1].

**Your verdict:** right block / false alarm

### DEV-0218 · authentication_failure · key says auto_respond

**Ticket:** Since yesterday morning I cannot get into the console at all. My colleague on the same team signs in without any trouble, so it does not appear to be a general outage. Could you check whether something is wrong with my account specifically?

**Blocked by:** {'grounding_model': 'block: sentences [3] not supported (The customer explicitly states they cannot access the console, so the CLI-specific instruction in sentence 3 is irrelevant to their reported issue.)'}

**The blocked reply:** Thanks for getting in touch. Check if the account is locked by visiting the security page of the console; a locked account shows a red banner and unlocks automatically after thirty minutes [1]. Clear cookies for the CloudServe domain or open a private browsing window, then try logging in again [1]. If using the CLI, run `cloudserve auth logout` followed by `cloudserve auth login` to discard any cached token [1].

**Your verdict:** right block / false alarm

### DEV-0219 · integration_help · key says auto_respond

**Ticket:** Connecting our CI pipeline Log forwarding to our external system stopped late last night and has not resumed by itself. The destination is healthy as far as we can tell.

**Blocked by:** {'grounding_model': 'block: sentences [3] not supported (The article states that debug logs cause higher volume, not that they cause forwarding pauses.)'}

**The blocked reply:** Thanks for getting in touch. Check the forwarding status page to see the last successful delivery and any error returned by the destination [1]. Verify that the destination credential is still valid, as expired credentials are the most common cause of stopped delivery [1]. Apply a level filter at the source so that debug output is not forwarded, which can increase volume and cause pauses [1]. If forwarding has paused after an hour of consecutive failures, resume it manually once the destination is healthy [1].

**Your verdict:** right block / false alarm

### DEV-0227 · configuration_help · key says auto_respond

**Ticket:** Environment variable not being read Where should secrets be stored so they do not appear in the logs? At the moment ours are being printed at startup and I am not comfortable with that.

**Blocked by:** {'grounding_model': 'block: sentences [3] not supported (The article states that secrets are masked in logs and does not claim that environment overrides cause variables to be printed at startup.)'}

**The blocked reply:** Thanks for getting in touch. Store any sensitive values as a secret rather than a variable so they are masked in logs and not readable through the API after creation [1]. Check the scope at which the variable was defined; service scope overrides project scope, and project scope overrides organisation defaults [1]. Review the environment overrides page to see if any overrides are causing the variable to be printed at startup [1]. Redeploy the service after making these changes so the new configuration takes effect [1].

**Your verdict:** right block / false alarm

### DEV-0233 · onboarding · key says auto_respond

**Ticket:** Migrating our app across We are planning to migrate an existing application across. It currently writes uploaded files to local disk. What should we change before we move?

**Blocked by:** {'grounding_words': 'block: sentences 3 (a number not in the article)'}

**The blocked reply:** Thanks for getting in touch. Externalise configuration before migrating, moving any file-based settings to environment variables or secrets [1]. Identify local state such as uploaded files or session data and move it to object storage or the managed database first [1]. Run the new deployment in parallel with the existing one and shift a small share of traffic before committing to the move [1]. Plan the database migration separately from the application migration; attempting both at once makes any failure hard to diagnose [1].

**Your verdict:** right block / false alarm

### DEV-0256 · onboarding · key says auto_respond

**Ticket:** We are planning to migrate an existing application across. It currently writes uploaded files to local disk. What should we change before we move?

**Blocked by:** {'grounding_words': 'block: sentences 3 (a number not in the article)'}

**The blocked reply:** Thanks for getting in touch. Externalise configuration before migrating, moving any file-based settings to environment variables or secrets [1]. Identify local state such as uploaded files or session data and move it to object storage or the managed database first [1]. Run the new deployment in parallel with the existing one and shift a small share of traffic before committing to the move [1]. Plan the database migration separately from the application migration; attempting both at once makes any failure hard to diagnose [1].

**Your verdict:** right block / false alarm

### DEV-0264 · api_usage_question · key says auto_respond

**Ticket:** Pagination returns duplicates Our cursor seems to stop working partway through a long iteration. Is there an expiry we should be handling?

**Blocked by:** {'grounding_words': 'block: sentences 3 (a number not in the article)'}

**The blocked reply:** Thanks for getting in touch. Use cursor pagination for any query that may change while iterating [1]. Pass the next_cursor value from each response as the cursor parameter of the following request, and stop when it is null [1]. Keep the page size at or below two hundred to avoid rejections [1]. For very large extracts, use the export endpoint, which runs asynchronously and returns a download link [1]. Cursors expire after one hour, so long-running iterations should handle expiry by restarting from a recorded checkpoint [1].

**Your verdict:** right block / false alarm

### DEV-0278 · data_export · key says auto_respond

**Ticket:** Our export is missing records that were definitely created before I started the job. Is there something about how the snapshot works that I am misunderstanding?

**Blocked by:** {'grounding_model': 'block: the article does not fit the situation (The article explains that records created *during* processing are excluded, but the customer reports records created *before* the job started are missing, which the article does not address.)'}

**The blocked reply:** Thanks for getting in touch. Check the exports page for the job status to confirm the export completed successfully [1]. If the download link has expired, request a fresh link from the exports page; the file remains available for seven days [1]. Remember that the export captures a snapshot taken when the job started, so any records created after the job began are not included in that export [1].

**Your verdict:** right block / false alarm

### DEV-0279 · data_export · key says auto_respond

**Ticket:** I started an export late last night and it is still showing as queued. It covers about two million records. Should I cancel and try again?

**Blocked by:** {'grounding_words': 'block: sentences 3 (29% of its words in the article)'}

**The blocked reply:** Thanks for getting in touch. Check the exports page to see the current job status [1]. Large exports covering more than a million records commonly take several minutes to complete [1]. If the export remains queued for an extended period, you can cancel it and start a new job, but it is usually not necessary to cancel unless it has stalled [1]. Once the job completes, request a fresh download link from the exports page if the original link has expired [1].

**Your verdict:** right block / false alarm

### DEV-0295 · onboarding · key says auto_respond

**Ticket:** Migrating our app across can you please point me at the right starting place? i am having created an account but console has more in it than I expect. this is urgent for us.

**Blocked by:** {'grounding_model': 'block: the article does not fit the situation (The customer is asking for a general onboarding guide for a new account, not for help with data residency or regional migration, so the cited article does not address their actual situation.)'}

**The blocked reply:** Thanks for getting in touch. Check the region shown on the organisation settings page as it determines where primary data is stored [1]. Enable read replicas in additional regions to reduce latency for distant users without moving primary storage [1]. Review the backup replication setting if a single-region requirement applies, since cross-region replication is enabled by default [1]. Migrating an organisation between regions requires a planned migration with support and involves a maintenance window [1].

**Your verdict:** right block / false alarm

### DEV-0310 · onboarding · key says auto_respond

**Ticket:** Migrating our app across Could you point me at the right starting place? I have created an account but the console has more in it than I expected.

**Blocked by:** {'grounding_words': 'block: sentences 3 (a number not in the article)'}

**The blocked reply:** Thanks for getting in touch. Externalise configuration before migrating, moving any file-based settings to environment variables or secrets [3]. Identify local state such as uploaded files or session data and move it to object storage or the managed database first [3]. Run the new deployment in parallel with the existing one and shift a small share of traffic before committing to the move [3]. Plan the database migration separately from the application migration to avoid diagnosing combined failures [3].

**Your verdict:** right block / false alarm

### DEV-0311 · sso_configuration · key says auto_respond

**Ticket:** single sign-on works for our engineering group but finance group gets error. Both configured identically as we know. waiting for your reply.

**Blocked by:** {'grounding_model': 'error: the check failed: all models failed after 6 calls (last: qwen/qwen3.8-27b: HTTP 429)'}

**The blocked reply:** Thanks for getting in touch. Compare the assertion consumer service URL in your identity provider against the value shown on the SSO settings page and ensure they match exactly, including the trailing path [1]. Inspect a failing SAML assertion and confirm the NameID is the user's email address in lower case [1]. Enable just-in-time provisioning if new finance users should be created on first login, and set a default role for provisioned users [1]. Keep at least one administrator account with password access while testing, so a misconfiguration does not lock the whole organisation out [1].

**Your verdict:** right block / false alarm

### DEV-0312 · authentication_failure · key says auto_respond

**Ticket:** Login fails after password change My authenticator app codes are being rejected every time. I have tried generating new ones several times. I do have access to the device, it just will not accept the code.

**Blocked by:** {'grounding_model': 'block: sentences [2] not supported (The customer explicitly states they have access to the device, so the advice for a lost device in sentence 2 does not apply to their situation.)'}

**The blocked reply:** Thanks for getting in touch. Check that automatic time synchronisation is enabled on the device generating the code [1]. If the device is lost, sign in with a recovery code and re-enrol a new device from the security page [1]. If no recovery codes are available, an account administrator can reset multi-factor authentication for that user from the team members page [1].

**Your verdict:** right block / false alarm

### DEV-0316 · quota_or_overage · key says auto_respond

**Ticket:** Usage allowance already consumed We were throttled around 14:00 yesterday after a traffic increase and it took down part of our product. We would rather pay overage than be stopped. How do we change that?

**Blocked by:** {'grounding_model': "block: sentences [2] not supported (The article states that production workloads 'generally need' overage, whereas the reply prescribes to 'choose overage' as a definitive instruction.)"}

**The blocked reply:** Thanks for getting in touch. Check the current period usage against the plan allowance on the billing page [1]. Decide deliberately between a hard spend cap, which stops the service, and overage, which continues at the listed rate, and choose overage for production workloads [1]. Configure alerts at fifty, eighty and ninety-five per cent of allowance rather than relying on the cap as a warning [1]. Where a cap has stopped a production service, an account owner can raise it immediately from the billing page and service resumes within a minute [1].

**Your verdict:** right block / false alarm

### DEV-0320 · api_usage_question · key says auto_respond

**Ticket:** How do I page through large results Our cursor seems to stop working partway through a long iteration. Is there an expiry we should be handling?

**Blocked by:** {'grounding_words': 'block: sentences 3 (a number not in the article)'}

**The blocked reply:** Thanks for getting in touch. Use cursor pagination for anything that may change while you iterate [1]. Pass the next_cursor value from each response as the cursor parameter of the following request, and stop when it is null [1]. Keep page size at or below two hundred [1]. Cursors expire after one hour; long-running iterations should handle expiry by restarting from a recorded checkpoint [1].

**Your verdict:** right block / false alarm

### DEV-0326 · data_export · key says auto_respond

**Ticket:** Our export is missing records that were definitely created before I started the job. Is there something about how the snapshot works that I am misunderstanding?

**Blocked by:** {'grounding_model': 'block: the article does not fit the situation; sentences [3] not supported (The article states the snapshot is taken when the job starts, which does not explain why records created *before* the job started are missing, and the article does not suggest scheduling a recurring e)'}

**The blocked reply:** Thanks for getting in touch. Check the exports page for the job status to confirm it completed [1]. Remember that the export captures a snapshot taken when the job started, so any records created during processing are not included [1]. If you need all recent records, schedule a recurring export to object storage instead of generating them manually [1].

**Your verdict:** right block / false alarm

### DEV-0329 · data_export · key says auto_respond

**Ticket:** Download link expired The download link from our export has expired and I cannot find a way to generate a new one. Is the file still available?

**Blocked by:** {'grounding_model': 'error: the check failed: all models failed after 6 calls (last: qwen/qwen3.8-27b: HTTP 429)'}

**The blocked reply:** Thanks for getting in touch. Check the exports page for the job status to confirm the export is still present [1]. Request a fresh link from the exports page if the original has expired [1]. The underlying file is retained for seven days, so you can still download it within that period [1].

**Your verdict:** right block / false alarm

### DEV-0331 · data_export · key says auto_respond

**Ticket:** I started an export over the weekend and it is still showing as queued. It covers about two million records. Should I cancel and try again?

**Blocked by:** {'grounding_words': 'block: sentences 2 (53% of its words in the article), 5 (57% of its words in the article)'}

**The blocked reply:** Thanks for getting in touch. Check the exports page to see the current job status; large exports covering more than a million records often take several minutes to complete [1]. If the export remains queued for an extended period, wait until the job finishes rather than canceling it, as the system processes large jobs asynchronously [1]. Once the job completes, you can request a fresh download link from the exports page; the file will be available for seven days even if the original link expires [1]. Remember that the export reflects the data snapshot at the start of the job, so any records created during processing will not appear in the file [1]. For future needs, consider setting up a scheduled export delivered to object storage to avoid manual queuing of large datasets [1].

**Your verdict:** right block / false alarm

### DEV-0335 · authentication_failure · key says auto_respond

**Ticket:** Login fails after password change My authenticator app codes are being rejected every time. I have tried generating new ones several times. I do have access to the device, it just will not accept the code.

**Blocked by:** {'grounding_model': 'block: the article does not fit the situation; sentences [2, 3] not supported (The customer explicitly states they have access to the device, making the recovery steps for lost devices or missing recovery codes irrelevant to their specific situation.)'}

**The blocked reply:** Thanks for getting in touch. Check that automatic time synchronization is enabled on the device generating the authenticator code [1]. If the device is lost, sign in with a recovery code and then re-enrol a new device from the security page [1]. If no recovery codes are available, an account administrator can reset multi-factor authentication for the user from the team members page [1].

**Your verdict:** right block / false alarm

### DEV-0338 · database_issue · key says escalate

**Ticket:** A restore we started two days ago is still running. The database is about four hundred gigabytes. Is this a normal duration or has something stalled?

**Blocked by:** {'grounding_words': 'block: sentences 3 (a number not in the article)'}

**The blocked reply:** Thanks for getting in touch. Identify the point you need to restore to, as point-in-time recovery covers any moment within the retention window [1]. Restore into a new database instance rather than over the existing one so you can preserve the current state while verifying the restore [1]. Allow roughly ten minutes per hundred gigabytes for the restore, and considerably longer if the instance is under load [1]. Verify the restored data before switching traffic and keep the original instance until verification is complete [1].

**Your verdict:** right block / false alarm

### DEV-0341 · integration_help · key says auto_respond

**Ticket:** Connecting our CI pipeline log forwarding to our external system stop late last night and not resumed by itself. The destination is healthy as we know.

**Blocked by:** {'grounding_model': 'block: sentences [2] not supported (The customer reported log forwarding issues, but sentence 2 discusses metric aggregation delays which are not relevant to the reported log forwarding failure.)'}

**The blocked reply:** Thanks for getting in touch. Check the forwarding status page to see the last successful delivery and any error returned by the destination [1]. Expect a delay of up to two minutes on metrics, as they are aggregated before being sent [1]. Verify the destination credential separately, since expired credentials are the most common cause of stopped delivery [1]. If forwarding has paused, resume it manually after confirming the destination is healthy [1].

**Your verdict:** right block / false alarm

### DEV-0347 · configuration_help · key says escalate

**Ticket:** Our staging environment is picking up production configuration values. I cannot work out where the override is coming from.

**Blocked by:** {'grounding_words': 'block: sentences 3 (43% of its words in the article)'}

**The blocked reply:** Thanks for getting in touch. Check the scope at which each variable was defined, noting that service scope overrides project scope and project scope overrides organisation defaults [1]. Review the environment overrides page, which lists values that differ from the defaults for each environment [1]. Adjust any overrides so that the staging environment uses its intended values [1]. Redeploy after changing configuration, as running containers do not pick up new values without a restart [1].

**Your verdict:** right block / false alarm

### DEV-0353 · deployment_failure · key says escalate

**Ticket:** Build fails in the pipeline Our deployment reaches running and then rolls back after about a minute. The logs mention a health check timeout. It runs perfectly on my machine and in staging.

**Blocked by:** {'grounding_model': 'block: sentences [5, 6, 7] not supported (The cited article DOC-DEPLOY-001 addresses health check timeouts during deployment, not build failures or dependency resolution issues covered by the other cited article.)'}

**The blocked reply:** Thanks for getting in touch. Confirm the container is listening on the port declared in the service definition [2]. Increase the initial delay for the health check, starting with thirty seconds, to allow the application time to warm up [2]. Compare the environment variables present in the deployment against those required by the application and add any missing ones [2]. Inspect the container logs from the failed revision rather than the running one to see the exact health-check failure details [2]. Pin all dependencies with exact versions and commit the lock file to avoid unpinned updates causing build failures [1]. Compare the runtime version declared in the build configuration with the version used locally [1]. Clear the build cache from the settings page and trigger a fresh build to rule out a corrupted artefact [1].

**Your verdict:** right block / false alarm

### DEV-0358 · onboarding · key says auto_respond

**Ticket:** New to the platform, where to begin we are planning to migrate an existing application across. It currently writes uploaded files to local disk. kindly check and revert.

**Blocked by:** {'grounding_words': 'block: sentences 3 (a number not in the article)'}

**The blocked reply:** Thanks for getting in touch. Externalise any configuration that is currently read from files on disk by moving it to environment variables or secrets [1]. Identify local state such as uploaded files or session data and move it to object storage or the managed database before migration [1]. Run the new deployment in parallel with the existing one and shift a small share of traffic to it before committing to the full move [1]. Plan the database migration separately from the application migration to avoid diagnosing combined failures [1].

**Your verdict:** right block / false alarm

### DEV-0360 · sso_configuration · key says auto_respond

**Ticket:** Single sign-on works for our engineering group but the finance group gets an error. Both are configured identically as far as we can tell. Any idea what differs?

**Blocked by:** {'grounding_model': 'error: the check failed: all models failed after 6 calls (last: qwen/qwen3.8-27b: HTTP 429)'}

**The blocked reply:** Thanks for getting in touch. Compare the assertion consumer service URL in your identity provider against the value shown on the SSO settings page; they must match exactly, including the trailing path [1]. Inspect a failing assertion and confirm the NameID is the user's email address in lower case [1]. Enable just-in-time provisioning if new users should be created on first login, and set a default role for provisioned users [1]. Keep at least one administrator account with password access while testing, so a misconfiguration does not lock the whole organisation out [1].

**Your verdict:** right block / false alarm

### DEV-0361 · quota_or_overage · key says auto_respond

**Ticket:** Our spend cap stopped a production workload overnight. We need it raised immediately and then we need to reconsider how we have this configured.

**Blocked by:** {'grounding_model': 'error: the check failed: all models failed after 6 calls (last: qwen/qwen3.8-27b: HTTP 429)'}

**The blocked reply:** Thanks for getting in touch. Check the current period usage against the plan allowance on the billing page [1]. Decide deliberately between a hard spend cap, which stops the service, and overage, which continues at the listed rate [1]. Configure alerts at fifty, eighty and ninety-five per cent of allowance rather than relying on the cap as a warning [1]. Raise the spend cap immediately from the billing page; the service will resume within a minute [1].

**Your verdict:** right block / false alarm

### DEV-0364 · data_export · key says auto_respond

**Ticket:** I started an export around 14:00 yesterday and it is still showing as queued. It covers about two million records. Should I cancel and try again?

**Blocked by:** {'grounding_words': 'block: sentences 2 (43% of its words in the article), 5 (58% of its words in the article)'}

**The blocked reply:** Thanks for getting in touch. Check the exports page to view the current job status; large exports covering more than a million records often take several minutes to complete [1]. If the export remains queued after a reasonable time, you can cancel it and submit a new request, but first confirm that the job has not started processing [1]. Once the export completes, download the file using the link provided on the exports page; the link is valid for twenty-four hours and the file is retained for seven days [1]. Remember that the export reflects the data snapshot at the start of the job, so any records created during processing will not appear in the file [1]. For future needs, consider setting up a scheduled export delivered to object storage to avoid manual queuing [1].

**Your verdict:** right block / false alarm

### DEV-0365 · quota_or_overage · key says auto_respond

**Ticket:** Usage allowance already consumed Overage charges appeared on our invoice that we were not expecting. We thought we were well inside our allowance.

**Blocked by:** {'grounding_model': 'block: sentences [3] not supported (The article advises configuring alerts to avoid relying on the cap as a warning, whereas the reply claims they warn before the cap is reached.)'}

**The blocked reply:** Thanks for getting in touch. Check the current period usage against the plan allowance on the billing page [1]. Decide deliberately between a hard spend cap, which stops the service, and overage, which continues at the listed rate [1]. Configure alerts at fifty, eighty and ninety-five per cent of allowance to be warned before the cap is reached [1]. If a cap has stopped a production service, an account owner can raise it immediately from the billing page and the service resumes within a minute [1].

**Your verdict:** right block / false alarm

### DEV-0368 · api_usage_question · key says auto_respond

**Ticket:** Pagination returns duplicates Our cursor seems to stop working partway through a long iteration. Is there an expiry we should be handling?

**Blocked by:** {'grounding_words': 'block: sentences 3 (a number not in the article)'}

**The blocked reply:** Thanks for getting in touch. Use cursor pagination for any data that may change while iterating, as offset pagination can cause duplicates [1]. Pass the next_cursor value from each response as the cursor parameter of the following request and stop when it is null [1]. Keep the page size at or below two hundred; larger requests are rejected rather than truncated [1]. For very large extracts, use the export endpoint, which runs asynchronously and returns a download link [1]. Cursors expire after one hour, so long-running iterations should handle expiry by restarting from a recorded checkpoint [1].

**Your verdict:** right block / false alarm

### DEV-0374 · database_issue · key says escalate

**Ticket:** Database restore taking hours we get errors saying no connection is available. This start when we scaled up our service. please do the needful.

**Blocked by:** {'grounding_words': 'block: sentences 3 (a number not in the article)'}

**The blocked reply:** Thanks for getting in touch. Identify the point in time you need to restore to, as point-in-time recovery covers any moment within the retention window [1]. Restore the data into a new database instance rather than overwriting the existing one so you can verify the restore while preserving the current state [1]. Allow roughly ten minutes per hundred gigabytes for the restore and expect longer if the instance is under load [1]. Verify the restored data before switching traffic and keep the original instance until verification is complete [1]. Calculate the total possible connections as pool size multiplied by maximum instances and compare it against your plan's connection limit [2]. Reduce the per-instance pool size rather than raising the limit, as many small pools can exceed the connection limit when scaling [2]. Look for queries that hold a transaction open across a network call, which commonly causes connections to be exhausted [2]. Consider using a connection proxy if you must keep a high instance count, so pooling occurs centrally instead of per instance [2].

**Your verdict:** right block / false alarm

### DEV-0377 · api_usage_question · key says auto_respond

**Ticket:** Question about the export endpoint What is the right way to pull a very large extract? Requesting a big page size gets rejected and iterating page by page takes hours.

**Blocked by:** {'grounding_model': 'error: the check failed: all models failed after 6 calls (last: qwen/qwen3.8-27b: HTTP 429)'}

**The blocked reply:** Thanks for getting in touch. Use the export endpoint for very large extracts, as it runs asynchronously and returns a download link [1]. Check the exports page for the job status, noting that jobs over a million records may take several minutes [2]. If the download link has expired, request a fresh link from the exports page; the file is retained for seven days [2].

**Your verdict:** right block / false alarm

### DEV-0378 · database_issue · key says auto_respond

**Ticket:** Database restore taking hours connection not available error coming. we scale up service then problem start. please check.

**Blocked by:** {'grounding_words': 'block: sentences 2 (a number not in the article)'}

**The blocked reply:** Thanks for getting in touch. Identify the point you need to restore to and restore into a new database instance rather than over the existing one so the current state is preserved while you verify the restore [1]. Allow roughly ten minutes per hundred gigabytes for the restore, and considerably longer where the instance is also under load [1]. Verify the restored data before switching traffic, and keep the original instance until that verification is complete [1]. Calculate the total possible connections as pool size multiplied by maximum instances, and compare it against your plan's connection limit [2]. Reduce the per-instance pool size rather than raising the limit, as a large number of small pools is usually the wrong shape for a scaled service [2]. Look for queries that hold a transaction open across a network call to another service, which is the most common cause of leaks of this kind [2].

**Your verdict:** right block / false alarm

### DEV-0384 · api_usage_question · key says escalate

**Ticket:** How do I page through large results Our cursor seems to stop working partway through a long iteration. Is there an expiry we should be handling?

**Blocked by:** {'grounding_words': 'block: sentences 3 (a number not in the article)'}

**The blocked reply:** Thanks for getting in touch. Use cursor pagination for any query that may change while iterating [1]. Pass the next_cursor value from each response as the cursor parameter of the following request, and stop when it is null [1]. Keep the page size at or below two hundred; larger requests are rejected rather than truncated [1]. For very large extracts, use the export endpoint, which runs asynchronously and returns a download link [1]. Cursors expire after one hour, so long-running iterations should handle expiry by restarting from a recorded checkpoint [1].

**Your verdict:** right block / false alarm

### DEV-0401 · data_export · key says escalate

**Ticket:** Export job stuck I started an export last Friday and it is still showing as queued. It covers about two million records. Should I cancel and try again?

**Blocked by:** {'grounding_words': 'block: sentences 3 (33% of its words in the article), 5 (50% of its words in the article)'}

**The blocked reply:** Thanks for getting in touch. Check the exports page to see the current status of the job [1]. Large exports, such as those with more than a million records, can take several minutes to process [1]. If the job remains queued for an extended period, you can cancel it and start a new export, but first confirm that the current job is still pending [1]. Once the export completes, download the file using the link provided on the exports page; the link is valid for twenty-four hours [1]. For future needs, consider setting up a scheduled export delivered to object storage to avoid manual retries [1].

**Your verdict:** right block / false alarm

### DEV-0408 · database_issue · key says auto_respond

**Ticket:** restore is running from long time. database is 400 gb. is it normal?

**Blocked by:** {'grounding_words': 'block: sentences 3 (a number not in the article)'}

**The blocked reply:** Thanks for getting in touch. Identify the point you need to restore to [1]. Restore into a new database instance rather than over the existing one, so the current state is preserved while you verify the restore [1]. Allow roughly ten minutes per hundred gigabytes for the restore, and considerably longer where the instance is also under load [1]. Verify the restored data before switching traffic, and keep the original instance until that verification is complete [1].

**Your verdict:** right block / false alarm

### DEV-0422 · api_usage_question · key says auto_respond

**Ticket:** Question about the export endpoint Our cursor seems to stop working partway through a long iteration. Is there an expiry we should be handling?

**Blocked by:** {'grounding_words': 'block: sentences 3 (a number not in the article)'}

**The blocked reply:** Thanks for getting in touch. Use cursor pagination for any data that may change while iterating, as offset pagination can miss or repeat records [1]. Pass the next_cursor value from each response as the cursor parameter of the following request and stop when it is null [1]. Keep the page size at or below two hundred; larger requests are rejected rather than truncated [1]. Be aware that cursors expire after one hour, so long-running iterations should handle expiry by restarting from a recorded checkpoint [1]. For very large extracts, consider using the export endpoint, which runs asynchronously and returns a download link [1].

**Your verdict:** right block / false alarm

### DEV-0424 · onboarding · key says auto_respond

**Ticket:** we planning to migrate existing application across. It currently writes uploaded files to local disk.

**Blocked by:** {'grounding_words': 'block: sentences 3 (a number not in the article)'}

**The blocked reply:** Thanks for getting in touch. Externalise configuration before migrating; move any file-based settings to environment variables or secrets [1]. Identify local state such as uploaded files and shift it to object storage or the managed database first [1]. Run the new deployment in parallel with the existing one and shift a small share of traffic before committing fully [1]. Plan the database migration separately from the application migration to simplify troubleshooting [1].

**Your verdict:** right block / false alarm

### DEV-0428 · onboarding · key says auto_respond

**Ticket:** New to the platform, where to begin we are planning to migrate existing application across. It currently writes uploaded files to local disk. please do the needful.

**Blocked by:** {'grounding_words': 'block: sentences 3 (a number not in the article)'}

**The blocked reply:** Thanks for getting in touch. Externalise configuration before migrating, moving any file-based settings to environment variables or secrets [1]. Move uploaded files or session data to object storage or the managed database before the migration [1]. Run the new deployment in parallel with the existing one and shift a small share of traffic before fully committing to the move [1]. Plan the database migration separately from the application migration to avoid diagnosing failures [1].

**Your verdict:** right block / false alarm

### DEV-0429 · data_export · key says auto_respond

**Ticket:** Export missing recent records Our export is missing records that were definitely created before I started the job. Is there something about how the snapshot works that I am misunderstanding?

**Blocked by:** {'grounding_model': "block: the article does not fit the situation; sentences [1, 2, 4] not supported (The customer's issue is about records created before the job start being missing, which the article does not address, and the reply includes unrelated troubleshooting steps for incomplete exports or e)"}

**The blocked reply:** Thanks for getting in touch. Check the exports page for the job status, as large exports may take several minutes to complete [1]. If the download link has expired, request a fresh link from the exports page; the file remains available for seven days [1]. Remember that the export captures a snapshot taken when the job started, so records created during processing are not included [1]. For recurring needs, configure a scheduled export delivered to object storage instead of generating them manually [1].

**Your verdict:** right block / false alarm

### DEV-0430 · api_usage_question · key says auto_respond

**Ticket:** Pagination returns duplicates What is the right way to pull a very large extract? Requesting a big page size gets rejected and iterating page by page takes hours.

**Blocked by:** {'grounding_words': 'block: sentences 3 (a number not in the article)'}

**The blocked reply:** Thanks for getting in touch. Use cursor pagination for any data that may change while you iterate, as offset pagination can cause duplicates [1]. Pass the next_cursor value from each response as the cursor parameter of the following request and stop when it is null [1]. Keep the page size at or below two hundred, since larger requests are rejected [1]. For very large extracts, use the export endpoint, which runs asynchronously and returns a download link [1].

**Your verdict:** right block / false alarm

### DEV-0434 · api_usage_question · key says auto_respond

**Ticket:** How do I page through large results What is the right way to pull a very large extract? Requesting a big page size gets rejected and iterating page by page takes hours.

**Blocked by:** {'grounding_words': 'block: sentences 3 (a number not in the article)'}

**The blocked reply:** Thanks for getting in touch. Use cursor pagination for any data that may change while you iterate [1]. Pass the next_cursor value from each response as the cursor parameter of the following request, and stop when it is null [1]. Keep the page size at or below two hundred, as larger requests are rejected [1]. For very large extracts, use the export endpoint, which runs asynchronously and returns a download link [1].

**Your verdict:** right block / false alarm

### DEV-0439 · database_issue · key says escalate

**Ticket:** Database restore taking hours Our connection pool appears to be exhausting under moderate load. We have already increased the pool size and it made things worse.

**Blocked by:** {'grounding_words': 'block: sentences 7 (a number not in the article)'}

**The blocked reply:** Thanks for getting in touch. Calculate the total possible connections as pool size multiplied by maximum instances and compare it against your plan's connection limit [1]. Reduce the per-instance pool size rather than raising the limit, as a large number of small pools is usually the wrong shape for a scaled service [1]. Look for queries that hold a transaction open across a network call to another service, which is the most common cause of leaks of this kind [1]. Consider a connection proxy if the instance count must remain high, so that pooling happens once rather than per instance [1]. Identify the point you need to restore to; point-in-time recovery covers any moment within the retention window rather than only backup times [2]. Restore into a new database instance rather than over the existing one, so the current state is preserved while you verify the restore [2]. Allow roughly ten minutes per hundred gigabytes for the restore, and considerably longer where the instance is also under load [2]. Verify the restored data before switching traffic, and keep the original instance until that verification is complete [2].

**Your verdict:** right block / false alarm

### DEV-0446 · data_export · key says auto_respond

**Ticket:** i start export two days ago and it is still showing as queued. It covers about two million records. kindly check and revert.

**Blocked by:** {'grounding_model': 'block: sentences [3] not supported (The article states that requesting a fresh link is for when the original has expired, not when the job is still queued.)'}

**The blocked reply:** Thanks for getting in touch. Check the exports page to view the current job status and confirm it is still queued [1]. Large exports covering more than a million records can take several minutes, so allow time for processing [1]. If the export remains queued after a reasonable period, request a fresh link from the exports page; the underlying file is retained for seven days [1]. Remember that the export reflects the snapshot taken when the job started, so records created during processing are not included [1]. For recurring large exports, consider configuring a scheduled export delivered to object storage instead of generating them manually [1].

**Your verdict:** right block / false alarm

### DEV-0451 · database_issue · key says auto_respond

**Ticket:** Database restore taking hours restore we start earlier today is still run. database about four hundred gigabytes. please do the needful.

**Blocked by:** {'grounding_words': 'block: sentences 3 (a number not in the article)'}

**The blocked reply:** Thanks for getting in touch. Identify the point in time you need to restore to, as point-in-time recovery covers any moment within the retention window [1]. Restore the data into a new database instance rather than overwriting the existing one so you can preserve the current state while verifying the restore [1]. Allow roughly ten minutes per hundred gigabytes for the restore, which means a 400 GB database may take around forty minutes plus additional time if the instance is under load [1]. After the restore completes, verify the restored data before switching traffic and keep the original instance until verification is finished [1].

**Your verdict:** right block / false alarm

### DEV-0458 · integration_help · key says escalate

**Ticket:** log forwarding to our external system stop late last night and not resumed by itself. destination is healthy as we know.

**Blocked by:** {'grounding_words': 'block: sentences 3 (57% of its words in the article)'}

**The blocked reply:** Thanks for getting in touch. Check the forwarding status page to see the last successful delivery and any error returned by the destination [1]. Verify the destination credential separately since expired credentials are the most common cause of stopped delivery [1]. If needed, resume forwarding manually after confirming the destination is healthy [1].

**Your verdict:** right block / false alarm

### DEV-0469 · integration_help · key says auto_respond

**Ticket:** Connecting our CI pipeline log forwarding to our external system stop yesterday morning and not resumed by itself. destination is healthy as we know. kindly check and revert.

**Blocked by:** {'grounding_model': "block: sentences [2, 3] not supported (The article links the two-minute delay to metrics aggregation and the level filter to high volume, neither of which addresses the customer's issue of logs stopping entirely.)"}

**The blocked reply:** Thanks for getting in touch. Check the forwarding status page to see the last successful delivery and any error returned by the destination [1]. Expect a delay of up to two minutes on metrics, as they are aggregated before being sent [1]. Apply a level filter at the source so that debug output is not forwarded, which often reduces unexpected volume [1]. Verify the destination credential separately, since expired credentials are the most common cause of stopped delivery [1].

**Your verdict:** right block / false alarm

### DEV-0472 · database_issue · key says escalate

**Ticket:** A restore we started last Friday is still running. The database is about four hundred gigabytes. Is this a normal duration or has something stalled?

**Blocked by:** {'grounding_words': 'block: sentences 3 (a number not in the article)'}

**The blocked reply:** Thanks for getting in touch. Identify the point you need to restore to [1]. Restore into a new database instance rather than over the existing one, so the current state is preserved while you verify the restore [1]. Allow roughly ten minutes per hundred gigabytes for the restore, and considerably longer where the instance is also under load [1]. Verify the restored data before switching traffic, and keep the original instance until that verification is complete [1].

**Your verdict:** right block / false alarm

### DEV-0481 · api_usage_question · key says auto_respond

**Ticket:** How do I page through large results When I page through results I am seeing some records twice and missing others entirely. The collection does change while I iterate. Am I doing this the wrong way?

**Blocked by:** {'grounding_words': 'block: sentences 3 (a number not in the article)'}

**The blocked reply:** Thanks for getting in touch. Use cursor pagination for collections that may change while iterating [1]. Pass the next_cursor value from each response as the cursor parameter of the following request, and stop when it is null [1]. Keep the page size at or below two hundred to avoid rejected requests [1]. For very large extracts, use the export endpoint, which runs asynchronously and returns a download link [1].

**Your verdict:** right block / false alarm

### DEV-0482 · api_usage_question · key says auto_respond

**Ticket:** Pagination returns duplicates Our cursor seems to stop working partway through a long iteration. Is there an expiry we should be handling?

**Blocked by:** {'grounding_words': 'block: sentences 3 (a number not in the article)'}

**The blocked reply:** Thanks for getting in touch. Use cursor pagination for any data that may change while iterating, as offset pagination can cause duplicates [1]. Pass the next_cursor value from each response as the cursor parameter of the following request and stop when it is null [1]. Keep the page size at or below two hundred; larger requests are rejected rather than truncated [1]. For very large extracts, use the export endpoint, which runs asynchronously and returns a download link [1]. Cursors expire after one hour, so long-running iterations should handle expiry by restarting from a recorded checkpoint [1].

**Your verdict:** right block / false alarm

### DEV-0485 · account_access · key says auto_respond

**Ticket:** One of our developers cannot see a project she should have access to. I have granted her the role twice and it does not seem to take effect.

**Blocked by:** {'grounding_model': "block: sentences [3] not supported (Sentence 3 adds a specific instruction to ask the user to accept the invitation, which is not explicitly stated in the article's resolution steps.)"}

**The blocked reply:** Thanks for getting in touch. Check the effective permissions view for the user, which resolves direct roles and group memberships together [1]. Confirm the invitation was accepted, as pending invitations appear in a separate section and expire after seven days [1]. If the user was invited but has not accepted, ask her to accept the invitation before the role takes effect [1]. Prefer assigning the role via group membership rather than multiple direct assignments to simplify access review [1].

**Your verdict:** right block / false alarm

### DEV-0487 · account_access · key says auto_respond

**Ticket:** One of our developers cannot see a project she should have access to. I have granted her the role twice and it does not seem to take effect.

**Blocked by:** {'grounding_model': "block: sentences [3] not supported (Sentence 3 adds a specific instruction to ask the user to accept the invitation, which is not explicitly stated in the article's resolution steps.)"}

**The blocked reply:** Thanks for getting in touch. Check the effective permissions view for the user, which resolves direct roles and group memberships together [1]. Confirm the invitation was accepted, as pending invitations appear in a separate section and expire after seven days [1]. If the user was invited but has not accepted, ask her to accept the invitation before the role takes effect [1]. Prefer assigning the role via group membership rather than multiple direct assignments to simplify access review [1].

**Your verdict:** right block / false alarm

### DEV-0490 · data_export · key says auto_respond

**Ticket:** Export job stuck Our export is missing records that were definitely created before I started the job. Is there something about how the snapshot works that I am misunderstanding?

**Blocked by:** {'grounding_model': 'block: the article does not fit the situation; sentences [2, 4] not supported (The article does not state that files are retained for seven days or that scheduled exports are delivered to object storage.)'}

**The blocked reply:** Thanks for getting in touch. Check the exports page for the job status, as large exports can take several minutes to complete [1]. If the download link has expired, request a fresh link from the exports page; the file remains available for seven days [1]. Remember that the export captures a snapshot taken when the job started, so any records created after that point are not included in the export [1]. For recurring needs, set up a scheduled export delivered to object storage instead of generating manual exports each time [1].

**Your verdict:** right block / false alarm

### DEV-0496 · onboarding · key says auto_respond

**Ticket:** Getting started with first deployment We are planning to migrate an existing application across. It currently writes uploaded files to local disk. What should we change before we move?

**Blocked by:** {'grounding_words': 'block: sentences 3 (a number not in the article)'}

**The blocked reply:** Thanks for getting in touch. Externalise any configuration that is currently read from files on disk by moving it to environment variables or secrets [1]. Identify local state such as uploaded files or session data and migrate it to object storage or the managed database before moving the application [1]. Run the new deployment in parallel with the existing one and shift a small share of traffic to it before committing fully to the move [1]. Plan the database migration separately from the application migration, as attempting both at once makes failures harder to diagnose [1].

**Your verdict:** right block / false alarm

## 2. Slip-throughs: answered although the answer key says a person

### DEV-0002 · api_key_issue · key says escalate

**Ticket:** One of our production keys started returning 401 at around yesterday morning without any change on our side. Other keys against the same account are still working.

**Answerable from articles (key):** False · **cited:** ['DOC-AUTH-004']

**Sent:** Thanks for getting in touch. Check the API keys page for the key's status and expiry [1]. Review the scopes attached to the key to ensure it has access to the endpoint being called [1]. If the key is revoked or expired, create a replacement key, deploy it, confirm traffic has moved, then revoke the old key [1].

This reply was written automatically from our help article "API key rotation and scope management" (DOC-AUTH-004). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0030 · rollback_request · key says escalate

**Ticket:** Bad release in production We shipped a release yesterday morning that has broken checkout for a portion of our customers. We need to get back to the previous version quickly. What is the fastest safe route?

**Answerable from articles (key):** False · **cited:** ['DOC-DEPLOY-002']

**Sent:** Thanks for getting in touch. Open the revisions page for the service and identify the last revision that was healthy [1]. Select roll back on that revision [1]. Traffic moves within roughly thirty seconds and no rebuild takes place [1]. If the release included a database migration, roll the migration back before the service, or the older code will encounter a schema it does not expect [1]. Record the incident and the reason for the rollback before deploying a fix while the detail is still fresh [1].

This reply was written automatically from our help article "Rolling back a failed release" (DOC-DEPLOY-002). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0031 · rate_limit · key says escalate

**Ticket:** Hitting the rate limit unexpectedly We started getting 429 responses at around two days ago. Our traffic has not increased noticeably. We have several keys, so I had assumed our limit would be higher.

**Answerable from articles (key):** False · **cited:** ['DOC-API-001']

**Sent:** Thanks for getting in touch. Read the rate limit headers returned with every response to see the exact limit, remaining allowance, and reset time [1]. Confirm whether the endpoint you are calling has a specific lower limit, such as search or export endpoints [1]. Implement exponential backoff with jitter on 429 responses instead of retrying immediately, which helps avoid prolonged throttling [1]. If you need higher sustained throughput, request a limit increase on Business or Enterprise plans through an account request [1].

This reply was written automatically from our help article "Understanding API rate limits and quota tiers" (DOC-API-001). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0032 · database_issue · key says escalate

**Ticket:** Connection pool exhausted We are getting errors saying no connection is available. This started when we scaled up our service. The database itself shows very few active queries.

**Answerable from articles (key):** False · **cited:** ['DOC-PERF-003']

**Sent:** Thanks for getting in touch. Calculate the total possible connections as pool size multiplied by maximum instances and compare it against your plan's connection limit [1]. Reduce the per-instance pool size rather than raising the limit [1]. Look for queries that hold a transaction open across a network call to another service, which is the most common cause of leaks of this kind [1]. Consider a connection proxy if the instance count must remain high, so that pooling happens once rather than per instance [1].

This reply was written automatically from our help article "Database connection pool exhaustion" (DOC-PERF-003). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0038 · integration_help · key says escalate

**Ticket:** Monitoring integration setup Log forwarding to our external system stopped late last night and has not resumed by itself. The destination is healthy as far as we can tell.

**Answerable from articles (key):** False · **cited:** ['DOC-INT-002']

**Sent:** Thanks for getting in touch. Check the forwarding status page to see the last successful delivery and any error returned by the destination [1]. Verify the destination credential separately, as expired credentials are the most common cause of delivery stopping [1]. If the forwarding has paused after an hour of consecutive failures, resume it manually once the destination is healthy [1].

This reply was written automatically from our help article "Third party monitoring and log forwarding" (DOC-INT-002). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0039 · configuration_help · key says escalate

**Ticket:** Config differs between environments Where should secrets be stored so they do not appear in the logs? At the moment ours are being printed at startup and I am not comfortable with that.

**Answerable from articles (key):** False · **cited:** ['DOC-DEPLOY-004']

**Sent:** Thanks for getting in touch. Store any sensitive data as a secret rather than a variable so it is masked in logs and not readable through the API after creation [1]. Check that the secret is defined at the correct scope; service scope overrides project scope, and project scope overrides organisation defaults [1]. Review the environment overrides page to ensure no overrides are exposing the secret value [1]. Redeploy the service after making these changes so the new configuration takes effect [1].

This reply was written automatically from our help article "Configuring environment variables and secrets" (DOC-DEPLOY-004). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0040 · rollback_request · key says escalate

**Ticket:** How do I revert to an earlier revision? The release we put out this morning is causing errors and I would rather roll back than try to fix forward.

**Answerable from articles (key):** False · **cited:** ['DOC-DEPLOY-002']

**Sent:** Thanks for getting in touch. Open the revisions page for the service and identify the last revision that was healthy [1]. Select roll back on that revision [1]. Traffic moves within roughly thirty seconds and no rebuild takes place [1]. If the release included a database migration, roll the migration back before the service, or the older code will encounter a schema it does not expect [1]. Record the incident and the reason for the rollback before deploying a fix while the detail is still fresh [1].

This reply was written automatically from our help article "Rolling back a failed release" (DOC-DEPLOY-002). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0042 · rollback_request · key says escalate

**Ticket:** Need to roll back the latest release How do I revert to an earlier revision? The release we put out this morning is causing errors and I would rather roll back than try to fix forward.

**Answerable from articles (key):** False · **cited:** ['DOC-DEPLOY-002']

**Sent:** Thanks for getting in touch. Open the revisions page for the service and identify the last revision that was healthy [1]. Select roll back on that revision [1]. Traffic moves within roughly thirty seconds and no rebuild takes place [1]. If the release included a database migration, roll the migration back before the service, or the older code will encounter a schema it does not expect [1]. Record the incident and the reason for the rollback before deploying a fix, while the detail is still fresh [1].

This reply was written automatically from our help article "Rolling back a failed release" (DOC-DEPLOY-002). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0057 · integration_help · key says escalate

**Ticket:** Connecting our CI pipeline we are connecting our CI pipeline and not are sure whether to use personal key or something else. What the recommended approach for automation? please do the needful.

**Answerable from articles (key):** False · **cited:** ['DOC-INT-001']

**Sent:** Thanks for getting in touch. Create a service account for the pipeline instead of using a personal key [1]. Grant the service account only the projects and permissions the pipeline needs, and review that grant when the pipeline changes [1]. Store the credential as an encrypted secret in your pipeline provider, never in the repository [1]. Test the pipeline credential separately from the deployment logic, so that authentication failures are distinguishable from deployment failures [1].

This reply was written automatically from our help article "Connecting continuous integration pipelines" (DOC-INT-001). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0064 · quota_or_overage · key says escalate

**Ticket:** Unexpected overage charges Our spend cap stopped a production workload overnight. We need it raised immediately and then we need to reconsider how we have this configured.

**Answerable from articles (key):** False · **cited:** ['DOC-BILL-003']

**Sent:** Thanks for getting in touch. Check the current period usage against the plan allowance on the billing page [1]. Decide deliberately between a hard spend cap, which stops the service, and overage, which continues at the listed rate [1]. Configure alerts at fifty, eighty and ninety-five per cent of allowance rather than relying on the cap as a warning [1]. Raise the spend cap immediately from the billing page; the service will resume within a minute [1].

This reply was written automatically from our help article "Usage limits, overage and spend controls" (DOC-BILL-003). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0067 · webhook_issue · key says escalate

**Ticket:** Signature verification failing signature verification fails for every delivery. We are computing signature exactly as the documentation describes, over parsed body.

**Answerable from articles (key):** False · **cited:** ['DOC-API-003']

**Sent:** Thanks for getting in touch. Check the webhook delivery log to see the response status and body for each attempt [1]. Ensure your endpoint returns a 2xx status quickly and processes the event asynchronously, as deliveries time out after five seconds [1]. Compute the signature over the raw request body before any parsing; parsing changes the bytes and invalidates the signature [1]. Make your handler idempotent using the event identifier, since at-least-once delivery can cause duplicates [1].

This reply was written automatically from our help article "Webhook delivery, retries and signature verification" (DOC-API-003). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0070 · database_issue · key says escalate

**Ticket:** Connection pool exhausted We are getting errors saying no connection is available. This started when we scaled up our service. The database itself shows very few active queries.

**Answerable from articles (key):** False · **cited:** ['DOC-PERF-003']

**Sent:** Thanks for getting in touch. Calculate the total possible connections as pool size multiplied by maximum instances and compare it against your plan's connection limit [1]. Reduce the per-instance pool size rather than raising the limit [1]. Look for queries that hold a transaction open across a network call to another service, which is the most common cause of leaks of this kind [1]. Consider a connection proxy if the instance count must remain high, so that pooling happens once rather than per instance [1].

This reply was written automatically from our help article "Database connection pool exhaustion" (DOC-PERF-003). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0076 · sso_configuration · key says escalate

**Ticket:** SAML login returns an error page Single sign-on works for our engineering group but the finance group gets an error. Both are configured identically as far as we can tell. Any idea what differs?

**Answerable from articles (key):** False · **cited:** ['DOC-AUTH-003']

**Sent:** Thanks for getting in touch. Compare the assertion consumer service URL in your identity provider against the value shown on the SSO settings page; they must match exactly, including the trailing path [1]. Inspect a failing assertion and confirm the NameID is the user's email address in lower case [1]. Enable just-in-time provisioning if new users should be created on first login, and set a default role for provisioned users [1]. Keep at least one administrator account with password access while testing, so a misconfiguration does not lock the whole organisation out [1].

This reply was written automatically from our help article "Single sign-on configuration with SAML providers" (DOC-AUTH-003). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0082 · configuration_help · key says escalate

**Ticket:** Config differs between environments our staging environment is picking up production configuration values. I not able to work out where override is coming from.

**Answerable from articles (key):** False · **cited:** ['DOC-DEPLOY-004']

**Sent:** Thanks for getting in touch. Check the scope at which the variable was defined, as service scope overrides project scope and project scope overrides organisation defaults [1]. Review the environment overrides page, which lists values that differ from the defaults for each environment [1]. Redeploy after changing configuration, because running containers do not pick up new values without a restart [1].

This reply was written automatically from our help article "Configuring environment variables and secrets" (DOC-DEPLOY-004). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0086 · deployment_failure · key says escalate

**Ticket:** Deployment rolls back every time Every deployment fails at the health check stage. I have increased the timeout twice already and it makes no difference.

**Answerable from articles (key):** False · **cited:** ['DOC-DEPLOY-001']

**Sent:** Thanks for getting in touch. Confirm the container is listening on the port declared in the service definition [1]. Increase the initial delay if the application needs time to warm up before it can answer; thirty seconds is a reasonable starting point [1]. Compare the environment variables present in the deployment against those the application requires; missing configuration frequently causes a silent startup failure [1]. Inspect the container logs from the failed revision rather than the running one; the rollback replaces the logs shown by default [1].

This reply was written automatically from our help article "Container deployments failing during the health check phase" (DOC-DEPLOY-001). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0087 · data_export · key says escalate

**Ticket:** Export job stuck The download link from our export has expired and I cannot find a way to generate a new one. Is the file still available?

**Answerable from articles (key):** False · **cited:** ['DOC-DATA-001']

**Sent:** Thanks for getting in touch. Check the exports page to see the current status of the job [1]. If the original download link has expired, request a fresh link from the exports page [1]. The underlying file is retained for seven days after the job completes [1]. For future needs, consider setting up a scheduled export that delivers the file to object storage instead of generating it manually [1].

This reply was written automatically from our help article "Exporting account data and scheduled extracts" (DOC-DATA-001). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0089 · performance_degradation · key says escalate

**Ticket:** Service slow at peak hours The service is noticeably slow during our afternoon peak and fine the rest of the day. We have autoscaling enabled so I expected it to cope.

**Answerable from articles (key):** False · **cited:** ['DOC-PERF-001', 'DOC-PERF-002']

**Sent:** Thanks for getting in touch. Compare the median and 95th percentile latency on the metrics page to see if a large gap indicates contention or queueing [1]. Check memory utilisation across instances; sustained utilisation above eighty percent typically shows up as latency before failure [1]. Review the dependency timing breakdown on the trace view to determine if the delay is in your service or a downstream dependency [1]. Verify that the service is not at its configured maximum instance count, which would stop scaling regardless of load [2]. Choose a scaling metric that reflects the pressure you actually face, such as request concurrency for request-bound services [2]. Set the cooldown period longer than your startup time so new instances are counted before another scaling decision is taken [2]. Set a minimum instance count above zero for latency-sensitive services to avoid cold starts on the first request [2].

This reply was written automatically from our help article "Diagnosing elevated response latency" (DOC-PERF-001). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0095 · performance_degradation · key says escalate

**Ticket:** Response times have doubled service not isiceably slow during our afternoon peak and fine rest of the day. we having autoscaling enabled so I expect it to cope. please tell what to do.

**Answerable from articles (key):** True · **cited:** ['DOC-PERF-001', 'DOC-PERF-002']

**Sent:** Thanks for getting in touch. Compare the median and 95th percentile latency on the metrics page to see if a large gap indicates contention or queueing [1]. Check memory utilisation across instances; sustained utilisation above eighty percent typically shows up as latency before failure [1]. Review the dependency timing breakdown on the trace view to identify whether the delay is in your service or a downstream dependency [1]. Check whether the service is sitting at its configured maximum instance count; scaling stops there regardless of load [2]. Choose a scaling metric that reflects the pressure you actually face, such as request concurrency for request-bound services [2]. Set the cooldown longer than your startup time so that new instances are counted before another scaling decision is taken [2]. Set a minimum instance count above zero for latency-sensitive services to avoid cold starts on the first request [2].

This reply was written automatically from our help article "Diagnosing elevated response latency" (DOC-PERF-001). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0101 · configuration_help · key says escalate

**Ticket:** Config differs between environments i am having set environment variable but application not able to see it. i am having checked spelling several times. please tell what to do.

**Answerable from articles (key):** False · **cited:** ['DOC-DEPLOY-004']

**Sent:** Thanks for getting in touch. Check the scope at which the variable was defined; service scope overrides project scope, and project scope overrides organisation defaults [1]. Store sensitive values as a secret instead of a variable to keep them masked in logs and unreadable via the API [1]. Review the environment overrides page to see values that differ from the defaults for each environment [1]. Redeploy after changing the configuration, as running containers do not pick up new values without a restart [1].

This reply was written automatically from our help article "Configuring environment variables and secrets" (DOC-DEPLOY-004). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0105 · webhook_issue · key says escalate

**Ticket:** Duplicate webhook deliveries Our webhook endpoint has stopped receiving events since last Friday. The endpoint is up and responding to health checks from our own monitoring.

**Answerable from articles (key):** False · **cited:** ['DOC-API-003']

**Sent:** Thanks for getting in touch. Check the webhook delivery log to see the status and body of each attempt for the last seven days [1]. Ensure your endpoint returns a 2xx status quickly and processes the event asynchronously, as deliveries time out after five seconds [1]. Compute the signature over the raw request body before any parsing, because re-serialising JSON changes the bytes and invalidates the signature [1]. Make your handler idempotent using the event identifier, since at-least-once delivery means duplicates are expected [1].

This reply was written automatically from our help article "Webhook delivery, retries and signature verification" (DOC-API-003). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0108 · deployment_failure · key says escalate

**Ticket:** Every deployment fails at the health check stage. I have increased the timeout twice already and it makes no difference.

**Answerable from articles (key):** False · **cited:** ['DOC-DEPLOY-001']

**Sent:** Thanks for getting in touch. Confirm the container is listening on the port declared in the service definition [1]. Increase the initial delay if the application needs time to warm up before it can answer [1]. Compare the environment variables present in the deployment against those the application requires [1]. Inspect the container logs from the failed revision rather than the running one; the rollback replaces the logs shown by default [1].

This reply was written automatically from our help article "Container deployments failing during the health check phase" (DOC-DEPLOY-001). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0115 · database_issue · key says escalate

**Ticket:** No connections available error We are getting errors saying no connection is available. This started when we scaled up our service. The database itself shows very few active queries.

**Answerable from articles (key):** True · **cited:** ['DOC-PERF-003']

**Sent:** Thanks for getting in touch. Calculate the total possible connections as pool size multiplied by maximum instances and compare it against your plan's connection limit [1]. Reduce the per-instance pool size rather than raising the limit, as a large number of small pools is usually the wrong shape for a scaled service [1]. Look for queries that hold a transaction open across a network call to another service, which is the most common cause of leaks of this kind [1]. Consider a connection proxy if the instance count must remain high, so that pooling happens once rather than per instance [1].

This reply was written automatically from our help article "Database connection pool exhaustion" (DOC-PERF-003). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0119 · api_key_issue · key says escalate

**Ticket:** A key can read fine but every write returns a permission error. I created it myself and I thought I gave it full access.

**Answerable from articles (key):** False · **cited:** ['DOC-AUTH-004']

**Sent:** Thanks for getting in touch. Check the API keys page for the key's status and expiry [1]. Review the scopes attached to the key to ensure it has write permissions and is not limited to read-only [1]. If the key is project-scoped, confirm it has access to the organization endpoints you are trying to write to [1].

This reply was written automatically from our help article "API key rotation and scope management" (DOC-AUTH-004). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0128 · database_issue · key says escalate

**Ticket:** Our connection pool appears to be exhausting under moderate load. We have already increased the pool size and it made things worse.

**Answerable from articles (key):** False · **cited:** ['DOC-PERF-003']

**Sent:** Thanks for getting in touch. Calculate the total possible connections as pool size multiplied by maximum instances and compare it against your plan's connection limit [1]. Reduce the per-instance pool size rather than raising the limit, as a large number of small pools is usually the wrong shape for a scaled service [1]. Look for queries that hold a transaction open across a network call to another service, which is the most common cause of leaks of this kind [1]. Consider a connection proxy if the instance count must remain high, so that pooling happens once rather than per instance [1].

This reply was written automatically from our help article "Database connection pool exhaustion" (DOC-PERF-003). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0133 · authentication_failure · key says escalate

**Ticket:** MFA code keeps getting rejected I have been trying to sign in for the last about a week and keep getting an invalid credentials message. I am certain the password is correct because I use a password manager. Nothing has changed at our end that I am aware of.

**Answerable from articles (key):** False · **cited:** ['DOC-AUTH-002']

**Sent:** Thanks for getting in touch. Check that automatic time synchronization is enabled on the device generating the MFA code [1]. If the device is lost, sign in with one of your recovery codes and then re-enrol a new device from the security page [1]. If no recovery codes are available, an account administrator can reset multi-factor authentication for the user from the team members page [1]. If you are the sole administrator and have no recovery codes, identity verification through support is required and takes up to one business day [1].

This reply was written automatically from our help article "Multi-factor authentication setup and recovery" (DOC-AUTH-002). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0136 · configuration_help · key says escalate

**Ticket:** Config differs between environments I have set an environment variable but the application cannot see it. I have checked the spelling several times. Is there a scope I might be getting wrong?

**Answerable from articles (key):** False · **cited:** ['DOC-DEPLOY-004']

**Sent:** Thanks for getting in touch. Check the scope at which the variable was defined, ensuring that service scope does not override project scope [1]. If the value is sensitive, store it as a secret so it is masked in logs and not readable through the API [1]. Review the environment overrides page to confirm no hidden overrides are changing the value for that environment [1]. Redeploy the service after making any configuration changes so the running containers pick up the new value [1].

This reply was written automatically from our help article "Configuring environment variables and secrets" (DOC-DEPLOY-004). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0137 · database_issue · key says escalate

**Ticket:** Database restore taking hours We are getting errors saying no connection is available. This started when we scaled up our service. The database itself shows very few active queries.

**Answerable from articles (key):** True · **cited:** ['DOC-PERF-003']

**Sent:** Thanks for getting in touch. Calculate the total possible connections as pool size multiplied by maximum instances, and compare it against your plan's connection limit [1]. Reduce the per-instance pool size rather than raising the limit [1]. Look for queries that hold a transaction open across a network call to another service, as this is the most common cause of leaks [1]. Consider using a connection proxy if the instance count must remain high, so that pooling happens once rather than per instance [1].

This reply was written automatically from our help article "Database connection pool exhaustion" (DOC-PERF-003). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0138 · quota_or_overage · key says escalate

**Ticket:** Unexpected overage charges Our spend cap stopped a production workload overnight. We need it raised immediately and then we need to reconsider how we have this configured.

**Answerable from articles (key):** False · **cited:** ['DOC-BILL-003']

**Sent:** Thanks for getting in touch. Check the current period usage against the plan allowance on the billing page [1]. Decide deliberately between a hard spend cap, which stops the service, and overage, which continues at the listed rate [1]. Configure alerts at fifty, eighty and ninety-five per cent of allowance rather than relying on the cap as a warning [1]. Raise the spend cap immediately from the billing page; the service will resume within a minute [1].

This reply was written automatically from our help article "Usage limits, overage and spend controls" (DOC-BILL-003). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0147 · configuration_help · key says escalate

**Ticket:** Where do I set secrets Where should secrets be stored so they do not appear in the logs? At the moment ours are being printed at startup and I am not comfortable with that.

**Answerable from articles (key):** False · **cited:** ['DOC-DEPLOY-004']

**Sent:** Thanks for getting in touch. Store sensitive values as secrets rather than variables so they are masked in logs and not readable through the API after creation [1]. Check the scope at which the secret was defined; service scope overrides project scope, and project scope overrides organisation defaults [1]. Review the environment overrides page to ensure no overrides are exposing the secret value [1]. Redeploy the service after changing the configuration so that running containers pick up the new secret values [1].

This reply was written automatically from our help article "Configuring environment variables and secrets" (DOC-DEPLOY-004). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0149 · authentication_failure · key says escalate

**Ticket:** Locked out of my account i cannot login since last Friday. password is correct i am sure. please help fast, it is blocking my work.

**Answerable from articles (key):** False · **cited:** ['DOC-AUTH-001']

**Sent:** Thanks for getting in touch. Check the security page of the console to see if the account is locked; a red banner indicates a lock that will release automatically after thirty minutes [1]. Clear cookies for the CloudServe domain or open a private browsing window, then try logging in again [1]. If using the CLI, run `cloudserve auth logout` followed by `cloudserve auth login` to discard any cached token [1]. If the account remains locked and immediate access is needed, an administrator can release the lock from the team members page [1].

This reply was written automatically from our help article "Resolving invalid credential errors on login" (DOC-AUTH-001). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0180 · authentication_failure · key says escalate

**Ticket:** I have been trying to sign in for the last a couple of days and keep getting an invalid credentials message. I am certain the password is correct because I use a password manager. Nothing has changed at our end that I am aware of.

**Answerable from articles (key):** False · **cited:** ['DOC-AUTH-001']

**Sent:** Thanks for getting in touch. Check if the account is locked by visiting the security page of the console; a locked account shows a red banner and unlocks automatically after thirty minutes [1]. Clear the CloudServe domain cookies or open a private browsing window, then try logging in again [1]. If using the CLI, run `cloudserve auth logout` followed by `cloudserve auth login` to discard any cached token [1].

This reply was written automatically from our help article "Resolving invalid credential errors on login" (DOC-AUTH-001). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0186 · performance_degradation · key says escalate

**Ticket:** p95 latency is very high Latency has been climbing gradually over the past most of the morning. Nothing in our code has changed. Memory usage looks high but not at the limit.

**Answerable from articles (key):** True · **cited:** ['DOC-PERF-001']

**Sent:** Thanks for getting in touch. Compare the median and 95th percentile latency on the metrics page to see if a large gap indicates contention or queueing [1]. Check memory utilisation across instances; sustained utilisation above eighty percent typically shows up as latency before failure [1]. Review the dependency timing breakdown on the trace view to determine if the delay is in your service or a downstream dependency [1]. Adjust the autoscaling policy if the load is predictable, using request count scaling rather than processor utilisation [1].

This reply was written automatically from our help article "Diagnosing elevated response latency" (DOC-PERF-001). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0204 · performance_degradation · key says escalate

**Ticket:** Latency has been climbing gradually over the past a couple of days. Nothing in our code has changed. Memory usage looks high but not at the limit.

**Answerable from articles (key):** False · **cited:** ['DOC-PERF-001']

**Sent:** Thanks for getting in touch. Compare the median and 95th percentile latency on the metrics page to see if a large gap indicates contention or queueing [1]. Check memory utilisation across instances; sustained utilisation above eighty percent typically shows up as latency before failure [1]. Review the dependency timing breakdown on the trace view to determine if the delay is in your service or a downstream dependency [1]. Adjust the autoscaling policy if the load is predictable, using request count rather than processor utilisation to respond sooner [1].

This reply was written automatically from our help article "Diagnosing elevated response latency" (DOC-PERF-001). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0220 · sso_configuration · key says escalate

**Ticket:** We are setting up SAML with our identity provider and users are being bounced back to an error page after authenticating successfully on our side. The assertion looks correct to us.

**Answerable from articles (key):** False · **cited:** ['DOC-AUTH-003']

**Sent:** Thanks for getting in touch. Compare the assertion consumer service URL in your identity provider against the value shown on the SSO settings page; they must match exactly, including the trailing path [1]. Inspect a failing assertion and confirm that the NameID is the user's email address in lower case [1]. Enable just-in-time provisioning if new users should be created on first login, and set a default role for provisioned users [1]. Keep at least one administrator account with password access while testing, so a misconfiguration does not lock the whole organisation out [1].

This reply was written automatically from our help article "Single sign-on configuration with SAML providers" (DOC-AUTH-003). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0225 · performance_degradation · key says escalate

**Ticket:** Service slow at peak hours Our response times have roughly doubled since last Friday with no deployment on our side. The median looks acceptable but the 95th percentile is far worse than it was.

**Answerable from articles (key):** True · **cited:** ['DOC-PERF-001']

**Sent:** Thanks for getting in touch. Compare the median and 95th percentile latency on the metrics page to confirm a large gap indicating contention or queueing [1]. Check memory utilisation across instances; sustained utilisation above eighty percent typically shows up as latency before failure [1]. Review the dependency timing breakdown on the trace view to identify whether the delay is in your service or a downstream dependency [1]. Adjust the autoscaling policy if the load is predictable, scaling on request count rather than processor utilisation to respond sooner [1].

This reply was written automatically from our help article "Diagnosing elevated response latency" (DOC-PERF-001). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0232 · webhook_issue · key says escalate

**Ticket:** Duplicate webhook deliveries we are receiving same event several times. Is this expect behaviour or is something wrong with our configuration? waiting for your reply.

**Answerable from articles (key):** False · **cited:** ['DOC-API-003']

**Sent:** Thanks for getting in touch. Check the webhook delivery log to see each attempt and its response status [1]. Return a 2xx status quickly and process the event asynchronously to avoid timeouts [1]. Compute the signature over the raw request body before any parsing to ensure verification succeeds [1]. Make your handler idempotent using the event identifier, as at-least-once delivery means duplicates are expected [1].

This reply was written automatically from our help article "Webhook delivery, retries and signature verification" (DOC-API-003). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0236 · deployment_failure · key says escalate

**Ticket:** Health check keeps timing out Builds that worked last week are now failing during dependency resolution. We have not changed our code at all. This is blocking a release we had planned for over the weekend.

**Answerable from articles (key):** False · **cited:** ['DOC-DEPLOY-001', 'DOC-DEPLOY-003']

**Sent:** Thanks for getting in touch. Confirm the container is listening on the port declared in the service definition, as a mismatch can cause health check timeouts [1]. Increase the initial delay to give the application time to warm up before it can answer the health check; thirty seconds is a reasonable starting point [1]. Compare the environment variables present in the deployment against those the application requires, because missing configuration frequently causes a silent startup failure [1]. Inspect the container logs from the failed revision rather than the running one, since the rollback replaces the logs shown by default [1]. Pin your dependencies with exact versions and commit the lock file, as unpinned dependencies are the most common cause of build failures after a dependency release [2]. Compare the runtime version declared in your build configuration against the version you use locally to ensure consistency [2]. Clear the build cache from the settings page and trigger a fresh build to rule out a corrupted artefact [2]. If a specific dependency is failing to resolve, check whether its registry is reachable from the build network [2].

This reply was written automatically from our help article "Container deployments failing during the health check phase" (DOC-DEPLOY-001). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0239 · quota_or_overage · key says escalate

**Ticket:** Spend cap stopped our service We were throttled yesterday morning after a traffic increase and it took down part of our product. We would rather pay overage than be stopped. How do we change that?

**Answerable from articles (key):** False · **cited:** ['DOC-BILL-003']

**Sent:** Thanks for getting in touch. Check the current period usage against the plan allowance on the billing page [1]. Decide deliberately between a hard spend cap, which stops the service, and overage, which continues at the listed rate [1]. Configure alerts at fifty, eighty and ninety-five per cent of allowance rather than relying on the cap as a warning [1]. If a cap has stopped a production service, an account owner can raise it immediately from the billing page and the service resumes within a minute [1].

This reply was written automatically from our help article "Usage limits, overage and spend controls" (DOC-BILL-003). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0241 · performance_degradation · key says escalate

**Ticket:** Response times have doubled Latency has been climbing gradually over the past most of the morning. Nothing in our code has changed. Memory usage looks high but not at the limit.

**Answerable from articles (key):** False · **cited:** ['DOC-PERF-001']

**Sent:** Thanks for getting in touch. Compare the median and 95th percentile latency on the metrics page to see if a large gap indicates contention or queueing [1]. Check memory utilisation across instances; sustained utilisation above eighty percent typically shows up as latency before failure [1]. Review the dependency timing breakdown on the trace view to identify whether the delay is in your service or a downstream dependency [1]. Adjust the autoscaling policy if the load is predictable, scaling on request count rather than processor utilisation to respond sooner [1].

This reply was written automatically from our help article "Diagnosing elevated response latency" (DOC-PERF-001). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0266 · account_access · key says escalate

**Ticket:** Permission changes not taking effect One of our developers cannot see a project she should have access to. I have granted her the role twice and it does not seem to take effect.

**Answerable from articles (key):** False · **cited:** ['DOC-ACCT-001']

**Sent:** Thanks for getting in touch. Check the effective permissions view for the developer, which resolves direct roles and group memberships together [1]. Confirm the invitation was accepted, as pending invitations appear in a separate section and expire after seven days [1].

This reply was written automatically from our help article "Managing team members, roles and permissions" (DOC-ACCT-001). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0267 · performance_degradation · key says escalate

**Ticket:** Latency has been climbing gradually over the past several hours. Nothing in our code has changed. Memory usage looks high but not at the limit.

**Answerable from articles (key):** True · **cited:** ['DOC-PERF-001']

**Sent:** Thanks for getting in touch. Compare the median and 95th percentile latency on the metrics page to see if there is a large gap indicating contention or queueing [1]. Check memory utilisation across instances, noting that sustained utilisation above eighty per cent can cause latency before failures appear [1]. Review the dependency timing breakdown on the trace view to determine whether time is spent in your service or waiting on a downstream dependency [1]. Adjust the autoscaling policy if the load pattern is predictable, using scaling on request count rather than processor utilisation for faster response [1].

This reply was written automatically from our help article "Diagnosing elevated response latency" (DOC-PERF-001). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0272 · deployment_failure · key says escalate

**Ticket:** Every deployment fails at the health check stage. I have increased the timeout twice already and it makes no difference.

**Answerable from articles (key):** False · **cited:** ['DOC-DEPLOY-001']

**Sent:** Thanks for getting in touch. Confirm the container is listening on the port declared in the service definition [1]. Increase the initial delay if the application needs time to warm up before it can answer, using a reasonable starting point such as thirty seconds [1]. Compare the environment variables present in the deployment against those the application requires and add any missing configuration [1]. Inspect the container logs from the failed revision rather than the running one to see the original failure details [1].

This reply was written automatically from our help article "Container deployments failing during the health check phase" (DOC-DEPLOY-001). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0274 · performance_degradation · key says escalate

**Ticket:** Service slow at peak hours Latency has been climbing gradually over the past most of the morning. Nothing in our code has changed. Memory usage looks high but not at the limit.

**Answerable from articles (key):** True · **cited:** ['DOC-PERF-001']

**Sent:** Thanks for getting in touch. Compare the median and 95th percentile latency on the metrics page to see if a large gap indicates contention or queueing [1]. Check memory utilisation across instances; sustained utilisation above eighty percent typically shows up as latency before failure [1]. Review the dependency timing breakdown on the trace view to identify whether the delay is in your service or a downstream dependency [1]. Adjust the autoscaling policy if the load is predictable, scaling on request count rather than processor utilisation [1].

This reply was written automatically from our help article "Diagnosing elevated response latency" (DOC-PERF-001). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0277 · database_issue · key says escalate

**Ticket:** Our connection pool appears to be exhausting under moderate load. We have already increased the pool size and it made things worse.

**Answerable from articles (key):** True · **cited:** ['DOC-PERF-003']

**Sent:** Thanks for getting in touch. Calculate the total possible connections as pool size multiplied by maximum instances and compare it against your plan's connection limit [1]. Reduce the per-instance pool size rather than raising the limit, as a large number of small pools is usually the wrong shape for a scaled service [1]. Look for queries that hold a transaction open across a network call to another service, which is the most common cause of leaks of this kind [1]. Consider a connection proxy if the instance count must remain high, so that pooling happens once rather than per instance [1].

This reply was written automatically from our help article "Database connection pool exhaustion" (DOC-PERF-003). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0280 · deployment_failure · key says escalate

**Ticket:** Build fails in the pipeline Our deployment reaches running and then rolls back after about a minute. The logs mention a health check timeout. It runs perfectly on my machine and in staging.

**Answerable from articles (key):** False · **cited:** ['DOC-DEPLOY-001']

**Sent:** Thanks for getting in touch. Confirm the container is listening on the port declared in the service definition [2]. Increase the initial delay if the application needs time to warm up before it can answer, using thirty seconds as a starting point [2]. Compare the environment variables present in the deployment against those the application requires [2]. Inspect the container logs from the failed revision rather than the running one to see the health check failure details [2].

This reply was written automatically from our help article "Container deployments failing during the health check phase" (DOC-DEPLOY-001). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0283 · configuration_help · key says escalate

**Ticket:** Environment variable not being read Our staging environment is picking up production configuration values. I cannot work out where the override is coming from.

**Answerable from articles (key):** False · **cited:** ['DOC-DEPLOY-004']

**Sent:** Thanks for getting in touch. Check the scope at which the variable was defined; service scope overrides project scope, and project scope overrides organisation defaults [1]. Review the environment overrides page, which lists values that differ from the defaults for each environment [1]. Redeploy after changing configuration, as running containers do not pick up new values without a restart [1].

This reply was written automatically from our help article "Configuring environment variables and secrets" (DOC-DEPLOY-004). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0286 · performance_degradation · key says escalate

**Ticket:** Latency has been climbing gradually over the past a couple of days. Nothing in our code has changed. Memory usage looks high but not at the limit.

**Answerable from articles (key):** True · **cited:** ['DOC-PERF-001']

**Sent:** Thanks for getting in touch. Compare the median and 95th percentile latency on the metrics page to see if a large gap indicates contention or queueing [1]. Check memory utilisation across instances; sustained utilisation above eighty percent typically shows up as latency before failure [1]. Review the dependency timing breakdown on the trace view to determine if the delay is in your service or a downstream dependency [1]. Adjust the autoscaling policy if the load is predictable, using request count rather than processor utilisation to respond sooner [1].

This reply was written automatically from our help article "Diagnosing elevated response latency" (DOC-PERF-001). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0287 · integration_help · key says escalate

**Ticket:** Connecting our CI pipeline We are connecting our CI pipeline and are not sure whether to use a personal key or something else. What is the recommended approach for automation?

**Answerable from articles (key):** False · **cited:** ['DOC-INT-001']

**Sent:** Thanks for getting in touch. Create a service account for the pipeline rather than using a personal key, so that access survives staff changes [1]. Grant the service account only the projects and permissions the pipeline needs, and review that grant when the pipeline changes [1]. Store the credential as an encrypted secret in your pipeline provider, never in the repository [1]. Test the pipeline credential separately from the deployment logic, so that authentication failures are distinguishable from deployment failures [1].

This reply was written automatically from our help article "Connecting continuous integration pipelines" (DOC-INT-001). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0291 · webhook_issue · key says escalate

**Ticket:** Webhooks not arriving We are receiving the same event several times. Is this expected behaviour or is something wrong with our configuration?

**Answerable from articles (key):** False · **cited:** ['DOC-API-003']

**Sent:** Thanks for getting in touch. Check the webhook delivery log to see each attempt and its response status and body for the last seven days [1]. Ensure your endpoint returns a 2xx status as quickly as possible and processes the event asynchronously, because deliveries time out after five seconds [1]. Compute the signature over the raw request body before any parsing; re-serialising JSON changes the bytes and invalidates the signature [1]. Make your handler idempotent using the event identifier, as at-least-once delivery means duplicates are expected rather than exceptional [1].

This reply was written automatically from our help article "Webhook delivery, retries and signature verification" (DOC-API-003). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0303 · api_key_issue · key says escalate

**Ticket:** one of our production keys start returning 401 at around two days ago without any change on our side. Other keys against same account are still working. kindly check and revert.

**Answerable from articles (key):** False · **cited:** ['DOC-AUTH-004']

**Sent:** Thanks for getting in touch. Check the API keys page for the key's status and expiry; revoked or expired keys will be listed with the date and the user who acted [1]. Review the scopes attached to the key; ensure it includes the endpoints you are calling [1]. If the key is still valid but needs replacement, create a new key, deploy it, confirm traffic has moved, then revoke the old key [1]. If the key was exposed, revoke it immediately rather than waiting for a rotation window [1].

This reply was written automatically from our help article "API key rotation and scope management" (DOC-AUTH-004). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0322 · database_issue · key says escalate

**Ticket:** We are getting errors saying no connection is available. This started when we scaled up our service. The database itself shows very few active queries.

**Answerable from articles (key):** True · **cited:** ['DOC-PERF-003']

**Sent:** Thanks for getting in touch. Calculate the total possible connections as pool size multiplied by maximum instances, and compare it against your plan's connection limit [1]. Reduce the per-instance pool size rather than raising the limit [1]. Look for queries that hold a transaction open across a network call to another service, which is the most common cause of leaks of this kind [1]. Consider a connection proxy if the instance count must remain high, so that pooling happens once rather than per instance [1].

This reply was written automatically from our help article "Database connection pool exhaustion" (DOC-PERF-003). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0325 · integration_help · key says escalate

**Ticket:** Connecting our CI pipeline Metrics arriving in our monitoring system lag behind what the console shows by a couple of minutes. Is that expected?

**Answerable from articles (key):** False · **cited:** ['DOC-INT-002']

**Sent:** Thanks for getting in touch. Check the forwarding status page to see the last successful delivery and any errors returned by the destination [1]. Expect a delay of up to two minutes on metrics, as they are aggregated before being sent [1].

This reply was written automatically from our help article "Third party monitoring and log forwarding" (DOC-INT-002). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0330 · database_issue · key says escalate

**Ticket:** No connections available error Our connection pool appears to be exhausting under moderate load. We have already increased the pool size and it made things worse.

**Answerable from articles (key):** True · **cited:** ['DOC-PERF-003']

**Sent:** Thanks for getting in touch. Calculate the total possible connections as pool size multiplied by maximum instances and compare it against your plan's connection limit [1]. Reduce the per-instance pool size rather than raising the limit, as many small pools are usually the wrong shape for a scaled service [1]. Look for queries that hold a transaction open across a network call to another service, which is the most common cause of leaks of this kind [1]. Consider using a connection proxy if the instance count must remain high so that pooling happens once rather than per instance [1].

This reply was written automatically from our help article "Database connection pool exhaustion" (DOC-PERF-003). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0339 · rollback_request · key says escalate

**Ticket:** Need to roll back the latest release How do I revert to an earlier revision? The release we put out this morning is causing errors and I would rather roll back than try to fix forward.

**Answerable from articles (key):** False · **cited:** ['DOC-DEPLOY-002']

**Sent:** Thanks for getting in touch. Open the revisions page for the service and identify the last revision that was healthy [1]. Select roll back on that revision; traffic moves within roughly thirty seconds and no rebuild takes place [1]. If the release included a database migration, roll the migration back before the service, or the older code will encounter a schema it does not expect [1]. Record the incident and the reason for the rollback before deploying a fix, while the detail is still fresh [1].

This reply was written automatically from our help article "Rolling back a failed release" (DOC-DEPLOY-002). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0342 · rollback_request · key says escalate

**Ticket:** Bad release in production how do I revert to earlier revision? The release we put out this morning causing errors and I better i roll back than try to fix forward. please help fast.

**Answerable from articles (key):** False · **cited:** ['DOC-DEPLOY-002']

**Sent:** Thanks for getting in touch. Open the revisions page for the service and identify the last revision that was healthy [1]. Select roll back on that revision; traffic moves within roughly thirty seconds and no rebuild takes place [1]. If the release included a database migration, roll the migration back before the service, or the older code will encounter a schema it does not expect [1]. Record the incident and the reason for the rollback before deploying a fix, while the detail is still fresh [1].

This reply was written automatically from our help article "Rolling back a failed release" (DOC-DEPLOY-002). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0349 · database_issue · key says escalate

**Ticket:** We are getting errors saying no connection is available. This started when we scaled up our service. The database itself shows very few active queries.

**Answerable from articles (key):** True · **cited:** ['DOC-PERF-003']

**Sent:** Thanks for getting in touch. Calculate the total possible connections as pool size multiplied by maximum instances, and compare it against your plan's connection limit [1]. Reduce the per-instance pool size rather than raising the limit, as a large number of small pools is usually the wrong shape for a scaled service [1]. Look for queries that hold a transaction open across a network call to another service, which is the most common cause of leaks of this kind [1]. Consider a connection proxy if the instance count must remain high, so that pooling happens once rather than per instance [1].

This reply was written automatically from our help article "Database connection pool exhaustion" (DOC-PERF-003). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0372 · performance_degradation · key says escalate

**Ticket:** latency has been climbing gradually over past a couple of days. Nothing in our code has change. please do the needful.

**Answerable from articles (key):** False · **cited:** ['DOC-PERF-001']

**Sent:** Thanks for getting in touch. Compare the median and 95th percentile latency on the metrics page to see if a large gap indicates contention or queueing [1]. Check memory utilisation across instances; sustained utilisation above eighty percent typically shows up as latency before failure [1]. Review the dependency timing breakdown on the trace view to identify whether the delay is in your service or a downstream dependency [1]. Adjust the autoscaling policy if the load is predictable, using request count rather than processor utilisation to respond sooner [1].

This reply was written automatically from our help article "Diagnosing elevated response latency" (DOC-PERF-001). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0393 · account_access · key says escalate

**Ticket:** Permission changes not taking effect A team member left on Monday and I want to make sure their access is fully removed, including anything they may have created.

**Answerable from articles (key):** False · **cited:** ['DOC-ACCT-001']

**Sent:** Thanks for getting in touch. Check the effective permissions view for the user to see all direct roles and group memberships [1]. Confirm that any pending invitation for the user has been accepted; pending invitations expire after seven days [1]. Remove the departing user from the team rather than just changing their password, and revoke any API keys they created [1]. If the user was the last account owner, transfer ownership before removing them [1].

This reply was written automatically from our help article "Managing team members, roles and permissions" (DOC-ACCT-001). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0399 · account_access · key says escalate

**Ticket:** user left company. how i remove all his access including key he made?

**Answerable from articles (key):** False · **cited:** ['DOC-ACCT-001']

**Sent:** Thanks for getting in touch. Check the effective permissions view for the user, which resolves direct roles and group memberships together [2]. Confirm the invitation was accepted, as pending invitations appear in a separate section and expire after seven days [2]. Remove the departing user rather than only changing their password, and revoke any API keys they created [2]. Prefer group membership to direct role assignment, so that access can be reviewed in one place [2].

This reply was written automatically from our help article "Managing team members, roles and permissions" (DOC-ACCT-001). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0400 · performance_degradation · key says escalate

**Ticket:** Our response times have roughly doubled since yesterday morning with no deployment on our side. The median looks acceptable but the 95th percentile is far worse than it was.

**Answerable from articles (key):** False · **cited:** ['DOC-PERF-001']

**Sent:** Thanks for getting in touch. Compare the median and 95th percentile latency on the metrics page to confirm a large gap indicating contention or queueing [1]. Check memory utilisation across instances; sustained utilisation above eighty percent typically shows up as latency before failure [1]. Review the dependency timing breakdown on the trace view to see if the delay is in your service or a downstream dependency [1]. Adjust the autoscaling policy if the load is predictable, using request count scaling instead of processor utilisation [1].

This reply was written automatically from our help article "Diagnosing elevated response latency" (DOC-PERF-001). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0406 · webhook_issue · key says escalate

**Ticket:** Webhooks not arriving We are receiving the same event several times. Is this expected behaviour or is something wrong with our configuration?

**Answerable from articles (key):** False · **cited:** ['DOC-API-003']

**Sent:** Thanks for getting in touch. Check the webhook delivery log, which records every attempt with the response status and body for the last seven days [1]. Return a 2xx status as quickly as possible and process the event asynchronously, noting that deliveries time out after five seconds [1]. Compute the signature over the raw request body before any parsing, as re-serialising JSON changes the bytes and invalidates the signature [1]. Make your handler idempotent using the event identifier because at-least-once delivery means duplicates are expected rather than exceptional [1].

This reply was written automatically from our help article "Webhook delivery, retries and signature verification" (DOC-API-003). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0407 · billing_query · key says escalate

**Ticket:** Our invoice this month is considerably higher than usual and I cannot see why from the summary. Could you help me understand what has driven the increase?

**Answerable from articles (key):** False · **cited:** ['DOC-BILL-001']

**Sent:** Thanks for getting in touch. Open the usage breakdown for the period, which itemises charges by service and by environment [1]. Look for resources in staging or development environments, which are billed at the same rate as production [1]. Check the billing period dates at the top of the invoice [1]. The period runs from the anniversary of the subscription date [1]. Set a usage alert on the billing page so that unexpected accrual is noticed during the period rather than at the end of it [1].

This reply was written automatically from our help article "Understanding your invoice and usage breakdown" (DOC-BILL-001). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0417 · sso_configuration · key says escalate

**Ticket:** Help configuring single sign-on Single sign-on works for our engineering group but the finance group gets an error. Both are configured identically as far as we can tell. Any idea what differs?

**Answerable from articles (key):** False · **cited:** ['DOC-AUTH-003']

**Sent:** Thanks for getting in touch. Compare the assertion consumer service URL in your identity provider against the value shown on the SSO settings page and ensure they match exactly, including the trailing path [1]. Inspect a failing assertion and confirm the NameID is the user's email address in lower case [1]. Enable just-in-time provisioning if new users should be created on first login, and set a default role for provisioned users [1]. Keep at least one administrator account with password access while testing, so a misconfiguration does not lock the whole organisation out [1].

This reply was written automatically from our help article "Single sign-on configuration with SAML providers" (DOC-AUTH-003). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0437 · performance_degradation · key says escalate

**Ticket:** p95 latency is very high The service is noticeably slow during our afternoon peak and fine the rest of the day. We have autoscaling enabled so I expected it to cope.

**Answerable from articles (key):** True · **cited:** ['DOC-PERF-001', 'DOC-PERF-002']

**Sent:** Thanks for getting in touch. Compare the median and 95th percentile latency on the metrics page to see if there is a large gap indicating contention or queueing [1]. Check memory utilisation across instances; sustained utilisation above eighty per cent can cause latency before failures appear [1]. Review the dependency timing breakdown on the trace view to determine if the delay is within your service or caused by a downstream dependency [1]. Check whether the service is sitting at its configured maximum instance count, as scaling will stop at that limit [3]. Choose a scaling metric that reflects the pressure you actually face, such as request concurrency, which reacts faster than processor utilisation [3]. Set the cooldown period longer than your instance startup time so new instances are counted before another scaling decision is made [3]. Set a minimum instance count above zero for latency-sensitive services to avoid cold starts during peak periods [3].

This reply was written automatically from our help article "Diagnosing elevated response latency" (DOC-PERF-001). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0442 · deployment_failure · key says escalate

**Ticket:** Build fails in the pipeline Our deployment reaches running and then rolls back after about a minute. The logs mention a health check timeout. It runs perfectly on my machine and in staging.

**Answerable from articles (key):** False · **cited:** ['DOC-DEPLOY-001']

**Sent:** Thanks for getting in touch. Confirm the container is listening on the port declared in the service definition [2]. Increase the initial delay if the application needs time to warm up before it can answer, using thirty seconds as a starting point [2]. Compare the environment variables present in the deployment against those the application requires [2]. Inspect the container logs from the failed revision rather than the running one to see the health check timeout details [2].

This reply was written automatically from our help article "Container deployments failing during the health check phase" (DOC-DEPLOY-001). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0444 · rollback_request · key says escalate

**Ticket:** How do I revert to the previous revision We shipped a release around 14:00 yesterday that has broken checkout for a portion of our customers. We need to get back to the previous version quickly. What is the fastest safe route?

**Answerable from articles (key):** False · **cited:** ['DOC-DEPLOY-002']

**Sent:** Thanks for getting in touch. Open the revisions page for the service and identify the last revision that was healthy [1]. Select roll back on that revision [1]. Traffic moves within roughly thirty seconds and no rebuild takes place [1]. If the release included a database migration, roll the migration back before the service, or the older code will encounter a schema it does not expect [1]. Record the incident and the reason for the rollback before deploying a fix while the detail is still fresh [1].

This reply was written automatically from our help article "Rolling back a failed release" (DOC-DEPLOY-002). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0460 · account_access · key says escalate

**Ticket:** Permission changes not taking effect A team member left over the weekend and I want to make sure their access is fully removed, including anything they may have created.

**Answerable from articles (key):** False · **cited:** ['DOC-ACCT-001']

**Sent:** Thanks for getting in touch. Check the effective permissions view for the user to see all direct roles and group memberships that may still grant access [1]. Confirm that any pending invitation for the user has been accepted; pending invitations expire after seven days [1]. Remove the departing user from the team rather than just changing their password, and revoke any API keys they created [1]. Prefer using group membership for access control so that future reviews can be done in one place [1].

This reply was written automatically from our help article "Managing team members, roles and permissions" (DOC-ACCT-001). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0461 · rollback_request · key says escalate

**Ticket:** How do I revert to the previous revision We shipped a release yesterday morning that has broken checkout for a portion of our customers. We need to get back to the previous version quickly. What is the fastest safe route?

**Answerable from articles (key):** False · **cited:** ['DOC-DEPLOY-002']

**Sent:** Thanks for getting in touch. Open the revisions page for the service and identify the last revision that was healthy [1]. Select roll back on that revision; traffic will move within roughly thirty seconds and no rebuild takes place [1]. If the release included a database migration, roll the migration back before the service, or the older code will encounter a schema it does not expect [1]. Record the incident and the reason for the rollback before deploying a fix, while the detail is still fresh [1].

This reply was written automatically from our help article "Rolling back a failed release" (DOC-DEPLOY-002). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0476 · api_key_issue · key says escalate

**Ticket:** One of our production keys started returning 401 at around around 14:00 yesterday without any change on our side. Other keys against the same account are still working.

**Answerable from articles (key):** False · **cited:** ['DOC-AUTH-004']

**Sent:** Thanks for getting in touch. Check the API keys page for the key's status and expiry, as revoked or expired keys will be listed with the date and the user who acted [1]. Review the scopes attached to the key to ensure it includes the endpoint you are calling [1]. If the key is revoked or expired, create a replacement key, deploy it, confirm traffic has moved, then revoke the old key to rotate without downtime [1]. If the key was exposed, revoke it immediately rather than waiting for a rotation window [1].

This reply was written automatically from our help article "API key rotation and scope management" (DOC-AUTH-004). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0480 · deployment_failure · key says escalate

**Ticket:** Build fails in the pipeline Builds that worked last week are now failing during dependency resolution. We have not changed our code at all. This is blocking a release we had planned for around 14:00 yesterday.

**Answerable from articles (key):** False · **cited:** ['DOC-DEPLOY-003']

**Sent:** Thanks for getting in touch. Pin all dependencies to exact versions and commit the lock file to prevent unpinned updates from breaking the build [1]. Verify that the runtime version declared in your build configuration matches the version you use locally [1]. Clear the build cache from the settings page and trigger a fresh build to eliminate any corrupted artefacts [1].

This reply was written automatically from our help article "Build failures caused by dependency resolution" (DOC-DEPLOY-003). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0484 · sso_configuration · key says escalate

**Ticket:** SSO works for some users only We are setting up SAML with our identity provider and users are being bounced back to an error page after authenticating successfully on our side. The assertion looks correct to us.

**Answerable from articles (key):** False · **cited:** ['DOC-AUTH-003']

**Sent:** Thanks for getting in touch. Compare the assertion consumer service URL in your identity provider against the value shown on the SSO settings page; they must match exactly, including the trailing path [1]. Inspect a failing assertion and confirm that the NameID is the user's email address in lower case [1]. Enable just-in-time provisioning if new users should be created on first login, and set a default role for provisioned users [1]. Keep at least one administrator account with password access while testing, so a misconfiguration does not lock the whole organisation out [1].

This reply was written automatically from our help article "Single sign-on configuration with SAML providers" (DOC-AUTH-003). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0495 · performance_degradation · key says escalate

**Ticket:** p95 latency is very high Latency has been climbing gradually over the past most of the morning. Nothing in our code has changed. Memory usage looks high but not at the limit.

**Answerable from articles (key):** False · **cited:** ['DOC-PERF-001']

**Sent:** Thanks for getting in touch. Compare the median and 95th percentile latency on the metrics page to see if a large gap indicates contention or queueing [1]. Check memory utilisation across instances; sustained utilisation above eighty percent typically shows up as latency before failure [1]. Review the dependency timing breakdown on the trace view to identify whether the delay is in your service or a downstream dependency [1]. Adjust the autoscaling policy if the load is predictable, scaling on request count rather than processor utilisation [1].

This reply was written automatically from our help article "Diagnosing elevated response latency" (DOC-PERF-001). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

### DEV-0497 · authentication_failure · key says escalate

**Ticket:** Locked out of my account I have been trying to sign in for the last most of the morning and keep getting an invalid credentials message. I am certain the password is correct because I use a password manager. Nothing has changed at our end that I am aware of.

**Answerable from articles (key):** False · **cited:** ['DOC-AUTH-001']

**Sent:** Thanks for getting in touch. Check if the account is locked by visiting the security page of the console; a locked account shows a red banner and unlocks automatically after thirty minutes [1]. Clear cookies for the CloudServe domain or open a private browsing window, then try logging in again [1]. If using the CLI, run `cloudserve auth logout` followed by `cloudserve auth login` to discard any cached token [1].

This reply was written automatically from our help article "Resolving invalid credential errors on login" (DOC-AUTH-001). If it does not solve your problem, just reply to this message and a member of our support team will pick it up.

**Your verdict:** harmful / acceptable / good

## 3. Should-be-automatic tickets sent to a person

- DEV-0016 (api_key_issue): Sent to a person (Needs a specialist) because a safety rule says a person must handle it (word rule: leaked key or credentials). Priority high (security risk).
- DEV-0050 (billing_query): Sent to a person (Needs a specialist) because a safety rule says a person must handle it (word rule: billing dispute). Priority medium (the classifier's urgency).
- DEV-0058 (data_residency): Sent to a person (Needs a specialist) because a safety rule says a person must handle it (word rule: data location; type: data_residency). Priority medium (the classifier's urgency).
- DEV-0059 (data_residency): Sent to a person (Needs a specialist) because a safety rule says a person must handle it (word rule: data location; type: data_residency). Priority medium (the classifier's urgency).
- DEV-0078 (billing_query): Sent to a person (Needs a specialist) because a safety rule says a person must handle it (word rule: billing dispute). Priority low (the classifier's urgency).
- DEV-0079 (billing_query): Sent to a person (Needs a specialist) because a safety rule says a person must handle it (word rule: billing dispute). Priority medium (the classifier's urgency).
- DEV-0106 (data_residency): Sent to a person (Needs a specialist) because a safety rule says a person must handle it (word rule: data location; type: data_residency). Priority medium (the classifier's urgency).
- DEV-0135 (data_residency): Sent to a person (Needs a specialist) because a safety rule says a person must handle it (word rule: data location; type: data_residency). Priority low (the classifier's urgency).
- DEV-0151 (billing_query): Sent to a person (Needs a specialist) because a safety rule says a person must handle it (word rule: billing dispute). Priority low (the classifier's urgency).
- DEV-0188 (data_residency): Sent to a person (Needs a specialist) because a safety rule says a person must handle it (word rule: data location; type: data_residency). Priority low (the classifier's urgency).
- DEV-0189 (billing_query): Sent to a person (Needs a specialist) because a safety rule says a person must handle it (word rule: billing dispute). Priority low (the classifier's urgency).
- DEV-0205 (data_residency): Sent to a person (Needs a specialist) because a safety rule says a person must handle it (word rule: data location; type: data_residency). Priority medium (the classifier's urgency).
- DEV-0208 (data_residency): Sent to a person (Needs a specialist) because a safety rule says a person must handle it (word rule: data location; type: data_residency). Priority medium (the classifier's urgency).
- DEV-0222 (api_key_issue): Sent to a person (Needs a specialist) because a safety rule says a person must handle it (word rule: leaked key or credentials). Priority high (security risk).
- DEV-0228 (billing_query): Sent to a person (Needs a specialist) because a safety rule says a person must handle it (word rule: billing dispute). Priority medium (the classifier's urgency).
- DEV-0269 (api_key_issue): Sent to a person (Needs a specialist) because a safety rule says a person must handle it (word rule: leaked key or credentials). Priority high (security risk).
- DEV-0273 (onboarding): Sent to a person (Needs a specialist) because the articles do not answer it.
- DEV-0289 (data_residency): Sent to a person (Needs a specialist) because a safety rule says a person must handle it (word rule: data location; type: data_residency). Priority medium (the classifier's urgency).
- DEV-0292 (data_residency): Sent to a person (Needs a specialist) because a safety rule says a person must handle it (word rule: data location; type: data_residency). Priority low (the classifier's urgency).
- DEV-0296 (onboarding): Sent to a person (Needs a specialist) because no help article matches it closely enough. Priority medium (the classifier's urgency).
- DEV-0309 (data_residency): Sent to a person (Needs a specialist) because a safety rule says a person must handle it (word rule: data location; type: data_residency). Priority low (the classifier's urgency).
- DEV-0314 (api_key_issue): Sent to a person (Needs a specialist) because a safety rule says a person must handle it (word rule: leaked key or credentials). Priority high (security risk).
- DEV-0317 (data_residency): Sent to a person (Needs a specialist) because a safety rule says a person must handle it (word rule: data location; type: data_residency). Priority medium (the classifier's urgency).
- DEV-0334 (api_key_issue): Sent to a person (Needs a specialist) because a safety rule says a person must handle it (word rule: leaked key or credentials). Priority high (security risk).
- DEV-0371 (data_residency): Sent to a person (Needs a specialist) because a safety rule says a person must handle it (word rule: data location; type: data_residency). Priority medium (the classifier's urgency).
- DEV-0388 (data_residency): Sent to a person (Needs a specialist) because a safety rule says a person must handle it (word rule: data location; type: data_residency). Priority low (the classifier's urgency).
- DEV-0389 (data_residency): Sent to a person (Needs a specialist) because a safety rule says a person must handle it (word rule: data location; type: data_residency). Priority low (the classifier's urgency).
- DEV-0411 (billing_query): Sent to a person (Needs a specialist) because a safety rule says a person must handle it (word rule: billing dispute). Priority low (the classifier's urgency).
- DEV-0415 (billing_query): Sent to a person (Needs a specialist) because a safety rule says a person must handle it (word rule: billing dispute). Priority low (the classifier's urgency).
- DEV-0433 (data_residency): Sent to a person (Needs a specialist) because a safety rule says a person must handle it (word rule: data location; type: data_residency). Priority medium (the classifier's urgency).
- DEV-0445 (data_residency): Sent to a person (Needs a specialist) because a safety rule says a person must handle it (word rule: data location; type: data_residency). Priority medium (the classifier's urgency).
- DEV-0464 (data_residency): Sent to a person (Needs a specialist) because a safety rule says a person must handle it (word rule: data location; type: data_residency). Priority medium (the classifier's urgency).
- DEV-0466 (data_residency): Sent to a person (Needs a specialist) because a safety rule says a person must handle it (word rule: data location; type: data_residency). Priority medium (the classifier's urgency).
- DEV-0474 (onboarding): Sent to a person (Needs a specialist) because the articles do not answer it.
- DEV-0478 (billing_query): Sent to a person (Needs a specialist) because a safety rule says a person must handle it (word rule: billing dispute). Priority low (the classifier's urgency).
- DEV-0483 (data_residency): Sent to a person (Needs a specialist) because a safety rule says a person must handle it (word rule: data location; type: data_residency). Priority medium (the classifier's urgency).
- DEV-0489 (data_residency): Sent to a person (Needs a specialist) because a safety rule says a person must handle it (word rule: data location; type: data_residency). Priority medium (the classifier's urgency).
- DEV-0491 (api_key_issue): Sent to a person (Needs a specialist) because a safety rule says a person must handle it (word rule: leaked key or credentials). Priority high (security risk).
- DEV-0492 (data_residency): Sent to a person (Needs a specialist) because a safety rule says a person must handle it (word rule: data location; type: data_residency). Priority medium (the classifier's urgency).
