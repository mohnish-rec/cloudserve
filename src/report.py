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
    return (f"- **Reply cache (D-025):** {t['writer_cached']} of {writes} replies and {t['checker_cached']} of {checks} "
            f"checks reused, with no model call\n"
            f"- **Tokens:** writer {t['writer_in']:,} in + {t['writer_out']:,} out "
            f"({per:,.0f} per reply written); checker {t['checker_in']:,} in + {t['checker_out']:,} out; "
            f"total {t_tokens:,} ({t_tokens / n if n else 0:,.0f} per ticket)")


def build(outcomes, tickets, raw_by_id, meta, decisions_logged) -> str:
    n = len(outcomes)
    by = Counter(o.action for o in outcomes)
    lat = [o.latency_ms for o in outcomes]
    p = lambda q: float(np.percentile(lat, q)) if lat else 0.0  # noqa: E731
    fired = Counter(name for o in outcomes if o.guardrails for name in o.guardrails.fired)
    labels = {tid: r.get("labels") for tid, r in raw_by_id.items() if isinstance(r.get("labels"), dict)}
    L = [
        f"# Metrics report: {meta['input']}", "",
        f"- **Run:** {meta['run_id']} · {meta['date']} · {n} tickets",
        f"- **System version:** commit {meta['git_commit']} · prompts {meta['prompts']} · writer {meta['writer']} "
        f"(backup {meta['backup']}) via {meta.get('writer_provider', 'Groq direct')} · checker {meta['checker']} · "
        f"classifier {meta['classifier']} · "
        f"threshold {meta['threshold']} · reply cache {meta.get('reply_cache', 'off')}"
        + (f" · experiment: {meta['experiment']}" if meta.get("experiment") else ""),
        f"- **Answer key in the file:** {'yes, used only to mark this report' if labels else 'no: accuracy figures not available'}",
        "", "## Volume", "",
        "| Processed | Answered automatically | Escalated | Blocked by guardrails |", "|---|---|---|---|",
        f"| {n} | {by['auto_respond']} ({_pct(by['auto_respond'], n)}) | {by['escalate']} ({_pct(by['escalate'], n)}) | "
        f"{by['block']} ({_pct(by['block'], n)}) |",
        "", "## Business", "",
        "| First contact resolution | Escalation rate | Mean response time | Median response time |", "|---|---|---|---|",
        f"| {_pct(by['auto_respond'], n)} | {_pct(n - by['auto_respond'], n)} | "
        f"{statistics.mean(lat) / 1000 if lat else 0:.1f} s | {statistics.median(lat) / 1000 if lat else 0:.1f} s |",
        "", "First contact resolution counts only tickets closed with no person involved; "
        "\"Draft ready\" hand-overs count as escalations (FR-07).",
        "", "## Technical", "",
        f"- **Latency:** median {p(50) / 1000:.1f} s, 95th percentile {p(95) / 1000:.1f} s (target: under 3 s for 95%, NFR-01)",
        f"- **Model calls:** {sum(o.model_calls for o in outcomes)} in total (retries included), "
        f"{sum(o.model_calls for o in outcomes) / n if n else 0:.2f} per ticket",
        _tokens(outcomes, n),
        f"- **Decisions logged:** {decisions_logged['total']} rows; {decisions_logged['outcome']} final outcomes for {n} tickets "
        f"-> {'reconciles' if decisions_logged['outcome'] == n else 'DOES NOT RECONCILE'} (A8)",
        f"- **Guardrail activations:** " + (", ".join(f"{k} {v}" for k, v in fired.most_common()) or "none"),
        f"- **Private data detections:** {fired.get('private_data', 0)} (every one blocked, none sent)",
        f"- **Labels:** " + ", ".join(f"{k} {v}" for k, v in Counter(o.label or 'sent' for o in outcomes).most_common()),
    ]
    if labels:
        ids = [o.ticket_id for o in outcomes if o.ticket_id in labels]
        oc = {o.ticket_id: o for o in outcomes}
        true_i = [labels[i]["intent"] for i in ids]
        # A ticket that hit a system error has no classification: counted as wrong, never skipped.
        pred_i = [oc[i].classification.intent if oc[i].classification else "(system error)" for i in ids]
        must_not = [i for i in ids if labels[i].get("must_not_auto_respond")]
        should = [i for i in ids if labels[i].get("expected_route") == "auto_respond"]
        auto = [i for i in ids if oc[i].action == "auto_respond"]
        hits = [i for i in ids if labels[i].get("expected_doc_ids")]
        hit5 = sum(bool(set(labels[i]["expected_doc_ids"]) & set(oc[i].passage_ids)) for i in hits)
        cited = [i for i in auto if labels[i].get("expected_doc_ids")]
        cite_ok = sum(bool(oc[i].draft and set(labels[i]["expected_doc_ids"]) & set(oc[i].draft.cited_doc_ids)) for i in cited)
        L += ["", "## Marked against the answer key", "",
              f"- **Must-not tickets answered automatically:** {sum(oc[i].action == 'auto_respond' for i in must_not)} "
              f"of {len(must_not)} (target 0)",
              f"- **Answered automatically when the answer key says a person:** "
              f"{sum(labels[i].get('expected_route') == 'escalate' for i in auto)} of {len(auto)} automatic replies",
              f"- **Should-be-automatic tickets answered automatically:** {sum(i in auto for i in should)} of {len(should)} "
              f"({_pct(sum(i in auto for i in should), len(should))})",
              f"- **Correct first contact resolution** (answered, and the answer key agrees): "
              f"{_pct(sum(i in should for i in auto), len(ids))}",
              f"- **Retrieval hit rate** (an expected article in the top 5): {hit5} of {len(hits)} ({_pct(hit5, len(hits))})",
              f"- **Citation accuracy** (automatic replies citing an expected article): {cite_ok} of {len(cited)} "
              f"({_pct(cite_ok, len(cited))}; target 95%)",
              f"- **Type accuracy:** {_pct(sum(a == b for a, b in zip(true_i, pred_i)), len(ids))}",
              "", "### Classification precision and recall per type", "", "```",
              classification_report(true_i, pred_i, digits=3, zero_division=0), "```", "",
              "Confusion matrix (rows = true type, columns = predicted, sorted type order):", "", "```",
              str(confusion_matrix(true_i, pred_i)), "```",
              "", "### Calibration (Evaluation Framework)", "",
              "| Band | Tickets | Stated confidence | Observed accuracy | Gap |", "|---|---|---|---|---|"]
        cal = calibration_table([(oc[i].classification.confidence, oc[i].classification.intent == labels[i]["intent"])
                                 for i in ids if oc[i].classification])
        L += [f"| {lo:.1f}-{hi:.1f} | {k} | {s:.1%} | {o:.1%} | {(s - o) * 100:+.1f} points |" for lo, hi, k, s, o in cal]
        L += ["", "### Results by customer group (NFR-06: under 5 points between groups)", "",
              "Resolution rate = answered automatically. Quality score = share of automatic replies that cite an "
              "expected article and passed every guardrail. Groups under 10 tickets are shown but not compared.", "",
              "| Group | Value | Tickets | Resolution rate | Quality score | Must-not answered |", "|---|---|---|---|---|---|"]
        tick = {t.ticket_id: t for t in tickets}
        for seg in SEGMENTS:
            groups = defaultdict(list)
            for i in ids:
                groups[getattr(tick[i], seg)].append(i)
            for g, members in sorted(groups.items()):
                a = [i for i in members if oc[i].action == "auto_respond"]
                q = [i for i in a if labels[i].get("expected_doc_ids") and oc[i].draft
                     and set(labels[i]["expected_doc_ids"]) & set(oc[i].draft.cited_doc_ids)]
                L.append(f"| {seg.replace('customer_', '')} | {g} | {len(members)} | {_pct(len(a), len(members))} | "
                         f"{_pct(len(q), len(a))} | {sum(labels[i].get('must_not_auto_respond') and i in a for i in members)} |")
    return "\n".join(L) + "\n"
