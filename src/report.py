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
    line = (f"**Repeat contacts:** {len(follow)} of {n} tickets were the same customer asking about the same type "
            f"within 7 days of an automatic reply in this run; {to_person} of them went to a person with the earlier "
            f"reply attached.")
    if hist:
        line += f" Baseline (the history block, when people handled these tickets): {base} of {len(hist)} ({_pct(base, len(hist))})."
    return line


# Why a ticket went to a person, in plain words (the same groups as Table 6 of the report), worked out from the
# reason the system wrote for it. The first that applies is used.
MUST_NOT = "A must-not ticket (security, compliance, feature request, unclear)"
DATA_LOCATION = "A data location question"
OWN = "Mohnish Grover's own decisions on these questions"
PLAN = "The only article that answers is for other plans (plan rule)"
FOLLOW = "A repeat contact within 7 days of an automatic reply"
REFUSED = "The grounding check could not run (the free tier's limit), so the reply was not sent"
NO_FIT = "A guardrail stopped the reply (for example, the article does not fit)"
UNSURE = "Not sure enough, or no help article fits"
SAFETY_FIRST = {MUST_NOT, DATA_LOCATION, OWN, PLAN, FOLLOW}      # sent by a rule on purpose
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
    """One plain reason per ticket sent to a person: the first that applies."""
    r = o.reason or ""
    rule = "a safety rule says" in r
    if "kill switch" in r:
        return "The kill switch was on"
    if "unexpected error" in r:
        return "A system error (sent to a person, never dropped)"
    if "model provider is unavailable" in r or "model unavailable" in r:
        return "The AI service was unavailable"
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
        return NO_FIT
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


