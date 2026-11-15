"""The plan rule (15 Nov 2026, Mohnish Grover): "It should be a general rule because if the standard plan customers
cannot get their answers with it then it will be useless".

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
Each help article states who it applies to ("**Applies to:** Business and Enterprise plans"). When a reply uses an
article that applies only to other plans than the customer's, the reply is not sent: the ticket goes to a person
with the draft ("Draft ready"), who can answer for the customer's plan. A customer whose plan is unknown is treated
the same way, because the system cannot confirm the article applies. PLAN_RULE=off turns it off.
"""
import os
import re

PLANS = ("standard", "business", "enterprise")
_APPLIES = re.compile(r"\*\*Applies to:\*\*\s*(.+)")


def enabled() -> bool:
    return os.getenv("PLAN_RULE", "on") == "on"


def applies_to(content: str) -> str:
    m = _APPLIES.search(content or "")
    return m.group(1).strip() if m else ""


def plan_limited(applies: str) -> bool:
    """True when the line names plans, e.g. "Business and Enterprise plans" (not "All plans", not a product list)."""
    a = applies.lower()
    return "plan" in a and "all plans" not in a and any(p in a for p in PLANS)


def excluded(tier: str, cited_ids, articles: dict):
    """The first article the reply uses that does not apply to this customer's plan, as (doc_id, applies), or None."""
    tier = (tier or "").strip().lower()
    for doc_id in cited_ids:
        applies = applies_to((articles.get(doc_id) or {}).get("content", ""))
        if plan_limited(applies) and tier not in applies.lower():
            return doc_id, applies
    return None


def reason(doc_id: str, applies: str, tier: str, label: str) -> str:
    plan = tier if tier and tier != "unknown" else "an unknown"
    return (f"Sent to a person ({label}) because article {doc_id} applies to {applies} and this customer is on "
            f"{plan} plan (plan rule).")
