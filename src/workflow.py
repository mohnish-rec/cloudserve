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
import time
from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from src.generate import articles_for, generate, with_notice
from src.guardrails import check_reply
from src.ingest import is_blocked
from src.pipeline import AUTO, DRAFT_READY, ESCALATE, SPECIALIST, finish
from src.route import route
from src.safety import check


class TicketState(TypedDict, total=False):
    ticket: Any
    start: float
    c: Any            # classification
    s: Any            # safety result
    passages: list
    d: Any            # route decision
    draft: Any
    report: Any       # guardrail report
    outcome: Any      # the final Outcome


def build(classifier, retriever, now=None, kill_switch_file=None, call=None, sleep=None):
    kw = {k: v for k, v in (("call", call), ("sleep", sleep)) if v}

    def classify(st):
        t = st["ticket"]
        return {"c": classifier.classify("" if is_blocked(t) else t.text)}

    def check_rules(st):
        return {"s": check(st["ticket"].text, st["c"].intent)}

    def search(st):
        t = st["ticket"]
        return {"passages": [] if is_blocked(t) else retriever.search(t.text)}

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
        return {"report": check_reply(reply, st["draft"], arts, st["ticket"].text, st["c"].confidence,
                                      st["d"].threshold, **kw)}

    def after_validate(st):
        return "blocked" if st["report"].blocked else "send"

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
        return {"outcome": finish(st, AUTO, "", st["d"].reason, sent=with_notice(st["draft"], st["passages"]),
                                  reqs=("FR-05", "FR-08", "FR-09"))}

    g = StateGraph(TicketState)
    for name, fn in [("classify", classify), ("check_rules", check_rules), ("search", search), ("route", route_node),
                     ("write", write), ("validate", validate), ("handover", handover), ("blocked", blocked),
                     ("send", send)]:
        g.add_node(name, fn)
    g.set_entry_point("classify")
    g.add_edge("classify", "check_rules")
    g.add_edge("check_rules", "search")
    g.add_edge("search", "route")
    g.add_conditional_edges("route", after_route, {"handover": "handover", "write": "write"})
    g.add_conditional_edges("write", after_write, {"handover": "handover", "validate": "validate"})
    g.add_conditional_edges("validate", after_validate, {"blocked": "blocked", "send": "send"})
    for end in ("handover", "blocked", "send"):
        g.add_edge(end, END)
    return g.compile()


def run_ticket(ticket, classifier, retriever, **options):
    app = build(classifier, retriever, **options)
    final = app.invoke({"ticket": ticket, "start": time.perf_counter()})
    return final["outcome"]
