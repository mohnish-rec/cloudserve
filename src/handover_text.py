"""The summary a person receives with a ticket, in plain words (16-17 Nov 2026, Mohnish Grover: "write the summary as
per [the project files] and should be easily understandable").

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
The four parts and their order come from the project files:
  Daniel (Stakeholder Interviews): "here is the ticket, here is what I think it is about, here is the documentation
  that seemed relevant, and here is specifically what I was not confident about".
  Project Brief: "a correct summary, the relevant documentation already attached and a clear statement of what the
  system was unsure about".
Written by plain code from what the system found: no model call, and the same ticket always gets the same summary.
"""
import re

TOPIC = {
    "account_access": "access to an account or project", "api_key_issue": "an API key problem",
    "api_usage_question": "a question about using the API", "authentication_failure": "a login problem",
    "billing_query": "a billing question", "compliance_request": "a compliance request",
    "configuration_help": "help with configuration", "data_export": "a data export",
    "data_residency": "where data is stored", "database_issue": "a database problem",
    "deployment_failure": "a failed deployment or build", "feature_request": "a request for a new feature",
    "integration_help": "help with an integration", "onboarding": "getting started",
    "performance_degradation": "slow performance", "quota_or_overage": "usage limits or overage",
    "rate_limit": "rate limits", "rollback_request": "rolling back a release",
    "security_incident": "a possible security incident", "sso_configuration": "single sign-on (SSO)",
    "unclear_request": "something that is not clear yet", "webhook_issue": "a webhook problem",
}

# Why a person handles it, one plain sentence per rule. The last four are Mohnish Grover's own decisions, in his words
# where he gave them (evaluation/human_review/dev_walkthrough.json).
RULE = {
    "leaked key or credentials": "The customer may have a leaked key or password, which a person must always handle.",
    "key or token in the ticket": "The ticket seems to contain a key or token, so it must not be answered automatically.",
    "security incident": "This looks like a security incident, which a person must always handle.",
    "data location": "It asks where data is stored, which a person must always answer.",
    "billing dispute": "It disputes a charge or asks for a refund, which a person must handle.",
    "compliance": "It is a compliance request, which a person must handle.",
    "feature request": "It asks for a feature, and there is no help article for that.",
    "no article covers it: automated jobs failing after a password change":
        "Automated jobs fail after a password change, and no help article covers this.",
    "needs a person: invalid credentials with a correct password":
        "The customer is sure the password is correct; this is complex and needs a person for a quick resolution.",
    "needs a person: a database restore still running":
        "The restore has run much longer than the article says to expect; only support can check whether it has stalled.",
    "needs a person: throttled, would rather pay overage":
        "The article's reply would include causes that do not fit this customer and could confuse them.",
}
TYPE = {
    "security_incident": "This looks like a security incident, which a person must always handle.",
    "compliance_request": "It is a compliance request, which a person must handle.",
    "feature_request": "It asks for a feature, and there is no help article for that.",
    "unclear_request": "It is not clear what the customer needs.",
    "data_residency": "It asks where data is stored, which a person must always answer.",
}


def excerpt(ticket, limit=250) -> str:
    text = " — ".join(x.strip() for x in (ticket.subject, ticket.body) if x and x.strip())   # subject — message
    return text if len(text) <= limit else text[:limit].rsplit(" ", 1)[0] + "…"


def about(ticket, c, d) -> str:
    plan = ticket.customer_tier.capitalize() if ticket.customer_tier not in ("", "unknown") else "Unknown plan"
    channel = {"email": "by email", "chat": "by chat", "docs_comment": "as a comment on the documentation",
               "forum": "on the forum"}.get(ticket.channel, "")
    topic = TOPIC.get(c.intent, c.intent.replace("_", " "))
    return f"{topic[0].upper() + topic[1:]}. {plan} customer, {channel}, {d.priority} priority.".replace(" ,", ",")


