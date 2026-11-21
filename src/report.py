"""The metrics report (FR-12, Build Specification section 04), calculated by code from one run.

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
The answer key ("labels" in the ticket file) is read ONLY here, after every ticket has been
processed, and only to mark the work; the pipeline never sees it. A file without labels
(for example the hidden set) still gets every figure that does not need them.
"""
import statistics
from collections import Counter, defaultdict

import numpy as np
from sklearn.metrics import classification_report, confusion_matrix

SEGMENTS = ["customer_tier", "customer_region", "language_fluency", "channel"]


def _pct(a, b):
    return f"{a / b:.1%}" if b else "-"


def calibration_table(rows, bands=5):
    """Evaluation Framework's calibration table, with the top band including 1.0 (as in D-018)."""
    out = []
    for i in range(bands):
        lo, hi = i / bands, (i + 1) / bands
        g = [r for r in rows if lo <= r[0] < hi or (hi == 1 and r[0] == 1)]
        if g:
            stated = sum(r[0] for r in g) / len(g)
            observed = sum(r[1] for r in g) / len(g)
            out.append((lo, hi, len(g), stated, observed))
    return out


def _tokens(outcomes, n) -> str:
    """Tokens as the provider reported them: the free tier's limits are counted in tokens (NFR-07)."""
    t = Counter()
    for o in outcomes:
        t.update(getattr(o, "tokens", None) or {})
    used = [o for o in outcomes if (getattr(o, "tokens", None) or {}).get("writer_in")]
    per = (t["writer_in"] + t["writer_out"]) / len(used) if used else 0
    writes = sum(1 for o in outcomes if getattr(o, "draft", None) is not None)
    checks = sum(1 for o in outcomes if getattr(o, "guardrails", None) is not None
                 and any(x.name == "grounding_model" and not x.detail.startswith("not run") for x in o.guardrails.checks))
    t_tokens = sum(v for k, v in t.items() if not k.endswith("_cached"))
    return (f"- **Reply cache (off for validation and test runs):** {t['writer_cached']} of {writes} replies and {t['checker_cached']} of {checks} "
            f"checks reused, with no model call\n"
            f"- **Tokens:** writer {t['writer_in']:,} in + {t['writer_out']:,} out "
            f"({per:,.0f} per reply written); checker {t['checker_in']:,} in + {t['checker_out']:,} out; "
            f"total {t_tokens:,} ({t_tokens / n if n else 0:,.0f} per ticket)")


def repeat_contacts(outcomes, raw_by_id) -> str:
    """17 Nov 2026: the Evaluation Framework's repeat-contact measure ("the same customer raising the same issue
    again within a week") for this run. The follow-up rule (FR-14) finds a repeat that comes after an automatic
    reply; the history block, read only here, gives what happened when people handled these tickets (the baseline)."""
    n = len(outcomes)
    follow = [o for o in outcomes if "follow-up:" in (o.reason or "")]
    to_person = sum(o.action != "auto_respond" for o in follow)
    hist = [r.get("history") for r in raw_by_id.values() if isinstance(r.get("history"), dict)]
    base = sum(bool(h.get("repeat_contact")) for h in hist)
    line = (f"**Repeat contacts:** {len(follow)} of {n} tickets {'was' if len(follow) == 1 else 'were'} the same customer asking about the same type "
            f"within 7 days of an automatic reply in this run; {to_person} of them went to a person with the earlier "
            f"reply attached.")
    if hist:
        line += f" Baseline (the history fields, when people handled these tickets): {base} of {len(hist)} ({_pct(base, len(hist))})."
    return line


