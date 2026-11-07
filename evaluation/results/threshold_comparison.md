# Confidence threshold comparison (decision D-019)

500 development tickets; classifier embeddings, C = 10 (D-018), out-of-fold predictions (5-fold group cross-validation). The answer key says 311 tickets (62.2%) should be answered automatically and 87 must never be.

Before any threshold: safety rules or person-only type send 134 tickets to a person; search finds no relevant article for 17.

| Threshold | Answered automatically (FCR estimate) | Escalated | Must-not answered automatically | Other escalate tickets answered | Wrong type among automatic | Not answerable from articles among automatic | Should-be-automatic tickets answered | Draft ready / Needs a specialist | Largest gap between groups |
|---|---|---|---|---|---|---|---|---|---|
| 0.50 | 72.2% (361) | 27.8% | 0 | 88 | 3 | 74 | 273 of 311 (87.8%) | 3 / 136 | 8.8 points (region) |
| 0.60 | 72.0% (360) | 28.0% | 0 | 88 | 3 | 74 | 272 of 311 (87.5%) | 4 / 136 | 8.8 points (region) |
| 0.70 | 71.4% (357) | 28.6% | 0 | 88 | 0 | 74 | 269 of 311 (86.5%) | 7 / 136 | 9.2 points (region) |
| 0.80 | 70.8% (354) | 29.2% | 0 | 86 | 0 | 72 | 268 of 311 (86.2%) | 10 / 136 | 8.2 points (region) |
| 0.85 | 70.8% (354) | 29.2% | 0 | 86 | 0 | 72 | 268 of 311 (86.2%) | 10 / 136 | 8.2 points (region) |
| 0.90 | 69.2% (346) | 30.8% | 0 | 86 | 0 | 72 | 260 of 311 (83.6%) | 18 / 136 | 11.4 points (region) |
| 0.95 | 67.6% (338) | 32.4% | 0 | 84 | 0 | 71 | 254 of 311 (81.7%) | 26 / 136 | 15.6 points (region) |
| 0.98 | 67.2% (336) | 32.8% | 0 | 84 | 0 | 71 | 252 of 311 (81.0%) | 28 / 136 | 14.6 points (region) |

## Why should-be-automatic tickets went to a person (threshold 0.85)

43 of 311 tickets.

| Reason | All | tier: worst group | region: worst group | language_fluency: worst group |
|---|---|---|---|---|
| safety word rule | 36 | standard 20 of 154 (13.0%) | latin_america 6 of 39 (15.4%) | non_fluent 12 of 80 (15.0%) |
| confidence | 6 | enterprise 2 of 51 (3.9%) | europe 3 of 103 (2.9%) | fluent 5 of 231 (2.2%) |
| search found no relevant article | 1 | business 1 of 106 (0.9%) | asia_pacific 1 of 64 (1.6%) | non_fluent 1 of 80 (1.2%) |
- customer_tier: gap 95% range 1.5 to 15.9 points
- customer_region: gap 95% range 3.6 to 22.3 points
- language_fluency: gap 95% range 0.2 to 14.6 points

Every ticket sent to a person (reason in full):

