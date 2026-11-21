"""Send the seven demo tickets to the running system (README step 8) and print each result in plain words.

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
The system must be running first (README step 7: python -m src.api). Because the tickets go to the running system,
they also appear on the live charts (Prometheus and Grafana), if those are set up.
Run: python scripts/send_demo_tickets.py
"""
import json
import sys
import textwrap
import urllib.error
import urllib.request
from pathlib import Path

URL = "http://127.0.0.1:8000/tickets"
TICKETS = Path(__file__).resolve().parent.parent / "data" / "samples" / "demo_tickets.json"
OUTCOME = {"auto_respond": "ANSWERED AUTOMATICALLY", "escalate": "SENT TO A PERSON", "block": "BLOCKED BY A GUARDRAIL"}


def send(ticket: dict) -> dict:
    request = urllib.request.Request(URL, json.dumps(ticket).encode("utf-8"), {"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=300) as response:
        return json.load(response)


def main() -> int:
    tickets = json.loads(TICKETS.read_text(encoding="utf-8"))
    print(f"Sending {len(tickets)} demo tickets to the running system ({URL})\n")
    for number, ticket in enumerate(tickets, 1):
        try:
            result = send(ticket)
        except urllib.error.URLError:
            print("The system is not running, so nothing was sent. Start it first (README step 7: "
                  "python -m src.api), then run this again.")
            return 1
        outcome = OUTCOME.get(result.get("action"), result.get("action", "?"))
        label = f" ({result['label']})" if result.get("label") else ""
        print(f"{number}. {ticket['ticket_id']}  |  {ticket.get('channel', '?')}  |  {ticket.get('subject') or '(no subject)'}")
        print(f"   Result: {outcome}{label}")
        print(textwrap.fill(f"Why: {result.get('reason', '')}", width=100, initial_indent="   ",
                            subsequent_indent="        "))
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
