"""Validate: five guardrails on every reply before it is released (FR-09).

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.

1. Private data        names, emails, phone numbers, keys, tokens, account and card numbers (NFR-04)
2. Grounding           (a) word check in code: each sentence's words and numbers are in the article it
                       cites; (b) a second model from a different family (PR-02, Qwen) checks the article fits
                       the customer's situation and every sentence is supported (decision D-020)
3. Instruction integrity  the ticket tries to take over the system, or the reply leaks our rules;
                       the ticket is recorded for review
4. Tone and scope      no refunds, credits, fixes on our side or dates (the three must-not-claims in
                       every reference answer), nothing rude, not too long
5. Confidence floor    the classifier at the threshold or above and the model "sure"; missing = low

Any guardrail firing, or any guardrail that itself fails, blocks the reply and the ticket is escalated
(fail closed): "A guardrail that only warns is not a guardrail" (Build Specification). Every check is
recorded, pass or block. Never edits a reply: "Block and escalate. Never redact and send."
"""
import json
import os
import re
from dataclasses import dataclass, field

from src.generate import call_with_fallback, load_prompt
from src.retrieve import STOPWORDS

# Another model family from the writer (gpt-oss). llama-3.1-8b-instant was planned but Groq no longer
# offers it (HTTP 404, 8 Nov 2026; scripts/list_models.py); Qwen is the other family Groq offers.
GUARD_MODEL = os.getenv("GUARDRAIL_MODEL", "qwen/qwen3.8-27b")
WORD_SUPPORT_MIN = float(os.getenv("WORD_SUPPORT_MIN", "0.6"))   # share of a sentence's words in its article
MAX_WORDS = 230
NUMBER_WORDS = set("one two three four five six seven eight nine ten eleven twelve fifteen twenty "
                   "thirty forty fifty sixty ninety hundred thousand million".split())


@dataclass
class Check:
    name: str
    passed: bool
    detail: str
    error: bool = False          # the check itself failed: counts as blocked


@dataclass
class Report:
    checks: list = field(default_factory=list)
    review_input: str = ""       # set when instruction integrity fires: the ticket kept for review

    @property
    def blocked(self) -> bool:
        return any(not c.passed for c in self.checks)

    @property
    def fired(self) -> list:
        return [c.name for c in self.checks if not c.passed]

    def as_log(self) -> dict:
        return {c.name: ("not run" if c.detail.startswith("not run") else "pass") if c.passed
                else ("error: " if c.error else "block: ") + c.detail for c in self.checks}


# ---------- 1. private data ----------
PRIVATE = {
    "email address": r"[\w.+-]+@[\w-]+\.[\w.-]+",
    "phone number": r"(?<![\w-])\+?\d[\d ()-]{7,}\d(?![\w-])",
    "key or token": r"\b(sk|pk|gsk|rk|ghp|xox[bp]|AKIA)[-_][A-Za-z0-9_-]{8,}|\b(?=[A-Za-z0-9_-]*\d)(?=[A-Za-z0-9_-]*[A-Za-z])[A-Za-z0-9_-]{24,}\b",
    "account or card number": r"\b\d(?:[ -]?\d){7,18}\b",
    "IP address": r"\b\d{1,3}(?:\.\d{1,3}){3}\b",
}


def private_data(reply, ticket_text, articles_text="") -> Check:
    found = [name for name, pat in PRIVATE.items() if re.search(pat, reply)]
    # A name from the ticket (two capitalised words together, e.g. a signature) repeated in the reply.
    for m in re.finditer(r"\b([A-Z][a-z]+ [A-Z][a-z]+)\b", ticket_text or ""):
        if m.group(1) in reply and m.group(1) not in articles_text and m.group(1).split()[0].lower() not in STOPWORDS:
            found.append(f"a name from the ticket ({m.group(1).split()[0][0]}.)")
    return Check("private_data", not found, "found " + ", ".join(found) if found else "none found")


# ---------- 2. grounding ----------
def _stem(word):
    for end in ("ing", "ed", "es", "s"):
        if word.endswith(end) and len(word) - len(end) >= 3:
            return word[: -len(end)]
    return word


