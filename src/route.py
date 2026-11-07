"""Route: answer automatically or send to a person (FR-06, FR-07, FR-13, FR-16).

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.

A ticket is answered automatically only when ALL of these hold:
  - the kill switch is off (FR-16);
  - the classifier produced a type (no fallback, FR-02);
  - no safety rule fires and the type is not person-only (FR-03);
  - search found a relevant article (D-017);
  - the classifier is at least CONFIDENCE_THRESHOLD sure (0.85, D-019).
Anything else goes to a person with a label set by a fixed rule (FR-07):
  "Draft ready: check and send": safe, an article was found, the type is known and
      the classifier is at least DRAFT_READY_MIN_CONFIDENCE sure (just under the threshold);
  "Needs a specialist": everything else.
The label is output only: it is never written to the data or fed back to the model.

Deterministic (acceptance criterion A5): no randomness and no model call here, so the
same inputs always give the same decision.
"""
import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.85"))          # D-019
DRAFT_READY_MIN_CONFIDENCE = float(os.getenv("DRAFT_READY_MIN_CONFIDENCE", "0.60"))
KILL_SWITCH_FILE = ROOT / os.getenv("KILL_SWITCH_FILE", "storage/kill_switch")
SLA_MINUTES = 120             # the agreement promises a first reply within 2 hours (Project Brief)
NEAR_BREACH_MINUTES = 90      # older than this and still unanswered: move it up the queue (FR-13)

AUTO, ESCALATE = "auto_respond", "escalate"
DRAFT_READY, SPECIALIST = "Draft ready: check and send", "Needs a specialist"

# Urgency labels in the data disagree with themselves (D-018), so clear words and
# risky types raise the priority on top of the classifier's urgency (FR-13).
URGENT_WORDS = re.compile(
    r"production (is |has gone )?down|\boutage\b|site (is )?down|all (of )?(our |my )?(users|customers)|"
    r"every (request|user|customer)|nobody can|no one can|data loss|losing (data|customers|money|revenue)|"
    r"\burgent(ly)?\b|asap|immediately", re.I)
HIGH_PRIORITY_REASONS = ("leaked key or credentials", "security incident", "type: security_incident")


@dataclass(frozen=True)
class RouteDecision:
    action: str                   # auto_respond or escalate
    label: str                    # "" when answered automatically, else DRAFT_READY or SPECIALIST
    priority: str                 # high, medium or low
    near_breach: bool
    confidence: float
    threshold: float
    reasons: tuple                # each reason it went to a person, in plain words
    reason: str                   # one sentence a support manager can read
    requirement_ids: tuple


def kill_switch_on(path=None) -> bool:
    """Checked before every ticket, so it works mid-run without a restart (FR-16).
    On when the file storage/kill_switch exists, or KILL_SWITCH=on in the environment."""
    path = Path(path) if path else KILL_SWITCH_FILE
    return path.exists() or os.getenv("KILL_SWITCH", "off").strip().lower() in {"on", "1", "true", "yes"}


def _priority(text, classification, safety, received_at, now):
    priority = classification.urgency if classification.urgency in {"high", "medium", "low"} else "medium"
    raised = []
    if URGENT_WORDS.search(text or ""):
        raised.append("urgent words")
    if any(x.replace("word rule: ", "") in HIGH_PRIORITY_REASONS for x in safety.reasons):
        raised.append("security risk")
    near_breach = False
    if received_at and now:
        try:
            age = (now - datetime.fromisoformat(str(received_at).replace("Z", "+00:00"))).total_seconds() / 60
            near_breach = age >= NEAR_BREACH_MINUTES
        except (TypeError, ValueError):
            near_breach = False
    if near_breach:
        raised.append(f"waiting {NEAR_BREACH_MINUTES}+ minutes")
    return ("high" if raised else priority), near_breach, raised


def route(text, classification, safety, passages, received_at=None, now=None,
          threshold=None, kill_switch_file=None) -> RouteDecision:
    threshold = CONFIDENCE_THRESHOLD if threshold is None else threshold
    conf = float(classification.confidence)
    reasons, reqs = [], ["FR-06"]
    if kill_switch_on(kill_switch_file):
        reasons.append("the kill switch is on, so all automatic replies are stopped")
        reqs.append("FR-16")
    if classification.fallback:
        reasons.append(f"the ticket could not be classified ({classification.reason or 'no reason given'})")
        reqs.append("FR-02")
    if safety.must_go_to_person:
        reasons.append("a safety rule says a person must handle it (" + "; ".join(safety.reasons) + ")")
        reqs.append("FR-03")
    if not passages:
        reasons.append("no help article matches it closely enough")
        reqs.append("FR-05")
    if not classification.fallback and conf < threshold:
        reasons.append(f"the system is only {conf:.0%} sure it is {classification.intent}; "
                       f"it answers by itself only at {threshold:.0%} or more")

    priority, near_breach, raised = _priority(text, classification, safety, received_at, now)
    if raised:
        reqs.append("FR-13")
    pr = f" Priority {priority} (" + (", ".join(raised) if raised else "the classifier's urgency") + ")."

    if not reasons:
        top = passages[0]
        return RouteDecision(AUTO, "", priority, near_breach, conf, threshold, (),
                             f"Answered automatically: {conf:.0%} sure it is {classification.intent} "
                             f"(threshold {threshold:.0%}), no safety rule applies, and article {top.doc_id} "
                             f"matches.{pr}", tuple(reqs))

    draft_ready = (not classification.fallback and not safety.must_go_to_person and bool(passages)
                   and conf >= DRAFT_READY_MIN_CONFIDENCE)
    label = DRAFT_READY if draft_ready else SPECIALIST
    reqs.append("FR-07")
    return RouteDecision(ESCALATE, label, priority, near_breach, conf, threshold, tuple(reasons),
                         f"Sent to a person ({label}) because " + "; and ".join(reasons) + "." + pr,
                         tuple(dict.fromkeys(reqs)))


def queue_key(decision: RouteDecision, received_at: str = ""):
    """Sort key for the agents' queue (FR-13): near-breach first, then high, medium, low, then oldest."""
    rank = {"high": 1, "medium": 2, "low": 3}.get(decision.priority, 2)
    return (0 if decision.near_breach else 1, rank, str(received_at or ""))