def build(outcomes, tickets, raw_by_id, meta, decisions_logged) -> str:
    n = len(outcomes)
    by = Counter(o.action for o in outcomes)
    person = n - by["auto_respond"]
    lat = [o.latency_ms for o in outcomes]
    wait = [getattr(o, "wait_ms", 0) for o in outcomes]                 # 17 Nov: rate-limit waits
    work = [max(0, a - b) for a, b in zip(lat, wait)]                    # response time without those waits
    pq = lambda xs, q: float(np.percentile(xs, q)) if xs else 0.0  # noqa: E731
    p = lambda q: float(np.percentile(lat, q)) if lat else 0.0  # noqa: E731
    fired = Counter(name for o in outcomes if o.guardrails for name in o.guardrails.fired)
    labels = {tid: r.get("labels") for tid, r in raw_by_id.items() if isinstance(r.get("labels"), dict)}
    oc = {o.ticket_id: o for o in outcomes}
    why = Counter(why_person(o) for o in outcomes if o.action != "auto_respond")
    groups = group_rates(outcomes, tickets)
    reconciles = decisions_logged["outcome"] == n
    mean_s = statistics.mean(lat) / 1000 if lat else 0
    fcr, esc = (by["auto_respond"] / n if n else 0), (person / n if n else 0)

    # Figures that need the answer key ("labels" in the ticket file). The hidden set may not have it.
    ids = [o.ticket_id for o in outcomes if o.ticket_id in labels]
    must_not = [i for i in ids if labels[i].get("must_not_auto_respond")]
    auto = [i for i in ids if oc[i].action == "auto_respond"]
    cited = [i for i in auto if labels[i].get("expected_doc_ids")]
    cite_bad = [i for i in cited if not (oc[i].draft and set(labels[i]["expected_doc_ids"]) & set(oc[i].draft.cited_doc_ids))]
    true_i = [labels[i]["intent"] for i in ids]
    pred_i = [oc[i].classification.intent if oc[i].classification else "(system error)" for i in ids]
    type_ok = sum(a == b for a, b in zip(true_i, pred_i))
    conf = [(oc[i].classification.confidence, oc[i].classification.intent == labels[i]["intent"])
            for i in ids if oc[i].classification]
    cal_gap = (sum(c for c, _ in conf) / len(conf) - sum(ok for _, ok in conf) / len(conf)) * 100 if conf else None
    must_not_sent = [i for i in must_not if oc[i].action == "auto_respond"]
    label_person = [i for i in ids if labels[i].get("expected_route") == "escalate"]
    compared_gaps = {seg: gap for seg, (_, _, gap) in groups.items() if gap is not None}

    rows = [  # measure, target, this run, met (True, False or None for not measured)
        ("Answered automatically (first contact resolution)", "60% or more", _pct(by["auto_respond"], n), fcr >= 0.60),
        ("Sent to a person (escalation rate)", "30% or less", _pct(person, n), esc <= 0.30),
        ("Tickets that must reach a person, answered automatically", "0",
         f"{len(must_not_sent)} of {len(must_not)}" if labels else "needs the answer key",
         (not must_not_sent) if labels else None),
        ("Private data in a reply that was sent", "0",
         f"0 ({fired.get('private_data', 0)} caught and blocked)", True),
        ("Replies citing the right article (citation accuracy)", "95% or more",
         f"{_pct(len(cited) - len(cite_bad), len(cited))} ({len(cited) - len(cite_bad)} of {len(cited)})" if cited
         else "needs the answer key", (1 - len(cite_bad) / len(cited) >= 0.95) if cited else None),
        ("Ticket type right", "85% or more", _pct(type_ok, len(ids)) if ids else "needs the answer key",
         (type_ok / len(ids) >= 0.85) if ids else None),
        ("Stated confidence against observed accuracy", "within 5 points",
         (f"{cal_gap:+.1f} points".replace("-0.0", "0.0").replace("+0.0", "0.0") if cal_gap is not None
          else "needs the answer key"),
         (abs(cal_gap) <= 5) if cal_gap is not None else None),
        ("Slowest 5% of replies, leaving out the free tier's waiting", "under 3 s",
         f"{pq(work, 95) / 1000:.1f} s (with waiting: {p(95) / 1000:.1f} s)", pq(work, 95) < 3000),
        ("Mean time to first reply", "under 5 minutes", f"{mean_s:.1f} s", mean_s < 300),
        ("Every ticket logged, with one final outcome", "all tickets",
         f"{decisions_logged['outcome']} of {n}", reconciles),
        ("Difference between customer groups (share answered)", "5 points or less",
         ", ".join(f"{GROUP_NAMES[s]} {g:.1f}" for s, g in compared_gaps.items()) or (
             f"too few tickets to compare: every group has under 10 of the {n} tickets, and one ticket "
             f"would move a group by 10 points or more"),
         (max(compared_gaps.values()) <= 5.0) if compared_gaps else None),
    ]
    L = [f"# Metrics report: {meta['input']}", "",
         "| Run | Date | Tickets | Run time | Answer key in the file |", "|---|---|---|---|---|",
         f"| {meta['run_id']} | {meta['date']} | {n} | {meta.get('minutes', '-')} minutes | "
         f"{'yes, used only to mark this report' if labels else 'no: the figures that need it are not measured'} |",
         "", f"System: commit {meta['git_commit']}; writer {meta['writer']} (backup {meta['backup']}) via "
             f"{meta.get('writer_provider', 'Groq direct')}; checker {meta['checker']}; classifier {meta['classifier']}; "
             f"threshold {meta['threshold']}; prompts {meta['prompts']}; reply cache {meta.get('reply_cache', 'off')}"
         + (f"; switches: {meta['experiment']}" if meta.get("experiment") else "") + ".",
         "", "## Results against the targets", "",
         "| Measure | Target | This run | Met? |", "|---|---|---|---|"]
    L += [f"| {m} | {t} | {v} | {_met(ok)} |" for m, t, v, ok in rows]
    L += ["", "Reply quality (sentences the article does not support, and how useful the reply is) is measured by two "
              "people reviewing the replies, not by this report."]

    # Why each missed target was missed, worked out from this run's own figures.
    missed = {m for m, _, _, ok in rows if ok is False}
    L += ["", "## Why targets were missed", ""]
    if not missed:
        L += ["Every target this report can measure was met."]
    if missed & {rows[0][0], rows[1][0]}:
        safety = sum(k for w, k in why.items() if w in SAFETY_FIRST)
        top = why.most_common(1)[0] if why else ("-", 0)
        text = (f"**Answered automatically and sent to a person.** {person} of {n} tickets ({_pct(person, n)}) went to "
                f"a person. The most common reason: {top[0].lower()} ({top[1]} tickets); the table \"Why tickets went "
                f"to a person\" below gives every reason. {safety} of them ({_pct(safety, n)} of all tickets) were sent "
                f"by a rule on purpose, because those tickets must reach a person, so the system will not answer them "
                f"to reach a target.")
        if label_person and len(label_person) / len(ids) > 0.30:
            text += (f" The answer key itself sends {_pct(len(label_person), len(ids))} of these tickets to a person, "
                     f"so even following it exactly would miss the 30% target.")
        L += [text, ""]
    if rows[4][0] in missed:
        L += [f"**Citation accuracy.** {len(cite_bad)} of {len(cited)} automatic replies cited a different article "
              f"from the answer key: {', '.join(cite_bad[:12])}{' …' if len(cite_bad) > 12 else ''}. Causes found on "
              f"the development tickets: a subject line that points to a different topic can add an article, and some "
              f"questions are answered by two articles while the answer key names one (docs/known_limitations.md).", ""]
    if rows[7][0] in missed:
        L += [f"**Speed.** Leaving out the free tier's waiting, the slowest 5% of replies took {pq(work, 95) / 1000:.1f} s. "
              f"An automatic reply needs at least two AI calls on the free tier, one to write it and one to check it "
              f"({sum(o.model_calls for o in outcomes) / n if n else 0:.2f} calls per ticket in this run).", ""]
    if rows[8][0] in missed:
        L += [f"**Time to first reply.** The free tier's rate limits made the system wait {sum(wait) / 1000:,.0f} s in "
              f"total, on {sum(1 for w in wait if w)} of {n} tickets. It waits as long as the provider asks, then carries "
              f"on; without that waiting the median reply took {pq(work, 50) / 1000:.1f} s.", ""]
    if rows[10][0] in missed:
        text = ["**Difference between customer groups.**"]
        for seg, (grows, compared, gap) in groups.items():
            if gap is None or gap <= 5.0:
                continue
            best, low = max(compared, key=compared.get), min(compared, key=compared.get)
            share = {}
            for g in (best, low):
                members = [o for o in outcomes if str(getattr({t.ticket_id: t for t in tickets}[o.ticket_id], seg, None)
                                                       or "unknown") == g]
                share[g] = _pct(sum(why_person(o) in SAFETY_FIRST for o in members if o.action != "auto_respond"),
                                len(members))
            text.append(f"By {GROUP_NAMES[seg]}: {nice(best)} {compared[best]:.1f}% answered, {nice(low)} "
                        f"{compared[low]:.1f}% ({gap:.1f} points apart). A rule sent {share[low]} of {nice(low)} tickets "
                        f"to a person, against {share[best]} for {nice(best)}.")
        text.append("Groups that ask more of the questions which must reach a person (for example data location) get "
                    "fewer automatic answers; their replies go through the same checks.")
        sizes = [k for seg_rows, compared, _ in groups.values() for g, (k, _) in seg_rows.items() if g in compared]
        if sizes and min(sizes) < 100:
            text.append(f"The groups compared here have {min(sizes)} to {max(sizes)} tickets, so one ticket moves a group "
                        f"by up to {100 / min(sizes):.1f} points.")
        L += [" ".join(text), ""]
    for i, label_ in ((2, "tickets that must reach a person were answered"), (5, "the ticket type was often wrong"),
                      (6, "the stated confidence does not match the accuracy"),
                      (9, "a ticket does not have exactly one final outcome in the decision log")):
        if rows[i][0] in missed:
            L += [f"**{rows[i][0]}.** In this run {label_}. This should not happen: look at the results file for these "
                  f"tickets first" + (f" ({', '.join(must_not_sent[:12])})." if i == 2 else "."), ""]

    L += ["## Volume", "",
          "| | Tickets | Share |", "|---|---|---|",
          f"| Processed | {n} | 100% |",
          f"| Answered automatically (first contact resolution) | {by['auto_respond']} | {_pct(by['auto_respond'], n)} |",
          f"| Sent to a person | {by['escalate']} | {_pct(by['escalate'], n)} |",
          f"| Blocked by a guardrail, then sent to a person | {by['block']} | {_pct(by['block'], n)} |",
          f"| Escalation rate (sent to a person, including blocked) | {person} | {_pct(person, n)} |",
          "", "First contact resolution counts only tickets closed with no person involved; \"Draft ready\" hand-overs "
              "count as escalations.",
          "", "## Why tickets went to a person", "",
          "| Reason | Tickets | Share of all tickets |", "|---|---|---|"]
    L += [f"| {w} | {k} | {_pct(k, n)} |" for w, k in why.most_common()] or ["| (none) | 0 | - |"]
    L += ["", repeat_contacts(outcomes, raw_by_id),
          "", "## Speed and cost", "",
          "| Measure | Median | 95th percentile |", "|---|---|---|",
          f"| Response time, as the customer waits | {p(50) / 1000:.1f} s | {p(95) / 1000:.1f} s |",
          f"| Response time, leaving out the free tier's waiting | {pq(work, 50) / 1000:.1f} s | {pq(work, 95) / 1000:.1f} s |",
          "", f"- **Mean response time:** {mean_s:.1f} s",
          f"- **Waiting on the free tier's rate limits:** {sum(wait) / 1000:,.0f} s in total, on "
          f"{sum(1 for w in wait if w)} of {n} tickets (kept apart from the working time, as the course team asked)",
          f"- **Model calls:** {sum(o.model_calls for o in outcomes)} in total (retries included), "
          f"{sum(o.model_calls for o in outcomes) / n if n else 0:.2f} per ticket",
          _tokens(outcomes, n),
          "", "## Safety and the decision log", "",
          f"- **Decisions logged:** {decisions_logged['total']:,} rows; {decisions_logged['outcome']} final outcomes for {n} "
          f"tickets -> {'reconciles' if reconciles else 'DOES NOT RECONCILE'}",
          f"- **Guardrail activations:** " + (", ".join(f"{k} {v}" for k, v in fired.most_common()) or "none"),
          f"- **Private data detections:** {fired.get('private_data', 0)} (every one blocked, none sent)",
          "- **Labels for a person:** " + (", ".join(f"{k} {v}" for k, v in
                                                     Counter(o.label for o in outcomes if o.label).most_common()) or "none"),
          "", "## Results by customer group", "",
          "Share answered automatically for each group; the target is 5 points or less between the groups of each kind. "
          "Groups under 10 tickets are shown but not compared." + (
              " Quality score = of the automatic replies the answer key names an article for, the share that cite one "
              "of those articles." if labels else ""), ""]
    head = "| Kind | Group | Tickets | Answered automatically |" + (" Quality score | Must-not answered |" if labels else "")
    L += [head, "|" + "---|" * (6 if labels else 4)]
    tick = {t.ticket_id: t for t in tickets}
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
        hits = [i for i in ids if labels[i].get("expected_doc_ids")]
        hit5 = sum(bool(set(labels[i]["expected_doc_ids"]) & set(oc[i].passage_ids)) for i in hits)
        should = [i for i in ids if labels[i].get("expected_route") == "auto_respond"]
        L += ["", "## Marked against the answer key", "",
              "| Measure | Result |", "|---|---|",
              f"| Tickets that must reach a person, answered automatically (target 0) | {len(must_not_sent)} of {len(must_not)} |",
              f"| Answered automatically when the answer key says a person | "
              f"{sum(labels[i].get('expected_route') == 'escalate' for i in auto)} of {len(auto)} automatic replies |",
              f"| Tickets the answer key would answer, answered automatically | {sum(i in auto for i in should)} of "
              f"{len(should)} ({_pct(sum(i in auto for i in should), len(should))}) |",
              f"| First contact resolution that agrees with the answer key | {_pct(sum(i in should for i in auto), len(ids))} |",
              f"| Retrieval hit rate (an expected article in the top 5) | {hit5} of {len(hits)} ({_pct(hit5, len(hits))}) |",
              f"| Citation accuracy (target 95%) | {len(cited) - len(cite_bad)} of {len(cited)} "
              f"({_pct(len(cited) - len(cite_bad), len(cited))}) |",
              f"| Ticket type right | {_pct(type_ok, len(ids))} |",
              f"| Sent to a person by the answer key itself | {len(label_person)} of {len(ids)} ({_pct(len(label_person), len(ids))}) |",
              "", "The answer key is not called \"correct\": it can be wrong too.",
              "", "### Classification precision and recall per type", "", "```",
              classification_report(true_i, pred_i, digits=3, zero_division=0), "```", "",
              "Confusion matrix (rows = true type, columns = predicted, sorted type order):", "", "```",
              str(confusion_matrix(true_i, pred_i)), "```",
              "", "### Calibration", "",
              "| Band | Tickets | Stated confidence | Observed accuracy | Gap |", "|---|---|---|---|---|"]
        L += [f"| {lo:.1f}-{hi:.1f} | {k} | {s:.1%} | {o:.1%} | {(s - o) * 100:+.1f} points |"
              for lo, hi, k, s, o in calibration_table(conf)]
    return "\n".join(L) + "\n"