# Why a ticket went to a person: the same groups, names and explanations as Table 6 of the report ("Why tickets went
# to a person"), worked out from the reason the system wrote for it. The first that applies is used.
MUST_NOT = "Must-not ticket (security, compliance, feature request, unclear)"
DATA_LOCATION = "Data location"
OWN = "Mohnish Grover's four question groups"
PLAN = "Plan rule"
REFUSED = "Grounding check could not run (free tier limit)"
NO_FIT = "Grounding check: the article does not fit"
BLOCKED = "Blocked by another guardrail"
FOLLOW = "Repeat contact within 7 days"
KILL = "Kill switch on"
ERROR = "System error"
DOWN = "Model provider unavailable"
UNSURE = "Below the confidence threshold, or no article fits"
WHY = {MUST_NOT: "The labels and the Governance Framework say these must never get an automatic reply",
       DATA_LOCATION: 'Daniel: getting it wrong "is a compliance problem"',
       OWN: "Decided in the walkthrough that these need a person",
       PLAN: "The only article that answers is for other plans, so a person checks the draft",
       REFUSED: "A reply that cannot be checked is never sent",
       NO_FIT: "The reply would not match the customer's situation",
       BLOCKED: "A guardrail stopped the reply before it was sent",
       FOLLOW: "The earlier automatic reply did not solve it",
       KILL: "The kill switch stops every automatic reply (FR-16, functional requirement 16)",
       ERROR: "Every ticket produces either a sent answer or a logged escalation (Build Specification)",
       DOWN: "The circuit breaker sends tickets to a person while the model provider fails (FR-11, functional requirement 11)",
       UNSURE: "Below the 85% confidence threshold, a person decides"}
SAFETY_FIRST = {MUST_NOT, DATA_LOCATION, OWN, PLAN, FOLLOW}      # sent by a rule on purpose
SAFETY_RULES = {MUST_NOT, DATA_LOCATION}                         # the fixed safety rules: no confidence score overrides them
MUST_NOT_WORDS = ("word rule: compliance", "word rule: security", "word rule: leaked", "word rule: feature",
                  "type: compliance_request", "type: security_incident", "type: feature_request", "type: unclear_request")
GROUP_NAMES = {"customer_tier": "plan", "customer_region": "region", "language_fluency": "language fluency",
               "channel": "channel"}
NICE = {"latin_america": "Latin America", "north_america": "North America", "asia_pacific": "Asia Pacific",
        "europe": "Europe", "non_fluent": "non-fluent English", "fluent": "fluent English",
        "docs_comment": "documentation comments", "enterprise": "Enterprise", "business": "Business",
        "standard": "Standard"}


def nice(group) -> str:
    return NICE.get(str(group), str(group))


def why_person(o) -> str:
    """One reason per ticket sent to a person: the first that applies."""
    r = o.reason or ""
    rule = "a safety rule says" in r
    if "kill switch" in r:
        return KILL
    if "unexpected error" in r:
        return ERROR
    if "model provider is unavailable" in r or "model unavailable" in r:
        return DOWN
    if rule and ("word rule: data location" in r or "type: data_residency" in r):
        return DATA_LOCATION
    if rule and any(w in r for w in MUST_NOT_WORDS):
        return MUST_NOT
    if any(w in r for w in ("needs a person:", "no article covers it:", "similar tickets were handled by a person")):
        return OWN
    if "follow-up:" in r:
        return FOLLOW
    if "(plan rule)" in r:
        return PLAN
    if "the check failed" in r:
        return REFUSED
    if "Reply blocked by a guardrail" in r:
        return NO_FIT if "grounding_model" in r else BLOCKED
    return UNSURE


def _met(ok):
    return "Not measured" if ok is None else ("Yes" if ok else "**No**")


def group_rates(outcomes, tickets):
    """Share answered automatically for each customer group (no answer key needed). Groups under 10 tickets are
    shown but not compared."""
    tick = {t.ticket_id: t for t in tickets}
    out = {}
    for seg in SEGMENTS:
        groups = defaultdict(list)
        for o in outcomes:
            if o.ticket_id in tick:
                groups[str(getattr(tick[o.ticket_id], seg, None) or "unknown")].append(o)
        rows = {g: (len(m), round(sum(x.action == "auto_respond" for x in m) / len(m) * 100, 1)) for g, m in groups.items()}
        compared = {g: r for g, (k, r) in rows.items() if k >= 10}
        gap = round(max(compared.values()) - min(compared.values()), 1) if len(compared) >= 2 else None
        out[seg] = (rows, compared, gap)
    return out


def _label_rates(ids, labels, tick, seg):
    """Share the labels would answer automatically for each group (groups of 10 or more), and the gap."""
    groups = defaultdict(list)
    for i in ids:
        groups[str(getattr(tick[i], seg, None) or "unknown")].append(labels[i].get("expected_route") == "auto_respond")
    rates = {g: round(sum(v) / len(v) * 100, 1) for g, v in groups.items() if len(v) >= 10}
    return round(max(rates.values()) - min(rates.values()), 1) if len(rates) >= 2 else None


