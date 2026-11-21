"""Setup Guide step 06: the metrics the system exposes for Prometheus.

Attribution: based on the Setup Guide's code (step 06), adapted with Claude (Anthropic); reviewed and run by
Mohnish Grover.

The guide's three metrics, plus a confidence histogram for the dashboard
panel the guide lists as "the distribution of confidence scores, which is
where drift shows up first".
"""
from prometheus_client import Counter, Histogram, start_http_server

TICKETS = Counter("tickets_processed_total", "Tickets processed", ["channel", "outcome"])
LATENCY = Histogram(  # buckets up to 5 minutes: on the free tier a reply can wait through rate limits (14 Nov)
    "response_seconds", "End to end response time",
    buckets=[0.25, 0.5, 1, 2, 3, 5, 10, 20, 30, 60, 120, 300],
)
GUARDRAIL = Counter("guardrail_blocks_total", "Responses blocked", ["guardrail"])
CONFIDENCE = Histogram(  # added: not in the guide's code, but needed for its fifth dashboard panel
    "classification_confidence", "Classifier confidence per ticket",
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
)


# 14 Nov 2026: every channel/outcome and guardrail count starts at 0. A count that first appears already at 1 has no
# earlier value, so Prometheus reads its increase as 0 and the per-hour panels stay flat (seen on the dashboard).
def _start_at_zero() -> None:
    for channel in ("email", "chat", "docs_comment", "forum", "unknown"):
        for outcome in ("auto_respond", "escalate", "block"):
            TICKETS.labels(channel, outcome)
    for name in ("private_data", "grounding_words", "grounding_model", "instruction_integrity", "tone_and_scope",
                 "confidence_floor"):
        GUARDRAIL.labels(name)


_start_at_zero()


def reset() -> None:
    """Every number back to 0, as if the system had just started (21 Nov 2026: the web page's "Start the live charts
    from zero" button). Only the chart numbers change; no decision, log row or setting does."""
    for counter in (TICKETS, GUARDRAIL):
        counter.clear()
    for histogram in (LATENCY, CONFIDENCE):
        try:
            histogram._metric_init()   # prometheus_client's own set-up of an unlabelled histogram: all buckets 0
        except AttributeError:
            pass
    _start_at_zero()


def start_metrics_server(port: int = 8001) -> None:
    """Serve metrics at http://localhost:<port>/metrics (the guide's port).

    Bound to 127.0.0.1 so Windows does not show a firewall prompt:
    Prometheus reads it from the same machine.
    """
    start_http_server(port, addr="127.0.0.1")