- DEV-0016 [asia_pacific, non_fluent] safety word rule: word rule: leaked key or credentials: Need to rotate an exposed key. one of our engineers pushed key to a public repository by mistake. We need to r
- DEV-0050 [north_america, non_fluent] safety word rule: word rule: billing dispute: Question about this month's charges. invoice showing service we not use. can you check and tell?
- DEV-0058 [latin_america, fluent] safety word rule: word rule: data location, type: data_residency: Question about backup regions. One of our customers has asked for written confirmation of where their data is 
- DEV-0059 [europe, fluent] safety word rule: word rule: data location, type: data_residency: One of our customers has asked for written confirmation of where their data is physically stored. Could you po
- DEV-0078 [north_america, fluent] safety word rule: word rule: billing dispute: There are charges on our invoice for a service I do not believe we use. Could you explain what these relate to
- DEV-0079 [asia_pacific, non_fluent] safety word rule: word rule: billing dispute: invoice showing service we not use. can you check and tell?
- DEV-0100 [north_america, non_fluent] confidence 0.56 below 0.85: throughput is fine for couple of minutes and then drops sharply. It looks like we are being throttled but docu
- DEV-0106 [north_america, non_fluent] safety word rule: word rule: data location, type: data_residency: are backups replicated outside our primary region? compliance review has raised this and I need definite answe
- DEV-0135 [latin_america, non_fluent] safety word rule: word rule: data location, type: data_residency: Need data to stay in the EU. one of our customers has asked for written confirmation of where their data physi
- DEV-0143 [north_america, fluent] confidence 0.41 below 0.85: Our connection pool appears to be exhausting under moderate load. We have already increased the pool size and 
- DEV-0145 [europe, fluent] confidence 0.76 below 0.85: A key can read fine but every write returns a permission error. I created it myself and I thought I gave it fu
- DEV-0151 [europe, fluent] safety word rule: word rule: billing dispute: Invoice higher than expected. There are charges on our invoice for a service I do not believe we use. Could yo
- DEV-0188 [north_america, fluent] safety word rule: word rule: data location, type: data_residency: Where is our data stored. Are backups replicated outside our primary region? A compliance review has raised th
- DEV-0189 [north_america, fluent] safety word rule: word rule: billing dispute: There are charges on our invoice for a service I do not believe we use. Could you explain what these relate to
- DEV-0205 [latin_america, fluent] safety word rule: word rule: data location, type: data_residency: Question about backup regions. Are backups replicated outside our primary region? A compliance review has rais
- DEV-0207 [europe, fluent] confidence 0.70 below 0.85: Question about the export endpoint. Our cursor seems to stop working partway through a long iteration. Is ther
- DEV-0208 [north_america, non_fluent] safety word rule: word rule: data location, type: data_residency: one of our customers has asked for written confirmation of where their data is physically stored. Can you plea
- DEV-0216 [europe, fluent] confidence 0.70 below 0.85: Question about the export endpoint. Our cursor seems to stop working partway through a long iteration. Is ther
- DEV-0222 [europe, fluent] safety word rule: word rule: leaked key or credentials: One of our engineers pushed a key to a public repository by mistake. We need to replace it without taking the 
- DEV-0228 [europe, non_fluent] safety word rule: word rule: billing dispute: Invoice higher than expected. invoice showing service we not use. can you check and tell?
- DEV-0269 [asia_pacific, fluent] safety word rule: word rule: leaked key or credentials: One of our engineers pushed a key to a public repository by mistake. We need to replace it without taking the 
- DEV-0289 [latin_america, non_fluent] safety word rule: word rule: data location, type: data_residency: we need our data to remain within EU for contract we are signing. Our organisation was created some time ago a
- DEV-0292 [north_america, fluent] safety word rule: word rule: data location, type: data_residency: Need data to stay in the EU. One of our customers has asked for written confirmation of where their data is ph
- DEV-0296 [asia_pacific, non_fluent] search found no relevant article: New to the platform, where to begin. can you please point me at right starting place? i am having created acco
- DEV-0309 [europe, non_fluent] safety word rule: word rule: data location, type: data_residency: Need data to stay in the EU. one of our customers has asked for written confirmation of where their data physi
- DEV-0314 [asia_pacific, fluent] safety word rule: word rule: leaked key or credentials: Key stopped working overnight. One of our engineers pushed a key to a public repository by mistake. We need to
- DEV-0317 [north_america, non_fluent] safety word rule: word rule: data location, type: data_residency: we need our data to remain within EU for contract we are signing. Our organisation was created some time ago a
- DEV-0334 [north_america, non_fluent] safety word rule: word rule: leaked key or credentials: Need to rotate an exposed key. one of our engineers pushed a key to a public repository by mistake. We need to
- DEV-0371 [north_america, fluent] safety word rule: word rule: data location, type: data_residency: We need our data to remain within the EU for a contract we are signing. Our organisation was created some time
- DEV-0388 [latin_america, fluent] safety word rule: word rule: data location, type: data_residency: Need data to stay in the EU. Are backups replicated outside our primary region? A compliance review has raised
- DEV-0389 [europe, fluent] safety word rule: word rule: data location, type: data_residency: Need data to stay in the EU. One of our customers has asked for written confirmation of where their data is ph
- DEV-0411 [asia_pacific, fluent] safety word rule: word rule: billing dispute: Billing period dates unclear. There are charges on our invoice for a service I do not believe we use. Could yo
- DEV-0415 [north_america, fluent] safety word rule: word rule: billing dispute: Question about this month's charges. There are charges on our invoice for a service I do not believe we use. C
- DEV-0422 [latin_america, fluent] confidence 0.70 below 0.85: Question about the export endpoint. Our cursor seems to stop working partway through a long iteration. Is ther
- DEV-0433 [north_america, fluent] safety word rule: word rule: data location, type: data_residency: One of our customers has asked for written confirmation of where their data is physically stored. Could you po
- DEV-0445 [north_america, fluent] safety word rule: word rule: data location, type: data_residency: We need our data to remain within the EU for a contract we are signing. Our organisation was created some time
- DEV-0464 [europe, fluent] safety word rule: word rule: data location, type: data_residency: Are backups replicated outside our primary region? A compliance review has raised this and I need a definite a
- DEV-0466 [asia_pacific, fluent] safety word rule: word rule: data location, type: data_residency: Where is our data stored. We need our data to remain within the EU for a contract we are signing. Our organisa
- DEV-0478 [asia_pacific, fluent] safety word rule: word rule: billing dispute: Billing period dates unclear. There are charges on our invoice for a service I do not believe we use. Could yo
- DEV-0483 [asia_pacific, fluent] safety word rule: word rule: data location, type: data_residency: We need our data to remain within the EU for a contract we are signing. Our organisation was created some time
- DEV-0489 [latin_america, non_fluent] safety word rule: word rule: data location, type: data_residency: Question about backup regions. are backups replicated outside our primary region? A compliance review has rais
- DEV-0491 [north_america, fluent] safety word rule: word rule: leaked key or credentials: Need to rotate an exposed key. A key can read fine but every write returns a permission error. I created it my
- DEV-0492 [asia_pacific, fluent] safety word rule: word rule: data location, type: data_residency: One of our customers has asked for written confirmation of where their data is physically stored. Could you po