def _words(text):
    return [w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOPWORDS and len(w) >= 3]


def word_support(sentences, articles: dict) -> Check:
    """Layer (a): for each sentence, most of its words and every number must be in its cited article."""
    weak = []
    for k, s in enumerate(sentences, 1):
        source = " ".join(articles[d]["content"] for d in s["doc_ids"] if d in articles).lower()
        if not source:
            weak.append(f"{k} (cites no known article)")
            continue
        vocab = {_stem(w) for w in re.findall(r"[a-z0-9]+", source)}
        words = _words(s["text"])
        numbers = [w for w in words if w.isdigit() or w in NUMBER_WORDS]
        if [n for n in numbers if n not in vocab]:
            weak.append(f"{k} (a number not in the article)")
            continue
        share = sum(_stem(w) in vocab for w in words) / len(words) if words else 1.0
        if share < WORD_SUPPORT_MIN:
            weak.append(f"{k} ({share:.0%} of its words in the article)")
    return Check("grounding_words", not weak, "sentences " + ", ".join(weak) if weak else "every sentence supported")


def model_support(ticket_text, sentences, articles: dict, call=None, sleep=None) -> Check:
    """Layer (b): a model from another family checks situation fit and support (PR-02)."""
    system, user = load_prompt("PR-02_grounding_check.md")
    cited = dict.fromkeys(d for s in sentences for d in s["doc_ids"])
    msg = user.format(ticket=ticket_text.replace("</ticket>", "< /ticket>"),
                      articles="\n\n".join(f"{d} · {articles[d]['title']}\n{articles[d]['content']}" for d in cited),
                      sentences="\n".join(f"{k}. {s['text']}" for k, s in enumerate(sentences, 1)))
    kw = {k: v for k, v in (("call", call), ("sleep", sleep)) if v}
    raw, _, _ = call_with_fallback([{"role": "system", "content": system}, {"role": "user", "content": msg}],
                                   models=[GUARD_MODEL], **kw)
    text = re.sub(r"<think>.*?</think>", "", raw or "", flags=re.S)     # Qwen may think aloud first
    m = re.search(r"\{[^{}]*\}\s*$", text.strip(), re.S) or re.search(r"\{.*\}", text, re.S)
    obj = json.loads(m.group(0)) if m else None
    if not isinstance(obj, dict) or not isinstance(obj.get("fits_situation"), bool) \
            or not isinstance(obj.get("unsupported_sentences", []), list):
        raise ValueError("the checker's answer could not be read")
    bad = [n for n in obj.get("unsupported_sentences", []) if isinstance(n, int)]
    ok = obj["fits_situation"] and not bad
    why = str(obj.get("reason", ""))[:200]
    if ok:
        return Check("grounding_model", True, f"fits and supported ({why})")
    parts = ([] if obj["fits_situation"] else ["the article does not fit the situation"]) + \
            ([f"sentences {bad} not supported"] if bad else [])
    return Check("grounding_model", False, "; ".join(parts) + f" ({why})")


# ---------- 3. instruction integrity ----------
TAKEOVER = re.compile(
    r"ignore (all |any |the |your |previous |prior |above )*(instructions|rules|prompts?)|disregard (all |the |your )*"
    r"(instructions|rules)|system prompt|you are now|pretend (to be|you are)|act as (an?|the) |developer mode|jailbreak|"
    r"reveal (your|the) (instructions|rules|prompt)|new instructions|</?(ticket|articles|reply|system)>|"
    r"respond with only|override (the|your) (rules|instructions)|"
    # RT-04 (8 Nov): a politely worded instruction aimed at the system, missed by the patterns above
    r"note (to|for) (the |any )?(ai|assistant|bot|model|system)|(ai|assistant|bot) reading this|"
    r"mark (this|the) ticket as|close (this|the) ticket|bypass (your|the) (usual )?(checks|rules)", re.I)
LEAK = re.compile(r"\bRULES\b|Respond with ONLY|<ticket>|<articles>|\"answered\"|\"sentences\"|\bPR-0\d")   # case-sensitive


