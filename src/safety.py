"""Safety rules: tickets that must always go to a person (FR-03).

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.

Two independent checks, either of which sends a ticket to a person:
1. these fixed word rules, run on the ticket text before any model call;
2. the classifier's predicted type, if it is one of the person-only types.
"Rules are code, not prompts" (Module 3): the model can never switch these off.

The person-only cases come from the workbook and the PRD (product requirements
document): security, compliance, feature requests and unclear requests (the
must-not labels), plus Daniel's cases: data location, leaked keys and billing
disputes (Stage 1 workbook, Section 1, Daniel row; PRD FR-03).
"""
import re
from dataclasses import dataclass

PERSON_ONLY_TYPES = {"security_incident", "compliance_request", "feature_request",
                     "unclear_request", "data_residency"}

_SECRET = r"(credentials?|passwords?|api ?keys?|keys?|tokens?|secrets?)"
RULES = {
    "leaked key or credentials": [
        rf"(exposed|leak\w*|compromis\w*|breach\w*|stolen|public (repo|repository)|github|pushed|committed)\W+(\w+\W+){{0,6}}{_SECRET}",
        rf"{_SECRET}\W+(\w+\W+){{0,6}}(exposed|leak\w*|compromis\w*|breach\w*|stolen|public (repo|repository)|github)",
    ],
    # Found by the red team (RT-05, 8 Nov): a working key pasted into a ticket was answered and sent
    # to the model. NFR-04: a ticket containing a key or token goes to a person as a security matter.
    "key or token in the ticket": [
        r"\b(sk|pk|gsk|rk|ghp|xox[bp]|AKIA)[-_][A-Za-z0-9_-]{8,}",
        r"\b(?=[A-Za-z0-9_-]*\d)(?=[A-Za-z0-9_-]*[A-Za-z])[A-Za-z0-9_-]{24,}\b",
        r"\bbearer [A-Za-z0-9._-]{16,}",
    ],
    "security incident": [
        r"(none of us|nobody|we do not|we don't|i do not|i don't|not) recogni[sz]e",
        r"audit log\W+(\w+\W+){0,8}(unknown|unfamiliar|recogni[sz]e)",
        r"former employee",
        r"unauthori[sz]ed (access|activity|login|logins|use|api calls)",
        r"\bhack(ed|er|ers|ing)?\b",
        r"suspicious (activity|login|logins|access)",
        r"account (has been |was |is )?(compromised|taken over)",
        # RT-10: "someone logged into our account from a country none of us have been to"
        r"(someone|somebody|an? (unknown|stranger|attacker)) (has )?(logged|signed) ?in(to)?",
        r"(logged|signed) ?in(to)? (our|my|the) account from",
        r"(changed|changing) (the|our) (billing |account |login )?(email|password) without",
    ],
    "data location": [
        r"physically stored",
        r"\bdata (residency|location|sovereignty)\b",
        r"remain (within|in) (the )?(eu|european union|us|uk|region)",
        r"(stay|stays|kept|keep|stored|store|hosted|host) (in|within|inside|outside) (the )?(eu|european union|us|uk|europe|region|country)",
        r"backups?\W+(\w+\W+){0,6}(region|replicat\w*|outside)",
        r"which region\W+(\w+\W+){0,6}(data|organi[sz]ation|stored|in)",
        r"written confirmation",
    ],
    "billing dispute": [
        r"\brefunds?\b", r"\bdisput\w*", r"charge ?backs?",
        r"charged twice|double[- ]charged|duplicate charges?|overcharg\w*",
        r"(not|never)\W+(\w+\W+){0,2}(use|used|using|ordered|authori[sz]ed)\b",
        r"\bwe not use\b",
        r"money back",                    # RT-07: a refund demand without the word "refund"
    ],
    "compliance": [
        r"\bauditors?\b", r"\bgdpr\b", r"\bsoc ?2\b", r"\bhipaa\b", r"\biso ?27001\b",
        r"data processing (agreement|addendum)", r"\bsub-?processors?\b",
        r"policy requires", r"demonstrate that", r"retention (policy|requirement)",
        r"penetration test",
    ],
    "feature request": [
        r"\broadmap\b", r"feature request", r"something you are considering",
        r"(would be|it would be) (very )?useful (to|if)",
    ],
}
_COMPILED = {name: [re.compile(p, re.I) for p in pats] for name, pats in RULES.items()}


@dataclass(frozen=True)
class SafetyResult:
    must_go_to_person: bool
    reasons: tuple   # which rules or types fired, in words a support manager can read


def check_text(text: str) -> list:
    """The fixed word rules alone: names of the rules that matched."""
    return [name for name, pats in _COMPILED.items() if any(p.search(text or "") for p in pats)]


def check(text: str, predicted_type: str = None) -> SafetyResult:
    reasons = [f"word rule: {name}" for name in check_text(text)]
    if predicted_type in PERSON_ONLY_TYPES:
        reasons.append(f"type: {predicted_type}")
    return SafetyResult(bool(reasons), tuple(reasons))