Notes:
- FCR (first contact resolution) here counts only the routing step. The reply must still pass the grounding check and guardrails, which can only lower it.
- 'Not answerable from articles among automatic': search found something, but the answer key says the articles do not answer it. The grounding check (the model answers only from the article, or abstains) must catch these; measured on Day 5.
- Gaps compare groups of at least 10 should-be-automatic tickets; the target is under 5 points.

## Threshold 0.50

Share of should-be-automatic tickets answered automatically, by group (groups under 10 tickets not compared):

- customer_tier: business 86.8% (of 106), enterprise 94.1% (of 51), standard 86.4% (of 154)
- customer_region: asia_pacific 84.4% (of 64), europe 93.2% (of 103), latin_america 84.6% (of 39), north_america 85.7% (of 105)
- language_fluency: fluent 89.2% (of 231), non_fluent 83.8% (of 80)

## Threshold 0.60

Share of should-be-automatic tickets answered automatically, by group (groups under 10 tickets not compared):

- customer_tier: business 85.8% (of 106), enterprise 94.1% (of 51), standard 86.4% (of 154)
- customer_region: asia_pacific 84.4% (of 64), europe 93.2% (of 103), latin_america 84.6% (of 39), north_america 84.8% (of 105)
- language_fluency: fluent 89.2% (of 231), non_fluent 82.5% (of 80)

## Threshold 0.70

Share of should-be-automatic tickets answered automatically, by group (groups under 10 tickets not compared):

- customer_tier: business 84.9% (of 106), enterprise 90.2% (of 51), standard 86.4% (of 154)
- customer_region: asia_pacific 84.4% (of 64), europe 91.3% (of 103), latin_america 82.1% (of 39), north_america 84.8% (of 105)
- language_fluency: fluent 87.9% (of 231), non_fluent 82.5% (of 80)

## Threshold 0.80

Share of should-be-automatic tickets answered automatically, by group (groups under 10 tickets not compared):

- customer_tier: business 84.9% (of 106), enterprise 90.2% (of 51), standard 85.7% (of 154)
- customer_region: asia_pacific 84.4% (of 64), europe 90.3% (of 103), latin_america 82.1% (of 39), north_america 84.8% (of 105)
- language_fluency: fluent 87.4% (of 231), non_fluent 82.5% (of 80)

## Threshold 0.85

Share of should-be-automatic tickets answered automatically, by group (groups under 10 tickets not compared):

- customer_tier: business 84.9% (of 106), enterprise 90.2% (of 51), standard 85.7% (of 154)
- customer_region: asia_pacific 84.4% (of 64), europe 90.3% (of 103), latin_america 82.1% (of 39), north_america 84.8% (of 105)
- language_fluency: fluent 87.4% (of 231), non_fluent 82.5% (of 80)

## Threshold 0.90

Share of should-be-automatic tickets answered automatically, by group (groups under 10 tickets not compared):

- customer_tier: business 81.1% (of 106), enterprise 90.2% (of 51), standard 83.1% (of 154)
- customer_region: asia_pacific 82.8% (of 64), europe 88.3% (of 103), latin_america 76.9% (of 39), north_america 81.9% (of 105)
- language_fluency: fluent 84.0% (of 231), non_fluent 82.5% (of 80)

## Threshold 0.95

Share of should-be-automatic tickets answered automatically, by group (groups under 10 tickets not compared):

- customer_tier: business 78.3% (of 106), enterprise 90.2% (of 51), standard 81.2% (of 154)
- customer_region: asia_pacific 82.8% (of 64), europe 87.4% (of 103), latin_america 71.8% (of 39), north_america 79.0% (of 105)
- language_fluency: fluent 81.8% (of 231), non_fluent 81.2% (of 80)

## Threshold 0.98

Share of should-be-automatic tickets answered automatically, by group (groups under 10 tickets not compared):

- customer_tier: business 76.4% (of 106), enterprise 90.2% (of 51), standard 81.2% (of 154)
- customer_region: asia_pacific 82.8% (of 64), europe 86.4% (of 103), latin_america 71.8% (of 39), north_america 78.1% (of 105)
- language_fluency: fluent 81.8% (of 231), non_fluent 78.8% (of 80)

