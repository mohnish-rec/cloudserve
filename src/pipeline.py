"""One ticket through every stage: classify, safety rules, search, route, write, guardrails, outcome.

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
Day 4 builds this as one plain function so the red-team set can run the real pipeline;
day 5 wraps the same stages in the LangGraph workflow (Module 7) and adds the decision log.

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
from src.generate import Draft, articles_for, generate, with_notice
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
    model_calls: int = 0
    latency_ms: int = 0
    requirement_ids: tuple = field(default_factory=tuple)


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
        "draft": draft.reply if draft is not None and draft.ok and not (report and {"private_data", "instruction_integrity"}
                                                                        & set(report.fired)) else "",
        "unsure": "; ".join(x for x in [why, draft.unsure_about if draft is not None else ""] if x),
    }


def process(ticket, classifier, retriever, now=None, kill_switch_file=None, call=None, sleep=None) -> Outcome:
    start = time.perf_counter()
    kw = {k: v for k, v in (("call", call), ("sleep", sleep)) if v}
    c = classifier.classify("" if is_blocked(ticket) else ticket.text)
    s = check(ticket.text, c.intent)
    passages = [] if is_blocked(ticket) else retriever.search(ticket.text)
    d = route(ticket.text, c, s, passages, received_at=ticket.received_at, now=now, kill_switch_file=kill_switch_file)

    def done(action, label, reason, draft=None, report=None, sent=ACKNOWLEDGEMENT, reqs=()):
        calls = (draft.calls if draft is not None else 0) + (
            1 if report is not None and any(x.name == "grounding_model" and not x.detail.startswith("not run")
                                            for x in report.checks) else 0)
        return Outcome(ticket.ticket_id, action, label, d.priority, reason, sent,
                       None if action == AUTO else _handover(ticket, c, s, passages, d, draft, reason, report),
                       c, d, draft, report, calls, int((time.perf_counter() - start) * 1000),
                       tuple(dict.fromkeys(d.requirement_ids + tuple(reqs))))

    # A safety rule, an unusable ticket or no article: to a person with no model call (NFR-07).
    if s.must_go_to_person or c.fallback or not passages:
        return done(ESCALATE, SPECIALIST, d.reason)

    draft = generate(ticket.text, c.intent, passages, **kw)
    if d.action == ESCALATE:                                   # e.g. confidence just under the threshold
        label = DRAFT_READY if (d.label == DRAFT_READY and draft.ok) else SPECIALIST
        return done(ESCALATE, label, d.reason, draft)
    if not draft.ok:
        return done(ESCALATE, SPECIALIST, f"Sent to a person ({SPECIALIST}) because {draft.error}.", draft,
                    reqs=("FR-05",))

    reply = with_notice(draft, passages)
    articles = {a["doc_id"]: a for a in articles_for(passages)}
    report = check_reply(reply, draft, articles, ticket.text, c.confidence, d.threshold, **kw)
    if report.blocked:
        why = "; ".join(f"{x.name}: {x.detail}" for x in report.checks if not x.passed)
        return done("block", SPECIALIST, f"Reply blocked by a guardrail and sent to a person ({SPECIALIST}): {why}.",
                    draft, report, reqs=("FR-09",))
    return done(AUTO, "", d.reason, draft, report, sent=reply, reqs=("FR-05", "FR-08", "FR-09"))