def instruction_integrity(reply, ticket_text) -> Check:
    if TAKEOVER.search(ticket_text or ""):
        return Check("instruction_integrity", False, "the ticket contains text that tries to instruct the system")
    if LEAK.search(reply):
        return Check("instruction_integrity", False, "the reply contains our own instructions")
    return Check("instruction_integrity", True, "no instruction found in the ticket or the reply")


# ---------- 4. tone and scope ----------
PROMISES = {
    "a refund or credit": r"\brefund\w*|\bcredit(ed|s)? (to|on|back)|\bcompensat\w*|money back",
    "a fix on our side": r"(we|i)('ve| have| had)? (fixed|resolved|patched|corrected)|fixed on our (side|end)|"
                         r"(issue|problem|bug) (has been|is now|was) (fixed|resolved)",
    "a date or deadline": r"\b(by|on|before|until) (monday|tuesday|wednesday|thursday|friday|saturday|sunday|tomorrow|"
                          r"tonight|end of (the )?(day|week|month))|\b(will|should) be (fixed|resolved|deployed|live) "
                          r"(by|on|within|in)\b|\b(will|should) be available (by|on) |\b\d{1,2} (jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*",
    "a guarantee": r"\bguarantee\w*|\bpromise\b",
}
RUDE = re.compile(r"\b(stupid|idiot\w*|dumb|obviously|your (own )?fault|as i already said|calm down|rtfm)\b", re.I)


def tone_and_scope(reply) -> Check:
    found = [name for name, pat in PROMISES.items() if re.search(pat, reply, re.I)]
    if RUDE.search(reply):
        found.append("rude wording")
    if len(reply.split()) > MAX_WORDS:
        found.append(f"too long ({len(reply.split())} words)")
    return Check("tone_and_scope", not found, "found " + ", ".join(found) if found else "no promises, polite, in length")


# ---------- 5. confidence floor ----------
def confidence_floor(classifier_confidence, model_sure, threshold) -> Check:
    if classifier_confidence is None or model_sure is None:
        return Check("confidence_floor", False, "a confidence is missing, which counts as low")
    if float(classifier_confidence) < threshold:
        return Check("confidence_floor", False, f"classifier {float(classifier_confidence):.0%} is below {threshold:.0%}")
    if model_sure != "sure":
        return Check("confidence_floor", False, "the reply writer was not sure")
    return Check("confidence_floor", True, f"classifier {float(classifier_confidence):.0%}, writer sure")


# ---------- all five, fail closed ----------
def check_reply(reply, draft, articles: dict, ticket_text, classifier_confidence, threshold,
                call=None, sleep=None) -> Report:
    """reply: the full text the customer would see. articles: {doc_id: {"title", "content"}}."""
    report = Report()
    steps = [
        ("private_data", lambda: private_data(reply, ticket_text, " ".join(a["content"] for a in articles.values()))),
        ("grounding_words", lambda: word_support(draft.sentences, articles)),
        ("instruction_integrity", lambda: instruction_integrity(reply, ticket_text)),
        ("tone_and_scope", lambda: tone_and_scope(reply)),
        ("confidence_floor", lambda: confidence_floor(classifier_confidence, getattr(draft, "sure", None), threshold)),
    ]
    for name, run in steps:
        try:
            report.checks.append(run())
        except Exception as e:  # noqa: BLE001 - a guardrail that errors blocks (fail closed)
            report.checks.append(Check(name, False, f"the check failed: {type(e).__name__}", error=True))
    # The second model only runs when every cheap check has passed (saves calls; either can block).
    if not report.blocked:
        try:
            report.checks.append(model_support(ticket_text, draft.sentences, articles, call=call, sleep=sleep))
        except Exception as e:  # noqa: BLE001
            report.checks.append(Check("grounding_model", False, f"the check failed: {str(e)[:120]}", error=True))
    else:
        report.checks.append(Check("grounding_model", True, "not run: already blocked by a cheaper check"))
    if any(c.name == "instruction_integrity" and not c.passed for c in report.checks):
        report.review_input = (ticket_text or "")[:2000]
    return report