def not_sure(ticket, c, s, d, passages, draft, report, prior, kill_switch) -> list:
    """Every reason the system did not answer by itself, each as one plain sentence."""
    out = []
    if kill_switch:
        out.append("Automatic replies are switched off at the moment.")
    if c.fallback:
        out.append("It was not possible to tell what the ticket is about.")
    for r in (s.reasons if s is not None else ()):
        if r.startswith("word rule: "):
            out.append(RULE.get(r[len("word rule: "):], r[len("word rule: "):].capitalize() + "."))
        elif r.startswith("type: "):
            out.append(TYPE.get(r[len("type: "):], ""))
        elif r.startswith("follow-up"):
            when = re.search(r"on (\d{1,2} \w+ \d{4}) \(([^)]+)\)", r)
            out.append("The same customer already had an automatic reply about the same problem"
                       + (f" on {when.group(1)} ({when.group(2)})" if when else "") + ", and it may not have solved it.")
        elif r.startswith("similar tickets were handled by a person"):
            out.append("Similar tickets were handled by a person in the past.")
    if not passages and not c.fallback:
        out.append("No help article matched the question closely enough.")
    if not c.fallback and d.confidence < d.threshold:
        out.append(f"The system was only {d.confidence:.0%} sure what the ticket is about.")
    if report is not None and report.blocked:
        for x in report.checks:
            if not x.passed:
                detail = re.split(r" \(", x.detail, 1)[0]
                out.append(f"A final check stopped the reply: {detail}.")
    if draft is not None and not draft.ok:
        out.append("The AI service did not respond, so no reply was written." if "unavailable" in (draft.error or "")
                   else "The help articles found do not answer it.")
    if draft is not None and draft.unsure_about:
        out.append(f"While writing the reply, the system was unsure about: {draft.unsure_about.rstrip('.')}.")
    return [x for x in dict.fromkeys(out) if x]


_ARTS = []


def _articles() -> list:
    if not _ARTS:
        try:
            from src.retrieve import load_documents
            _ARTS.extend(load_documents())
        except Exception:  # noqa: BLE001 - without the corpus the titles from search are still used
            pass
    return _ARTS


def _where(doc_id: str, titles: dict) -> str:
    """17 Nov 2026 (Mohnish Grover: "it still doesn't have where the article comes from"): the article's title, its
    ID in the knowledge base, and who it applies to, e.g. "Single sign-on configuration with SAML providers"
    (knowledge base article DOC-AUTH-003, applies to Business and Enterprise plans)."""
    art = next((a for a in _articles() if a["doc_id"] == doc_id), {})
    title = art.get("title") or titles.get(doc_id, doc_id)
    applies = art.get("applies_to") or (re.search(r"\*\*Applies to:\*\*\s*(.+)", art.get("content", "")) or [None, ""])[1]
    return f'"{title}" (knowledge base article {doc_id}' + (f", applies to {applies.strip()}" if applies else "") + ")"


def closest(passages) -> list:
    """17 Nov 2026 (Mohnish Grover: "How about including top 2 where the second one makes sense too"): with no reply
    attached, the closest article, and the second closest only when the knowledge base itself links the two (either
    article's related_docs list names the other). The links are the documentation team's, not the system's guess."""
    ids = list(dict.fromkeys(p.doc_id for p in passages))
    if len(ids) < 2:
        return ids
    rel = {a["doc_id"]: set(a.get("related_docs") or []) for a in _articles()}
    first, second = ids[0], ids[1]
    linked = second in rel.get(first, set()) or first in rel.get(second, set())
    return [first, second] if linked else [first]


def titles_in(reply: str) -> list:
    """The articles a sent reply was written from, read from its own lines ('From our help article "…":')."""
    return list(dict.fromkeys(re.findall(r'From our help article "([^"]+)"', reply or "")))


def summary(ticket, c, d, passages, reasons_text, attached, used=(), used_titles=()) -> str:
    """used: the articles the attached reply was written from. When there is one, those are the relevant articles;
    otherwise the search's best three (17 Nov: the search's top three alone included unrelated articles)."""
    titles = {p.doc_id: p.title for p in passages}
    by_title = {v: k for k, v in titles.items()}
    by_title.update({a["title"]: a["doc_id"] for a in _articles()})
    ids = ([by_title.get(t, "") for t in used_titles] or list(dict.fromkeys(used)) or closest(passages))
    docs = [_where(i, titles) for i in ids if i]
    lines = [f'The ticket: "{excerpt(ticket)}"',
             f"What it is about: {about(ticket, c, d)}",
             "Help articles that seemed relevant: " + ("; ".join(docs) if docs else "none found."),
             "What the system was not sure about: " + (" ".join(reasons_text) or "nothing recorded."),
             attached]
    return "\n".join(lines)
