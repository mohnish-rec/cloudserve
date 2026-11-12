"""One ticket through every stage: classify, safety rules, search, route, write, guardrails, outcome.

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
Day 4 built this as one plain function; on 9 Nov the same stages moved into the LangGraph
workflow (src/workflow.py, Module 7). This module keeps the outcome, hand-over and acknowledgement.

Every ticket ends in exactly one outcome (Build Specification: "Every ticket produces either
a sent answer or a logged escalation. None are silently dropped."):
  auto_respond  the reply passed all five guardrails and is sent (FR-05, FR-08, FR-09)
  block         a guardrail blocked the reply; the ticket goes to a person (FR-09)
  escalate      routing sent it to a person (FR-03, FR-06, FR-07)
Anything that goes to a person carries the hand-over (FR-07) and the customer gets the
acknowledgement straight away.
"""
import time
from dataclasses import dataclass, field

from src.classify import Classification
from src.generate import Draft, articles_for, generate, render, with_notice
from src.guardrails import Report, check_reply
from src.ingest import is_blocked
from src.route import AUTO, DRAFT_READY, ESCALATE, SPECIALIST, RouteDecision, route
from src.safety import check

ACKNOWLEDGEMENT = ("Thanks for getting in touch. A member of our support team has your ticket and will "
                   "reply to you directly.")     # FR-07: fixed text, no promise of time or outcome


@dataclass
class Outcome:
    ticket_id: str
    action: str                       # auto_respond, escalate or block
    label: str                        # "" when sent, else DRAFT_READY or SPECIALIST
    priority: str
    reason: str                       # one sentence a support manager can read
    sent_text: str                    # what the customer receives: the reply, or the acknowledgement
    handover: dict = None             # for a person: summary, tried, article, draft, unsure
    classification: Classification = None
    route: RouteDecision = None
    draft: Draft = None
    guardrails: Report = None
    passage_ids: tuple = ()           # the articles search found, best first
    model_calls: int = 0
    latency_ms: int = 0
    requirement_ids: tuple = field(default_factory=tuple)
    tokens: dict = field(default_factory=dict)   # {"writer_in", "writer_out", "checker_in", "checker_out"}
    sources: tuple = ()               # 11 Nov: every passage search found: doc_id, rank, scores, the passage itself


def citation_trail(draft, sources) -> list:
    """11 Nov (A6, Ines): for each cited article, its title, best search score, the passages search found in it, and
    the sentences it supports, so a reader can follow every citation to the passage and see what it backs."""
    if draft is None or not draft.ok:
        return []
    from src.generate import _pieces, _title
    trail = {}
    for k, s in enumerate(draft.sentences, 1):
        for d in dict.fromkeys(s["doc_ids"]):
            found = [x for x in sources if x["doc_id"] == d]
            t = trail.setdefault(d, {"doc_id": d, "title": _title(d), "score": max((x["score"] for x in found), default=None),
                                     "passages": [x["passage"] for x in found], "sentences": []})
            t["sentences"] += [f"{k}. {p}" for p in _pieces(s["text"])]
    return list(trail.values())


def _handover(ticket, c, s, passages, d, draft, why, report=None):
    """FR-07's five parts. The draft is for the agent to check, never sent as it is."""
    tried = [f"classified as {c.intent} ({c.confidence:.0%} sure)"]
    tried.append("safety rules: " + ("; ".join(s.reasons) if s.reasons else "none fired"))
    tried.append("search: " + (", ".join(p.doc_id for p in passages) if passages else "no relevant article"))
    if draft is not None:
        tried.append("reply drafted" if draft.ok else f"reply not drafted ({draft.error})")
    return {
        "summary": (draft.summary if draft is not None and draft.summary else
                    f"{ticket.channel} ticket, type {c.intent}, priority {d.priority}"),
        "tried": tried,
        "article": passages[0].doc_id if passages else "",
        # No draft for the agent when it held private data or came from an attack on the system.
        "draft": render(draft, passages) if draft is not None and draft.ok and not (report and {"private_data", "instruction_integrity"}
                                                                        & set(report.fired)) else "",
        "unsure": "; ".join(x for x in [why, draft.unsure_about if draft is not None else ""] if x),
    }


def finish(state, action, label, reason, sent=ACKNOWLEDGEMENT, reqs=()) -> Outcome:
    """Build the one final outcome for a ticket from whatever stages ran (used by the workflow's end nodes)."""
    ticket, c, s, d = state["ticket"], state["c"], state["s"], state["d"]
    passages, draft, report = state.get("passages") or [], state.get("draft"), state.get("report")
    calls = (draft.calls if draft is not None else 0) + (
        1 if report is not None and any(x.name == "grounding_model" and not x.detail.startswith("not run")
                                        and not x.cached and not x.memo for x in report.checks) else 0)
    chk = next((x for x in (report.checks if report else []) if x.name == "grounding_model"), None)
    tokens = {"writer_in": draft.tokens_in if draft else 0, "writer_out": draft.tokens_out if draft else 0,
              "checker_in": chk.tokens_in if chk else 0, "checker_out": chk.tokens_out if chk else 0,
              "writer_cached": int(bool(draft and draft.cached)), "checker_cached": int(bool(chk and chk.cached))}
    return Outcome(ticket.ticket_id, action, label, d.priority, reason, sent,
                   None if action == AUTO else _handover(ticket, c, s, passages, d, draft, reason, report),
                   c, d, draft, report, tuple(p.doc_id for p in passages), calls,
                   int((time.perf_counter() - state["start"]) * 1000),
                   tuple(dict.fromkeys(d.requirement_ids + tuple(reqs))), tokens,
                   tuple({"doc_id": p.doc_id, "rank": p.rank, "score": round(float(p.similarity), 3),
                          "keyword": round(float(p.keyword), 3), "passage": p.text[:400]} for p in passages))


def process(ticket, classifier, retriever, now=None, kill_switch_file=None, call=None, sleep=None) -> Outcome:
    """One ticket through the LangGraph workflow (src/workflow.py, Module 7)."""
    from src.workflow import run_ticket
    return run_ticket(ticket, classifier, retriever, now=now, kill_switch_file=kill_switch_file, call=call, sleep=sleep)
