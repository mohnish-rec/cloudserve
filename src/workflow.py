"""The orchestrated workflow (Module 7): every stage is a node, every branch is an edge in LangGraph.

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.

    classify -> check_rules -> search -> route --(safety rule / no article / unusable)--> handover
                                              \\--> write --(routed to a person)--------> handover (with draft)
                                                        \\--(no answer / unreadable)----> handover
                                                         \\--> validate --(blocked)----> blocked
                                                                       \\--(passed)----> send
Bounded: no loops, at most eight steps per ticket, so a ticket can never cycle (Module 7: bounded
autonomy). The model never chooses the path: every branch is decided by code from the stage results.
One state per ticket, keyed by the ticket ID, which is also the trace ID in the decision log (FR-10).
"""
import os
import time
from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from src.generate import articles_for, generate, with_notice
from src.guardrails import check_reply, trim
from src.ingest import is_blocked
from src.retrieve import search_typed, type_aware
from src.pipeline import AUTO, DRAFT_READY, ESCALATE, SPECIALIST, finish
from src.route import route
from src import decisions, followups, plans
from src.safety import SafetyResult, check


class TicketState(TypedDict, total=False):
    ticket: Any
    start: float
    c: Any            # classification
    s: Any            # safety result
    passages: list
    d: Any            # route decision
    draft: Any
    report: Any       # guardrail report
    trimmed: str      # 10 Nov: which sentences were removed before the reply was sent
    outcome: Any      # the final Outcome


