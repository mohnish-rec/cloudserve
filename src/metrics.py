"""Setup Guide step 06: the metrics the system exposes for Prometheus.

The guide's three metrics, plus a confidence histogram for the dashboard
panel the guide lists as "the distribution of confidence scores, which is
where drift shows up first".
"""
from prometheus_client import Counter, Histogram, start_http_server

TICKETS = Counter("tickets_processed_total", "Tickets processed", ["channel", "outcome"])
LATENCY = Histogram("response_seconds", "End to end response time")
GUARDRAIL = Counter("guardrail_blocks_total", "Responses blocked", ["guardrail"])
CONFIDENCE = Histogram(  # added: not in the guide's code, but needed for its fifth dashboard panel
    "classification_confidence", "Classifier confidence per ticket",
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
)


def start_metrics_server(port: int = 8001) -> None:
    """Serve metrics at http://localhost:<port>/metrics (the guide's port).

    Bound to 127.0.0.1 so Windows does not show a firewall prompt:
    Prometheus reads it from the same machine.
    """
    start_http_server(port, addr="127.0.0.1")