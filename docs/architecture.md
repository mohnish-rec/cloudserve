# Architecture

How the CloudServe support system is designed, and why. Each choice traces to a requirement in the PRD (product requirements document) version 2 and to the course module it comes from. Written 7 November 2026, before the build; updated as the build changes it.

## 1. Why the system exists: the translation ladder (Module 1)

| Layer | CloudServe |
|---|---|
| L1 Business outcome | First reply within the two-hour agreement; first-contact resolution from 43.8% to 60% or more; without adding staff |
| L2 Decision changed | For each ticket: answer it now from an article, or hand it to the right person with the work already done |
| L3 Metric | First-contact resolution, escalation rate, first-reply time, repeat contacts, fairness gap between customer groups |
| L4 Signal | The ticket's type and urgency with a calibrated confidence; whether an article answers it; whether it is a risky type |
| L5 Model task | Classify the ticket; find the article; write a cited reply or a hand-over; check it before release |

Downward check: an answer that is classified, grounded in an article and checked is what lets a ticket close without a person (L1). Upward check: a perfect L4 signal changes L2 for about 70% of tickets (the safe ceiling in the workbook, Section 2).

## 2. Boundaries (Module 1)

- **We own:** reading tickets, classifying, searching the 29 articles, writing replies and hand-overs, guardrails, routing, the decision log, the metrics report.
- **We assume:** the articles are correct and current; agents read hand-overs; the hidden tickets resemble the development tickets (PRD section 7).
- **Not ours:** sending email, account changes, refunds, live channel connections, writing articles (PRD section 6).

## 3. The pipeline

```
tickets file / API (application programming interface)
  -> 1 Ingest      raw kept + cleaned copy + 7 data-quality checks        (FR-01)
  -> kill switch   on: escalate every ticket                              (FR-16)
  -> 2 Classify    type, urgency, calibrated confidence, 3 alternatives   (FR-02)
  -> safety rules  fixed word rules + risky types: either one -> person   (FR-03)
  -> 3 Retrieve    meaning + keyword search, top 5, abstain below floor   (FR-04)
  -> 4 Route       answer or escalate, threshold from data, reason        (FR-06)
  -> 5 Generate    cited reply (or fixed "not covered" sentence)          (FR-05)
  -> 6 Validate    5 guardrails, fail closed                              (FR-09)
  -> answer: reply + automatic-reply notice                               (FR-08)
     escalate: hand-over (5 parts + label) + customer acknowledgement     (FR-07)
  -> decision log (every stage), results, metrics report, gaps list       (FR-10, FR-12, FR-15)
```

Every exit is either **answered** or **escalated with a reason**. Nothing is dropped and nothing crashes the run (FR-11).

## 4. The Generative Four and the Sustaining Three (Module 1)

| Lever | Decision | How |
|---|---|---|
| Retrieval | Current, not stale | Search the supplied articles every time; check each article's last-reviewed date (NFR-04 risk) |
| Context | Specific to this ticket | The ticket text, its type, urgency and channel; never the customer's name |
| Memory | Accumulates, within limits | Stored history of processed tickets for repeat contacts (FR-14) |
| Feedback | Reviewed by people, not self-learning | Gaps and blocked replies listed for the writer and tier two (FR-15). The system never changes itself, because learning from current practice would "scale up a mistake" (Daniel) |
| Guardrails | Prevent | Fixed safety rules before the model; five guardrails after it (FR-03, FR-09) |
| Orchestration | Coordinate and record | One orchestrated workflow; every stage logged with the ticket ID as trace ID (FR-10) |
| Recovery | Fail to a person, never to silence | Retries, backup model, then escalation; the kill switch (FR-11, FR-16) |

Trust (Module 1): Trust = Accuracy x Consistency, and customers need to know what produced the answer. Accuracy is measured (NFR-03), consistency is tested (NFR-11), and every automatic reply says it is automatic (FR-08).

## 5. Data pipeline card (Module 3)