def build(classifier, retriever, now=None, kill_switch_file=None, call=None, sleep=None):
    kw = {k: v for k, v in (("call", call), ("sleep", sleep)) if v}
    has_vectors = hasattr(retriever, "vectors")       # a test retriever may not have them
    # Looked up once here: LangGraph inspects each step's code, and a test classifier has no embed (10 Nov, 14 Nov).
    embed = getattr(classifier, "embed", None)

    def classify(st):
        t = st["ticket"]
        return {"c": classifier.classify("" if is_blocked(t) else t.text)}

    def check_rules(st):
        t = st["ticket"]
        s = check(t.text, st["c"].intent)
        # 14 Nov 2026: Mohnish Grover's decisions, learned from the 500 development tickets (src/decisions.py). It can
        # only add a handover; a test classifier without embeddings skips it.
        prior = None if is_blocked(t) else followups.earlier(t, st["c"].intent)
        if prior is not None and not s.must_go_to_person:            # 14 Nov: Mohnish Grover's follow-up rule
            s = SafetyResult(True, s.reasons + (followups.reason(prior),))
        if decisions.enabled() and not s.must_go_to_person and not is_blocked(t) and embed is not None:
            p = decisions.person_probability(embed([decisions.text_of(t)])[0])   # message only (14 Nov)
            if p >= decisions.THRESHOLD:
                s = SafetyResult(True, s.reasons + (decisions.reason(p),))
        return {"s": s}

    def search(st):
        t = st["ticket"]
        if is_blocked(t):
            return {"passages": []}
        if type_aware() and has_vectors:                      # 11 Nov, non-fluent tickets (see src/retrieve.py)
            return {"passages": search_typed(retriever, t.text, st["c"].intent)}
        return {"passages": retriever.search(t.text)}

    def route_node(st):
        t = st["ticket"]
        return {"d": route(t.text, st["c"], st["s"], st["passages"], received_at=t.received_at, now=now,
                           kill_switch_file=kill_switch_file)}

    def after_route(st):
        # A safety rule, an unusable ticket or no article: to a person with no model call (NFR-07).
        return "handover" if (st["s"].must_go_to_person or st["c"].fallback or not st["passages"]) else "write"

    def write(st):
        return {"draft": generate(st["ticket"].text, st["c"].intent, st["passages"], **kw)}

    def after_write(st):
        if st["d"].action == ESCALATE or not st["draft"].ok:
            return "handover"
        return "validate"

    def validate(st):
        reply = with_notice(st["draft"], st["passages"])
        arts = {a["doc_id"]: a for a in articles_for(st["passages"])}
        report = check_reply(reply, st["draft"], arts, st["ticket"].text, st["c"].confidence,
                             st["d"].threshold, **kw)
        # 10 Nov, experiment 1B (on by default from 12 Nov): remove only the failed sentences, then check the
        # WHOLE reply again. TRIM_UNSUPPORTED=off turns it off.
        if report.blocked and os.getenv("TRIM_UNSUPPORTED", "on") == "on":
            short = trim(st["draft"], report)
            if short is not None:
                again = check_reply(with_notice(short, st["passages"]), short, arts, st["ticket"].text,
                                    st["c"].confidence, st["d"].threshold, **kw)
                if not again.blocked:
                    gone = len(st["draft"].sentences) - len(short.sentences)
                    return {"report": again, "draft": short,
                            "trimmed": f"{gone} of {len(st['draft'].sentences)} sentences removed "
                                       f"({'; '.join(c.name for c in report.checks if not c.passed)}), then re-checked"}
        return {"report": report}

    def after_validate(st):
        if st["report"].blocked:
            return "blocked"
        return "plan" if plan_excluded(st) else "send"

    def plan_excluded(st):
        """15 Nov 2026, Mohnish Grover's plan rule (src/plans.py)."""
        if not plans.enabled():
            return None
        arts = {a["doc_id"]: a for a in articles_for(st["passages"])}
        return plans.excluded(st["ticket"].customer_tier, st["draft"].cited_doc_ids, arts)

    def plan(st):
        doc_id, applies = plan_excluded(st)
        return {"outcome": finish(st, ESCALATE, DRAFT_READY,
                                  plans.reason(doc_id, applies, st["ticket"].customer_tier, DRAFT_READY),
                                  reqs=("FR-07",))}

    def handover(st):
        d, draft = st["d"], st.get("draft")
        if draft is None:                                   # never written: safety rule, no article, unusable
            return {"outcome": finish(st, ESCALATE, SPECIALIST, d.reason)}
        if d.action == ESCALATE:                            # e.g. confidence just under the threshold
            label = DRAFT_READY if (d.label == DRAFT_READY and draft.ok) else SPECIALIST
            return {"outcome": finish(st, ESCALATE, label, d.reason)}
        return {"outcome": finish(st, ESCALATE, SPECIALIST, f"Sent to a person ({SPECIALIST}) because {draft.error}.",
                                  reqs=("FR-05",))}

    def blocked(st):
        why = "; ".join(f"{x.name}: {x.detail}" for x in st["report"].checks if not x.passed)
        return {"outcome": finish(st, "block", SPECIALIST,
                                  f"Reply blocked by a guardrail and sent to a person ({SPECIALIST}): {why}.",
                                  reqs=("FR-09",))}

    def send(st):
        why = st["d"].reason + (f" Trimmed: {st['trimmed']}." if st.get("trimmed") else "")
        followups.remember(st["ticket"], st["c"].intent, with_notice(st["draft"], st["passages"]))
        return {"outcome": finish(st, AUTO, "", why, sent=with_notice(st["draft"], st["passages"]),
                                  reqs=("FR-05", "FR-08", "FR-09"))}

    g = StateGraph(TicketState)
    for name, fn in [("classify", classify), ("check_rules", check_rules), ("search", search), ("route", route_node),
                     ("write", write), ("validate", validate), ("handover", handover), ("blocked", blocked),
                     ("send", send), ("plan", plan)]:
        g.add_node(name, fn)
    g.set_entry_point("classify")
    g.add_edge("classify", "check_rules")
    g.add_edge("check_rules", "search")
    g.add_edge("search", "route")
    g.add_conditional_edges("route", after_route, {"handover": "handover", "write": "write"})
    g.add_conditional_edges("write", after_write, {"handover": "handover", "validate": "validate"})
    g.add_conditional_edges("validate", after_validate, {"blocked": "blocked", "send": "send", "plan": "plan"})
    for end in ("handover", "blocked", "send", "plan"):
        g.add_edge(end, END)
    return g.compile()


def run_ticket(ticket, classifier, retriever, **options):
    app = build(classifier, retriever, **options)
    final = app.invoke({"ticket": ticket, "start": time.perf_counter()})
    return final["outcome"]
