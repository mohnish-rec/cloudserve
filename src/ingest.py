"""Ingest: turn tickets from all four channels into one shape (FR-01).

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
The project files contain no ingest code; reading the file follows the
Dataset Guide's loading snippet, with one marked change (see load_tickets).

Build Specification, "Ingest":
- accepts email, live chat, documentation comments and the community forum;
- produces one normalised representation whatever the channel;
- keeps the original text and the channel;
- handles missing fields, unusual characters and empty bodies without failing.

Data handling (Module 3):
- ELT (extract, load, transform): the input file is never changed and each
  ticket keeps its original subject and body next to the cleaned copy, so
  nothing is lost by cleaning; the harness records the input file's hash;
- seven data-quality checks run on every ticket and any problem is written
  to `issues`; a ticket with a blocking issue is escalated later, never
  dropped (our dead-letter queue).

Two privacy and fairness choices (PRD NFR-04, NFR-06):
- the customer's name is never copied into the ticket, so it can never reach
  the model or a reply;
- the labels and history in the data files are the answer key: they are left
  out here and only the evaluation harness reads them.

Check (Build Specification, day one):  python -m src.ingest data/validation_tickets.json
"""
import json
import re
from datetime import datetime
import sys
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path

CHANNELS = ("email", "chat", "docs_comment", "forum")
TIERS = ("enterprise", "business", "standard")
REGIONS = ("north_america", "europe", "asia_pacific", "latin_america")
FLUENCY = ("fluent", "non_fluent")
ALLOWED = {"customer_tier": TIERS, "customer_region": REGIONS, "language_fluency": FLUENCY}
# Issues that mean the ticket cannot be answered automatically at all.
BLOCKING_ISSUES = ("not a ticket object", "empty body")
CHANNEL_ALIASES = {"live_chat": "chat", "docs_comments": "docs_comment",
                   "documentation_comment": "docs_comment", "community_forum": "forum"}


@dataclass(frozen=True)
class Ticket:
    ticket_id: str
    channel: str             # one of CHANNELS, or "unknown"
    subject: str             # cleaned; empty for chat
    body: str                # cleaned
    text: str                # what the rest of the system reads: subject and body together
    original_subject: str    # exactly as received
    original_body: str       # exactly as received
    received_at: str         # ISO 8601 time as received, or "" if missing
    customer_id: str
    customer_tier: str       # enterprise, business, standard, or "unknown"
    customer_region: str
    language_fluency: str
    issues: tuple            # anything odd found while reading the ticket


def clean(value) -> str:
    """Text safe to process: normal Unicode, no control characters, single spaces."""
    if value is None:
        return ""
    text = unicodedata.normalize("NFKC", str(value))
    text = "".join(" " if unicodedata.category(c).startswith("C") else c for c in text)
    return re.sub(r"\s+", " ", text).strip()


def normalise(raw, position: int = 0) -> Ticket:
    """One ticket in, one Ticket out. Never raises: problems are recorded in `issues`."""
    issues = []
    if not isinstance(raw, dict):
        issues.append("not a ticket object")
        raw = {}

    ticket_id = clean(raw.get("ticket_id"))
    if not ticket_id:
        ticket_id = f"UNKNOWN-{position:04d}"
        issues.append("missing ticket_id")

    channel = clean(raw.get("channel")).lower().replace(" ", "_")
    channel = CHANNEL_ALIASES.get(channel, channel)
    if channel not in CHANNELS:
        issues.append(f"unknown channel {channel!r}" if channel else "missing channel")
        channel = "unknown"

    original_subject = "" if raw.get("subject") is None else str(raw.get("subject"))
    original_body = "" if raw.get("body") is None else str(raw.get("body"))
    subject, body = clean(original_subject), clean(original_body)
    if not body:
        issues.append("empty body")

    text = f"{subject}. {body}" if subject and body else (subject or body)

    def field(name):
        # Completeness and validity: present, and one of the allowed values.
        value = clean(raw.get(name)).lower()
        if not value:
            issues.append(f"missing {name}")
            return "unknown"
        if value not in ALLOWED[name]:
            issues.append(f"invalid {name} {value!r}")
            return "unknown"
        return value

    # Timeliness: the time received must be readable.
    received_at = clean(raw.get("received_at"))
    if not received_at:
        issues.append("missing received_at")
    else:
        try:
            datetime.fromisoformat(received_at.replace("Z", "+00:00"))
        except ValueError:
            issues.append("unreadable received_at")

    return Ticket(
        ticket_id=ticket_id, channel=channel, subject=subject, body=body, text=text,
        original_subject=original_subject, original_body=original_body,
        received_at=received_at,
        customer_id=clean(raw.get("customer_id")) or "unknown",
        customer_tier=field("customer_tier"),
        customer_region=field("customer_region"),
        language_fluency=field("language_fluency"),
        issues=tuple(issues),
    )


def load_tickets(path) -> list:
    """Every entry in the file becomes a Ticket, so none is silently dropped."""
    # Dataset Guide, section 5: tickets = json.loads(Path(input_path).read_text())
    # Change: the encoding is stated. Without it, Windows reads the file in its own
    # default encoding and a ticket with an accented letter or an emoji fails;
    # "utf-8-sig" also accepts a file saved with a byte-order mark.
    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if isinstance(data, dict):  # also accept {"tickets": [...]}
        data = data.get("tickets", [data])
    tickets = [normalise(raw, i) for i, raw in enumerate(data, start=1)]
    # Uniqueness: a repeated ticket ID is kept and processed, but flagged.
    seen = set()
    for i, t in enumerate(tickets):
        if t.ticket_id in seen:
            tickets[i] = Ticket(**{**t.__dict__, "issues": t.issues + ("duplicate ticket_id",)})
        seen.add(t.ticket_id)
    return tickets


def is_blocked(ticket: Ticket) -> bool:
    """True when a data-quality problem means the ticket must go to a person."""
    return any(issue in BLOCKING_ISSUES for issue in ticket.issues)


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "data/validation_tickets.json"
    tickets = load_tickets(path)
    print(f"{len(tickets)} tickets read from {Path(path).name}\n")
    for channel in CHANNELS:
        first = next((t for t in tickets if t.channel == channel), None)
        if first:
            print(f"--- {channel} ---")
            print(json.dumps(asdict(first), indent=2, ensure_ascii=False))