| Question | Answer |
|---|---|
| Source to destination | Tickets file -> decisions, results and metrics report |
| ETL (extract, transform, load) or ELT (extract, load, transform) | **ELT**: each ticket is kept raw as received and a cleaned copy is made, because "every cleaning step loses information" and future analysis may need the original |
| Pipeline or orchestration | Per ticket: orchestration (each step depends on the one before). Across tickets: a pipeline (one bad ticket never stops the others) |
| Load | Full load of the input file each run; every run has its own run ID |
| Idempotency | Re-running the same file gives the same decisions under a new run ID; nothing is overwritten or duplicated |
| Failure handling | Temporary errors (429, 5xx, timeouts): retry with backoff and jitter, limited. Permanent errors (401, 400, bad input): no retry. Both end in escalation with the reason |
| Quarantine | A ticket that fails the data-quality checks is escalated with its reasons: our dead-letter queue. Owner: tier two |
| Data-quality checks at ingest | Completeness (ID, body), validity (channel, plan, region, fluency), timeliness (readable time), uniqueness (ticket ID), consistency (clean text), integrity (customer ID carries several names: plan and region read from each ticket, never looked up by ID) |
| Monitoring | Tickets in and out, escalation rate, guardrail blocks, latency, confidence distribution, each with a threshold, an action and an owner (week three) |

## 6. Classifier (Module 4)

- Embeddings (all-MiniLM-L6-v2) with a logistic regression classifier, compared against a TF-IDF (term frequency-inverse document frequency) baseline; the better one is kept (decision D-016).
- Trained only on development tickets; validation tickets used only for testing, never tuning.
- **Group cross-validation by question text**: only 215 different questions in 500 tickets, so ordinary splits would put the same question on both sides and inflate the score.
- Probabilities calibrated and checked with the Evaluation Framework's `calibration_table`.
- Threshold chosen for **high recall on tickets that should escalate**: a missed escalation costs more than an unnecessary one.
- Precision and recall per class, confusion matrix, 95% bootstrap confidence intervals; fixed seed; runs recorded with git commit and data hash.

## 7. Retrieval and generation (Modules 2 and 5)

- **Search:** meaning-based and keyword (BM25, Best Matching 25) results merged by reciprocal rank fusion, because tickets contain exact codes such as 429 and 401. Kept only if it beats meaning-only search (decision D-017, with chunk size).
- **Abstain:** below a relevance threshold set from data, search returns nothing and the ticket escalates.
- **Grounding contract:** numbered sources; every claim cites [n]; one fixed sentence when the sources do not answer; ticket text inside delimiters as data, never instructions; temperature 0.
- **Structured output:** JSON (JavaScript Object Notation) checked against a schema in code; unparseable output escalates.
- **Prompts:** versioned in `prompts/` and registered in the Stage 3 prompt library with the requirement each serves.
- **Evaluation:** search measured separately (expected article in the top 5, and its rank) from replies (grounding, citation accuracy). An AI judge from a different model family (Llama) judges gpt-oss replies; agreement with my own scores is reported.

## 8. Guardrails (Module 5, Governance Framework section 4)

| Guardrail | Checks | When it fires |
|---|---|---|
| Private data | Names, addresses, keys, account numbers, anything identifying another customer | Block and escalate; never redact and send |
| Grounding | Every claim cites a retrieved passage | Block and escalate, with the unsupported claim flagged |
| Instruction integrity | The ticket has not tried to change the system's instructions | Block, escalate and record the input for review |
| Tone and scope | Stays within support; no promises about refunds, credits or dates | Block and escalate |
| Confidence floor | The threshold was applied; a missing confidence counts as low | Escalate |

All guardrails **fail closed**: if a check errors, the reply is blocked. A red-team set of attack tickets is kept as regression tests, and the false-alarm rate on ordinary tickets is reported.

## 9. Orchestration and deployment (Module 7)

- The steps can be drawn as a flowchart, so the system is **one orchestrated workflow with a single language model**, not a crew of agents (which costs 3 to 8 times the model calls).
- One framework: LangGraph, as the Project Brief recommends; no CrewAI.
- Bounded: one retry for malformed output, timeouts on every call, a token budget per ticket.
- Typed contracts: every result checked against a schema before it is written.
- One trace per ticket, with secrets and personal details removed before logging.
- FastAPI endpoint with `/healthz` and `/readyz` (FR-17); pinned requirements; keys only in `.env`.

## 10. How the system is judged (Module 1, eval first)

Gates set before running: type precision 85%+; calibration within 5 points; unsupported claims 5% or fewer; citation accuracy 95%+; zero private data; fairness gap under 5 points; consistency 80%+ agreement over 10 runs; zero automatic replies to risky tickets. Also measured: success of each step and the weakest step, latency at the median and 95th percentile, and the share of "check and send" drafts that were right.

## 11. Architecture decisions

Recorded in full in `docs/decision_log.md`: D-016 (trained classifier, not the language model, decides the ticket type). To come during the build: D-017 (chunk size and hybrid search), D-018 (threshold), D-019 (LangGraph orchestration), D-020 (AI judge).
