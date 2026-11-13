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
import os
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

# ---- 10 Nov: narrowed rules (on by default from 12 Nov; NARROW_RULES=off turns them off) ----
# Questions about where data lives, and questions about an unrecognised charge, are answered from the
# help articles (the answer key labels 21 of 29 and 9 of 11 of these automatic). REQUESTS stay with a person:
# moving or deleting data, changing region, refunds, disputes, chargebacks, double charges, money back.
# Untouched, zero tolerance: security incidents, leaked keys, keys pasted in a ticket, compliance,
# feature and unclear requests (every must-not type), and every guardrail on every reply.
NARROW_DATA_LOCATION = [
    r"\b(move|moving|migrate|migrating|transfer|transferring|relocate|relocating)\b\W+(\w+\W+){0,4}(data|organi[sz]ation|account|project)\W+(\w+\W+){0,4}(to|into)\b",
    r"\b(change|changing|switch|switching)\b\W+(\w+\W+){0,3}region\b",
    r"\b(delete|deleting|erase|erasing|purge|purging)\b\W+(\w+\W+){0,4}(all )?(our |my )?data\b",
    r"\bdata (sovereignty)\b",
]
NARROW_BILLING = [p for p in RULES["billing dispute"] if "use" not in p]   # drops only "a service we do not use"
_NARROW = {"data location": [re.compile(p, re.I) for p in NARROW_DATA_LOCATION],
           "billing dispute": [re.compile(p, re.I) for p in NARROW_BILLING]}


def _narrow() -> bool:
    return os.getenv("NARROW_RULES", "on") == "on"   # on by default from 12 Nov


# ---- 11 Nov 2026: final question rules decided by Mohnish Grover (off unless QUESTION_RULES=on) ----
# All 500 development tickets were grouped into 53 questions and each was decided by him
# (evaluation/human_review/question_groups_decisions.json). With this switch on:
# 1. Daniel's data-location rule is restored in full: every data-location ticket goes to a person, by its words or
#    by its type, even when NARROW_RULES is on (Daniel: "anything involving data location, because we get those
#    wrong occasionally even as humans and the consequence is a compliance problem"). This covers Q22, Q23 and Q24.
#    13 Nov 2026 (Mohnish Grover): backup-replication questions (Q24) follow Daniel's rule like every other
#    data-location question; the earlier exception for them is removed.
#    The billing narrowing (an unrecognised charge is answered) is unchanged.
# 2. Q20 and Q11 go to a person (Q11 below). Q20: no article explains an export missing records created BEFORE the job (Ines's article
#    covers records created during it), so an automatic reply would give the wrong reason.
# Checked on the development tickets: exactly the 29 data-location tickets, the 9 Q20 tickets and the 4 Q11 tickets.
QUESTION_RULES = {
    "no article covers it: export missing records created before the job (Q20)": [
        r"\bexport\w*\W+(\w+\W+){0,6}missing\W+(\w+\W+){0,8}before\b"],
    # Q11: no article says to update the password stored in automated jobs; decided "person" (11 Nov). The checker
    # blocked all 4 in v1.6 but let 1 through in v1.7, so the decision is enforced here instead.
    "no article covers it: automated jobs failing after a password change (Q11)": [
        r"\bpassword\b\W+(\w+\W+){0,12}(automated|scheduled|scripts?|jobs?|pipelines?|integrations?)\W+(\w+\W+){0,6}(fail\w*|authenticat\w*|broken|stopped)"],
}
_QUESTIONS = {name: [re.compile(p, re.I) for p in pats] for name, pats in QUESTION_RULES.items()}

def _question_rules() -> bool:
    return os.getenv("QUESTION_RULES", "on") == "on"   # on by default from 12 Nov


@dataclass(frozen=True)
class SafetyResult:
    must_go_to_person: bool
    reasons: tuple   # which rules or types fired, in words a support manager can read


def check_text(text: str) -> list:
    """The fixed word rules alone: names of the rules that matched."""
    rules = {**_COMPILED, **_NARROW} if _narrow() else dict(_COMPILED)
    if _question_rules():
        rules["data location"] = _COMPILED["data location"]     # Daniel's rule in full (11 Nov)
        rules.update(_QUESTIONS)
    return [name for name, pats in rules.items() if any(p.search(text or "") for p in pats)]


def check(text: str, predicted_type: str = None) -> SafetyResult:
    reasons = [f"word rule: {name}" for name in check_text(text)]
    types = PERSON_ONLY_TYPES - {"data_residency"} if (_narrow() and not _question_rules()) else PERSON_ONLY_TYPES
    if predicted_type in types:
        reasons.append(f"type: {predicted_type}")
    return SafetyResult(bool(reasons), tuple(reasons))
