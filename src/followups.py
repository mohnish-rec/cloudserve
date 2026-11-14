"""Follow-ups (14 Nov 2026, Mohnish Grover): "If an automatic answer did not solve the problem, the follow-up goes to a
person with a draft."

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
Every automatic reply ends "If it does not solve your problem, just reply to this message and a member of our support
team will pick it up." Without this, a detailed follow-up ("I tried those steps, it still fails") could be answered
again with the same article. So: when the same customer had an automatic reply on the same ticket type within the 7
days before (the Evaluation Framework's repeat-contact window), the new ticket goes to a person, and the handover's
draft is the earlier reply (Daniel: "here is the documentation that seemed relevant, and here is specifically what I
was not confident about"). Like the run memory (A5), this lasts only for the run and is never saved.
"""
from datetime import datetime, timedelta

WINDOW = timedelta(days=7)
_SENT = {}          # customer_id -> list of (time, ticket type, ticket_id, reply sent)


def reset():
    _SENT.clear()


def _when(text):
    try:
        return datetime.fromisoformat((text or "").replace("Z", "+00:00"))
    except ValueError:
        return None


def remember(ticket, intent, reply):
    """An automatic reply was sent: keep it so a follow-up from the same customer can be recognised."""
    when = _when(ticket.received_at)
    if when and ticket.customer_id and ticket.customer_id != "unknown":
        _SENT.setdefault(ticket.customer_id, []).append((when, intent, ticket.ticket_id, reply))


def earlier(ticket, intent):
    """The same customer's most recent automatic reply on the same type within the 7 days before, or None."""
    when = _when(ticket.received_at)
    if not when:
        return None
    found = [e for e in _SENT.get(ticket.customer_id, []) if e[1] == intent and timedelta(0) <= when - e[0] <= WINDOW]
    return max(found, key=lambda e: e[0]) if found else None


def reason(e) -> str:
    return (f"follow-up: the same customer had an automatic reply on the same type on {e[0]:%d %b %Y} ({e[2]}), "
            f"so it may not have solved the problem")