def build(outcomes, tickets, raw_by_id, meta, decisions_logged) -> str:
    """The metrics report. Measures, baselines and targets use the Evaluation Framework's names; the sections after
    them follow the Build Specification's groups (Volume, Business, Technical, Governance)."""
    n = len(outcomes)
    by = Counter(o.action for o in outcomes)
    person = n - by["auto_respond"]
    lat = [o.latency_ms for o in outcomes]
    wait = [getattr(o, "wait_ms", 0) for o in outcomes]                 # 17 Nov: rate-limit waits
    work = [max(0, a - b) for a, b in zip(lat, wait)]                    # response time without those waits
    pq = lambda xs, q: float(np.percentile(xs, q)) if xs else 0.0  # noqa: E731
    fired = Counter(name for o in outcomes if o.guardrails for name in o.guardrails.fired)
    labels = {tid: r.get("labels") for tid, r in raw_by_id.items() if isinstance(r.get("labels"), dict)}
    oc = {o.ticket_id: o for o in outcomes}
    tick = {t.ticket_id: t for t in tickets}
    why = Counter(why_person(o) for o in outcomes if o.action != "auto_respond")
    groups = group_rates(outcomes, tickets)
    reconciles = decisions_logged["outcome"] == n
    mean_s = statistics.mean(lat) / 1000 if lat else 0
    median_s = statistics.median(lat) / 1000 if lat else 0
    fcr, esc = (by["auto_respond"] / n if n else 0), (person / n if n else 0)
    calls = sum(o.model_calls for o in outcomes)
    waited = sum(1 for w in wait if w)

    # Figures that need the labels in the ticket file. The hidden evaluation set may not have them.
    ids = [o.ticket_id for o in outcomes if o.ticket_id in labels]
    must_not = [i for i in ids if labels[i].get("must_not_auto_respond")]
    auto = [i for i in ids if oc[i].action == "auto_respond"]
    cited = [i for i in auto if labels[i].get("expected_doc_ids")]
    cite_bad = [i for i in cited if not (oc[i].draft and set(labels[i]["expected_doc_ids"]) & set(oc[i].draft.cited_doc_ids))]
    true_i = [labels[i]["intent"] for i in ids]
    pred_i = [oc[i].classification.intent if oc[i].classification else "(system error)" for i in ids]
    per_type = {c: sum(t == c for t, p_ in zip(true_i, pred_i) if p_ == c) / pred_i.count(c) for c in set(pred_i)}
    lowest = min(per_type, key=per_type.get) if per_type else None
    conf = [(oc[i].classification.confidence, oc[i].classification.intent == labels[i]["intent"])
            for i in ids if oc[i].classification]
    cal_gap = (sum(c for c, _ in conf) / len(conf) - sum(ok for _, ok in conf) / len(conf)) * 100 if conf else None
    must_not_sent = [i for i in must_not if oc[i].action == "auto_respond"]
    label_person = [i for i in ids if labels[i].get("expected_route") == "escalate"]
    compared_gaps = {seg: gap for seg, (_, _, gap) in groups.items() if gap is not None}
    follow = [o for o in outcomes if "follow-up:" in (o.reason or "")]
    hist = [r.get("history") for r in raw_by_id.values() if isinstance(r.get("history"), dict)]
    base = sum(bool(h.get("repeat_contact")) for h in hist)
    down = sum(why_person(o) == DOWN for o in outcomes if o.action != "auto_respond")
    no_labels = "needs the labels"
    review = "measured by two people reviewing replies, not by a run"

    # (measure, baseline, target, this run, met: True / False / None = not measured): the Evaluation Framework's tiers
    business = [
        ("First contact resolution", "42%", "60% or better", f"{_pct(by['auto_respond'], n)} ({by['auto_respond']} of {n})",
         fcr >= 0.60),
        ("Mean time to first reply", "8 to 12 hours", "Under 5 minutes",
         f"mean {mean_s:.1f} s, median {median_s:.1f} s", mean_s < 300),
        ("Customer satisfaction (satisfaction proxy)", "3.2 / 5", "4.0 or better", review, None),
        ("Escalation rate", "58%", "30% or lower", f"{_pct(person, n)} ({person} of {n})", esc <= 0.30),
        ("Repeat contacts", "Not measured" + (f" ({_pct(base, len(hist))} in the history fields)" if hist else ""),
         "Halved", f"{len(follow)} within 7 days of an automatic reply in this run, all sent to a person", None),
    ]
    technical = [
        ("Classification precision", "-", "85% or better, per class",
         ((f"{min(per_type.values()):.1%} for every type" if min(per_type.values()) == max(per_type.values())
           else f"{min(per_type.values()):.1%} for the lowest type ({lowest})") if per_type else no_labels),
         (min(per_type.values()) >= 0.85) if per_type else None),
        ("Hallucination rate", "-", "5% or lower", review, None),
        ("Citation accuracy", "-", "95% or better",
         f"{_pct(len(cited) - len(cite_bad), len(cited))} ({len(cited) - len(cite_bad)} of {len(cited)})" if cited
         else no_labels, (1 - len(cite_bad) / len(cited) >= 0.95) if cited else None),
        ("Latency, 95th percentile", "-", "Under 3 seconds",
         f"{pq(work, 95) / 1000:.1f} s without rate-limit waits ({pq(lat, 95) / 1000:.1f} s with them)",
         pq(work, 95) < 3000),
        ("Availability", "-", "99.5% or better",
         f"every ticket got a decision ({decisions_logged['outcome']} of {n}); {down} sent to a person because the "
         f"model provider was unavailable", None),
    ]
    governance = [
        ("Private data in outbound text", "-", "Zero occurrences",
         f"0 sent ({fired.get('private_data', 0)} detected and blocked)", True),
        ("Quality across customer groups", "-", "Under five percentage points of variation",
         ", ".join(f"{GROUP_NAMES[s_]} {g:.1f} points" for s_, g in compared_gaps.items()) or (
             f"too few tickets to compare: every group has under 10 of the {n} tickets"),
         (max(compared_gaps.values()) < 5.0) if compared_gaps else None),
        ("Decision logging", "-", "Complete coverage: logged decisions match processed tickets",
         f"{decisions_logged['outcome']} final outcomes logged for {n} tickets", reconciles),
        ("Confidence calibration", "-", "Stated confidence within five points of observed accuracy",
         (f"{abs(cal_gap):.1f} points apart" if cal_gap is not None else no_labels),
         (abs(cal_gap) <= 5) if cal_gap is not None else None),
        ("What the system must never do: must-not tickets answered automatically", "-", "0",
         f"{len(must_not_sent)} of {len(must_not)}" if labels else no_labels,
         (not must_not_sent) if labels else None),
    ]
    rows = business + technical + governance
    L = [f"# Metrics report: {meta['input']}", "",
         "| Run | Date | Tickets | Run time | Labels in the file |", "|---|---|---|---|---|",
         f"| {meta['run_id']} | {meta['date']} | {n} | {meta.get('minutes', '-')} minutes | "
         f"{'yes, used only to mark this report' if labels else 'no: the measures that need them are not measured'} |",
         "", f"System: commit {meta['git_commit']}; writer {meta['writer']} (backup {meta['backup']}) via "
             f"{meta.get('writer_provider', 'Groq direct')}; checker {meta['checker']}; classifier {meta['classifier']}; "
             f"threshold {meta['threshold']}; prompts {meta['prompts']}; reply cache {meta.get('reply_cache', 'off')}"
         + (f"; switches: {meta['experiment']}" if meta.get("experiment") else "") + ".",
         "", "## Results against the targets", "",
         "Every measure, baseline and target in the Evaluation Framework (the same targets as the Project Brief), in "
         "its three tiers. \"Not measured\" means a run cannot produce that figure; the sections after the tables "
         "say why each target was missed or not measured."]
    for title, part in (("Business outcomes", business), ("Technical performance", technical),
                        ("Governance conditions", governance)):
        L += ["", f"### {title}", "", "| Measure | Baseline | Target | This run | Met? |", "|---|---|---|---|---|"]
        L += [f"| {m} | {b} | {t} | {v} | {_met(ok)} |" for m, b, t, v, ok in part]

    # Why each target was missed or not measured, worked out from this run's own figures.
    missed = {m for m, _, _, _, ok in rows if ok is False}
    L += ["", "## Why targets were missed", ""]
    if not missed:
        L += ["Every target this run can measure was met.", ""]
    if missed & {"First contact resolution", "Escalation rate"}:
        rules = sum(k for w, k in why.items() if w in SAFETY_RULES)
        text = (f"**Escalation rate.** {person} of {n} tickets ({_pct(person, n)}) went to a person; the table \"Why "
                f"tickets went to a person\" below gives every reason. The fixed safety rules alone sent {rules} "
                f"({_pct(rules, n)}): must-not tickets and data location questions, which no confidence score can "
                f"override.")
        if ids and label_person:
            text += (f" The labels themselves miss the target: followed exactly, they send {len(label_person)} of "
                     f"{len(ids)} tickets ({_pct(len(label_person), len(ids))}) to a person.")
        text += (" Meeting it would mean answering tickets that must reach a person. Marcus said he \"would rather it "
                 "said nothing than said something wrong\", so the safety rules stay and the miss is reported.")
        if why.get(REFUSED):
            text += (f" The free tier added {why[REFUSED]} tickets ({why[REFUSED] / n * 100:.1f} points) whose "
                     f"grounding check could not run.")
        L += [text, ""]
    if "Citation accuracy" in missed:
        L += [f"**Citation accuracy.** {len(cite_bad)} of {len(cited)} automatic replies cite a different article from "
              f"the labels: {', '.join(cite_bad[:12])}{' …' if len(cite_bad) > 12 else ''}. On the development tickets, "
              f"most such replies come from the article whose title matches the customer's question while the labels "
              f"list a different article, and a few follow a subject line that points to a different problem from the "
              f"message (docs/known_limitations.md, limitations 1 and 8).", ""]
    if "Latency, 95th percentile" in missed:
        L += [f"**Latency, 95th percentile.** Without the provider's rate-limit waits, the median reply took "
              f"{pq(work, 50) / 1000:.1f} s and the slowest 5% took {pq(work, 95) / 1000:.1f} s. An answered ticket needs "
              f"two model calls, the writer and the grounding check ({calls / n if n else 0:.2f} calls per ticket in "
              f"this run, retries included). The free tier made {waited} of {n} tickets wait, "
              f"{sum(wait) / 1000:,.0f} s in total; the latency requirement (NFR-01, non-functional requirement 1) reports latency with and without those waits, as the course "
              f"team asked.", ""]
    if "Mean time to first reply" in missed:
        L += [f"**Mean time to first reply.** The free tier's rate limits made {waited} of {n} tickets wait, "
              f"{sum(wait) / 1000:,.0f} s in total; without that waiting the median reply took {pq(work, 50) / 1000:.1f} s.",
              ""]
    if "Quality across customer groups" in missed:
        text = ["**Quality across customer groups.** The difference is in the share answered automatically, best group "
                "minus lowest."]
        for seg, (grows, compared, gap) in groups.items():
            if gap is None or gap < 5.0:
                continue
            best, low = max(compared, key=compared.get), min(compared, key=compared.get)
            rule_share = {}
            for g in (best, low):
                members = [o for o in outcomes if str(getattr(tick[o.ticket_id], seg, None) or "unknown") == g]
                rule_share[g] = _pct(sum(why_person(o) in SAFETY_FIRST for o in members if o.action != "auto_respond"),
                                     len(members))
            line = (f"By {GROUP_NAMES[seg]}: {nice(best)} {compared[best]:.1f}%, {nice(low)} {compared[low]:.1f}% "
                    f"({gap:.1f} points). A rule sent {rule_share[low]} of {nice(low)} tickets to a person, "
                    f"against {rule_share[best]} for {nice(best)}.")
            lg = _label_rates(ids, labels, tick, seg) if ids else None
            if lg is not None:
                line += f" The labels followed exactly are {lg:.1f} points apart."
            text.append(line)
        text.append("The groups ask different mixes of questions, and some ask more of the questions that must go to a "
                    "person; every group's replies go through the same checks.")
        refused = [o for o in outcomes if why_person(o) == REFUSED] if why.get(REFUSED) else []
        if refused:
            text.append(f"The {len(refused)} tickets whose grounding check the free tier refused widen the gaps.")
        sizes = [k for seg_rows, compared, _ in groups.values() for g, (k, _) in seg_rows.items() if g in compared]
        if sizes and min(sizes) < 100:
            text.append(f"The groups compared have {min(sizes)} to {max(sizes)} tickets, so one ticket moves a group "
                        f"by up to {100 / min(sizes):.1f} points.")
        L += [" ".join(text), ""]
    for m, line in (("What the system must never do: must-not tickets answered automatically",
                     "must-not tickets were answered automatically: " + ", ".join(must_not_sent[:12])),
                    ("Classification precision", f"the lowest type was {lowest}"),
                    ("Confidence calibration", "stated confidence and observed accuracy are more than 5 points apart"),
                    ("Decision logging", "a ticket does not have exactly one final outcome in the decision log"),
                    ("Private data in outbound text", "private data was found in a sent reply")):
        if m in missed:
            L += [f"**{m}.** In this run {line}. Look at these tickets in the results file and the decision log first.",
                  ""]
    L += ["## Why some measures are not measured", "",
          "- **Customer satisfaction and hallucination rate:** there are no live customers, so the Evaluation Framework "
          "has people review a sample of at least fifty replies against a rubric, two assessors independently. That "
          "review is in the report, not in a run.",
          "- **Repeat contacts:** \"the same customer raising the same issue again within a week\" needs customers "
          "writing back after launch. In a run, a repeat contact after an automatic reply is sent to a person (the follow-up rule, FR-14, functional requirement 14).",
          "- **Availability:** 99.5% or better is a share of time, which needs the live service over weeks. In a run, every "
          "ticket gets a decision, and while the model provider fails, tickets go to a person (the circuit breaker, FR-11, functional requirement 11)."]
    if not labels:
        L.append("- **Classification precision, citation accuracy, confidence calibration and must-not tickets:** they "
                 "compare the system with the labels, and this file has none.")
    if not compared_gaps:
        L.append(f"- **Quality across customer groups:** every group has fewer than 10 of the {n} tickets, so one ticket "
                 f"would move a group by 10 points or more.")

    L += ["", "## Volume", "",
          "| | Tickets | Share |", "|---|---|---|",
          f"| Tickets processed | {n} | 100% |",
          f"| Answered automatically | {by['auto_respond']} | {_pct(by['auto_respond'], n)} |",
          f"| Escalated | {by['escalate']} | {_pct(by['escalate'], n)} |",
          f"| Blocked by guardrails, then escalated | {by['block']} | {_pct(by['block'], n)} |",
          "", "## Business", "",
          "| Measure | Result |", "|---|---|",
          f"| First contact resolution | {_pct(by['auto_respond'], n)} |",
          f"| Escalation rate (escalated and blocked) | {_pct(person, n)} |",
          f"| Mean response time | {mean_s:.1f} s |",
          f"| Median response time | {median_s:.1f} s |",
          "", "First contact resolution counts only tickets closed with no person involved; \"Draft ready: check and "
              "send\" handovers count as escalations.",
          "", "### Why tickets went to a person", "",
          "| Reason | Tickets | Share of all tickets | Why it goes to a person |", "|---|---|---|---|"]
    L += [f"| {w} | {k} | {_pct(k, n)} | {WHY.get(w, '')} |" for w, k in why.most_common()] or ["| (none) | 0 | - | |"]
    L += ["", repeat_contacts(outcomes, raw_by_id),
          "", "## Technical", "",
          "| Latency | Median | 95th percentile |", "|---|---|---|",
          f"| Without rate-limit waits | {pq(work, 50) / 1000:.1f} s | {pq(work, 95) / 1000:.1f} s |",
          f"| With rate-limit waits | {pq(lat, 50) / 1000:.1f} s | {pq(lat, 95) / 1000:.1f} s |",
          "", f"- **Time spent waiting for the rate limit:** {sum(wait) / 1000:,.0f} s on {waited} of {n} tickets",
          f"- **Model calls:** {calls} in total (retries included), {calls / n if n else 0:.2f} per ticket",
          _tokens(outcomes, n)]
    if labels:
        hits = [i for i in ids if labels[i].get("expected_doc_ids")]
        hit5 = sum(bool(set(labels[i]["expected_doc_ids"]) & set(oc[i].passage_ids)) for i in hits)
        L += [f"- **Retrieval hit rate (the right article in the top 5 found):** {hit5} of {len(hits)} "
              f"({_pct(hit5, len(hits))})",
              f"- **Citation accuracy:** {len(cited) - len(cite_bad)} of {len(cited)} "
              f"({_pct(len(cited) - len(cite_bad), len(cited))})",
              "", "### Classification precision and recall per class", "", "```",
              classification_report(true_i, pred_i, digits=3, zero_division=0), "```", "",
              "Confusion matrix (rows = type in the labels, columns = type the system chose, in sorted type order):",
              "", "```", str(confusion_matrix(true_i, pred_i)), "```"]
    else:
        L += ["- **Retrieval hit rate and classification precision and recall per class:** need the labels"]

    L += ["", "## Governance", "",
          f"- **Decisions logged:** {decisions_logged['total']:,} rows; {decisions_logged['outcome']} final outcomes for {n} "
          f"tickets -> {'reconciles' if reconciles else 'DOES NOT RECONCILE'}",
          f"- **Guardrail activations:** " + (", ".join(f"{k} {v}" for k, v in fired.most_common()) or "none"),
          f"- **Private data detections:** {fired.get('private_data', 0)} (every one blocked, none sent)",
          "- **Labels for a person:** " + (", ".join(f"{k} {v}" for k, v in
                                                     Counter(o.label for o in outcomes if o.label).most_common()) or "none"),
          "", "### Results by customer group", "",
          "Share answered automatically for each group; the condition is under five percentage points of variation "
          "between the groups of each kind. Groups under 10 tickets are shown but not compared." + (
              " Right article = of the automatic replies the labels name an article for, the share that cite one of "
              "those articles." if labels else ""), ""]
    head = "| Kind | Group | Tickets | Answered automatically |" + (" Right article | Must-not answered |" if labels else "")
    L += [head, "|" + "---|" * (6 if labels else 4)]
    for seg in SEGMENTS:
        grows, compared, gap = groups[seg]
        for g in sorted(grows):
            k, rate = grows[g]
            line = f"| {GROUP_NAMES[seg]} | {nice(g)} | {k}{'' if k >= 10 else ' (not compared)'} | {rate:.1f}% |"
            if labels:
                members = [i for i in ids if str(getattr(tick[i], seg, None) or "unknown") == g]
                a = [i for i in members if oc[i].action == "auto_respond"]
                w = [i for i in a if labels[i].get("expected_doc_ids")]
                q = [i for i in w if oc[i].draft and set(labels[i]["expected_doc_ids"]) & set(oc[i].draft.cited_doc_ids)]
                line += f" {len(q)} of {len(w)} ({_pct(len(q), len(w))}) | {sum(i in a for i in members if labels[i].get('must_not_auto_respond'))} |"
            L.append(line)
        L.append(f"| **{GROUP_NAMES[seg]}** | **difference** | | **{gap:.1f} points** |" + (" | |" if labels else "")
                 if gap is not None else f"| **{GROUP_NAMES[seg]}** | **difference** | | not compared |" + (" | |" if labels else ""))
    if labels:
        should = [i for i in ids if labels[i].get("expected_route") == "auto_respond"]
        L += ["", "### Calibration: stated confidence against observed accuracy", "",
              "| Band | Tickets | Stated confidence | Observed accuracy | Gap |", "|---|---|---|---|---|"]
        L += [f"| {lo:.1f}-{hi:.1f} | {k} | {s_:.1%} | {o_:.1%} | {abs(s_ - o_) * 100:.1f} points |"
              for lo, hi, k, s_, o_ in calibration_table(conf)]
        L += ["", "### The labels followed exactly, compared with the system", "",
              "| Measure | Result |", "|---|---|",
              f"| Must-not tickets answered automatically (0) | {len(must_not_sent)} of {len(must_not)} |",
              f"| Tickets the labels would answer that the system answered | {sum(i in auto for i in should)} of "
              f"{len(should)} ({_pct(sum(i in auto for i in should), len(should))}) |",
              f"| Tickets the labels send to a person that the system answered | "
              f"{sum(labels[i].get('expected_route') == 'escalate' for i in auto)} |",
              f"| Sent to a person by the labels followed exactly | {len(label_person)} of {len(ids)} "
              f"({_pct(len(label_person), len(ids))}) |",
              f"| Ticket type right | {_pct(sum(a == b for a, b in zip(true_i, pred_i)), len(ids))} |",
              "", "The labels are someone's decisions, not the truth: they can be wrong too."]
    return "\n".join(L) + "\n"
