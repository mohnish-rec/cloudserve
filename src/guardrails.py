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

from src import cache
from src.generate import call_with_fallback, load_prompt, tokens_of
from src.retrieve import STOPWORDS

# Another model family from the writer (gpt-oss). llama-3.1-8b-instant was planned but Groq no longer
# offers it (HTTP 404, 8 Nov 2026; scripts/list_models.py); Qwen is the other family Groq offers.
GUARD_MODEL = os.getenv("GUARDRAIL_MODEL", "qwen/qwen3.8-27b")
WORD_SUPPORT_MIN = float(os.getenv("WORD_SUPPORT_MIN", "0.6"))   # share of a sentence's words in its article
MAX_WORDS = 230
MAX_WORDS_TWO_ARTICLES = 320   # 14 Nov 2026, reply setting R1 (Mohnish Grover): a reply drawing on two articles may be longer
# "one" is left out: it is usually not a number ("one of our keys"). Found 9 Nov: it blocked 8 good replies.
NUMBER_WORDS = set("two three four five six seven eight nine ten eleven twelve fifteen twenty "
                   "thirty forty fifty sixty ninety hundred thousand million".split())


@dataclass
class Check:
    name: str
    passed: bool
    detail: str
    error: bool = False          # the check itself failed: counts as blocked
    cached: bool = False         # the second model's answer reused from the reply cache (D-025)
    memo: bool = False           # reused from this run's memory, no call made (A5, 12 Nov)
    tokens_in: int = 0           # the second model's tokens, for the budget
    tokens_out: int = 0
    bad: tuple = ()              # 10 Nov: numbers of the sentences that failed (1-based)
    trimmable: bool = False      # True when removing those sentences alone could fix the reply


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
    weak, bad = [], []
    for k, s in enumerate(sentences, 1):
        source = " ".join(articles[d]["content"] for d in s["doc_ids"] if d in articles).lower()
        if not source:
            weak.append(f"{k} (cites no known article)")
            bad.append(k)
            continue
        raw = set(re.findall(r"[a-z0-9]+", source))
        vocab = {_stem(w) for w in raw}
        words = _words(s["text"])
        numbers = [w for w in words if w.isdigit() or w in NUMBER_WORDS]
        # Numbers are compared exactly as written. Found 9 Nov on the 500 development tickets: they were
        # compared with shortened article words ("hundred" -> "hundr"), so 34 correct replies were blocked.
        if [n for n in numbers if n not in raw]:
            weak.append(f"{k} (a number not in the article)")
            bad.append(k)
            continue
        share = sum(_stem(w) in vocab for w in words) / len(words) if words else 1.0
        if share < WORD_SUPPORT_MIN:
            weak.append(f"{k} ({share:.0%} of its words in the article)")
            bad.append(k)
    return Check("grounding_words", not weak, "sentences " + ", ".join(weak) if weak else "every sentence supported",
                 bad=tuple(bad), trimmable=bool(bad))


def _shown(s) -> str:
    """PR-01 v1.7 (11 Nov): the checker sees a Common cause as the customer does, under the line "Common causes listed
    in the article:", not as a plain statement about this customer (v1.6: 6 replies blocked for "stating a cause as
    fact")."""
    from src import generate
    if generate.ALL_STEPS and ".C" in s.get("piece", ""):
        return f"(listed under \"{generate.CAUSES}\") {s['text']}"
    return s["text"]


def exact_copy(sentence, articles: dict) -> bool:
    """14 Nov 2026 (walkthrough, Q09): True when the sentence is word for word in an article it cites (list numbers and
    dashes aside). Such a sentence is supported by construction, so the checker's 'not supported' verdict on it is a
    false alarm (DEV-0218, DEV-0285). Checked here, not taken from the writer's own flag."""
    words = " ".join((sentence.get("text") or "").split()).rstrip(".")
    if not sentence.get("verbatim") or not words:
        return False
    for d in sentence.get("doc_ids", ()):
        body = " ".join(re.sub(r"^\s*(\d+\.|-)\s+", "", ln) for ln in articles.get(d, {}).get("content", "").splitlines())
        if words in " ".join(body.split()):
            return True
    return False


def model_support(ticket_text, sentences, articles: dict, call=None, sleep=None) -> Check:
    """Layer (b): a model from another family checks situation fit and support (PR-02)."""
    system, user = load_prompt("PR-02_grounding_check.md")
    cited = dict.fromkeys(d for s in sentences for d in s["doc_ids"])
    msg = user.format(ticket=ticket_text.replace("</ticket>", "< /ticket>"),
                      articles="\n\n".join(f"{d} · {articles[d]['title']}\n{articles[d]['content']}" for d in cited),
                      sentences="\n".join(f"{k}. {_shown(s)}" for k, s in enumerate(sentences, 1)))
    kw = {k: v for k, v in (("call", call), ("sleep", sleep)) if v}
    raw, _, _ = call_with_fallback([{"role": "system", "content": system}, {"role": "user", "content": msg}],
                                   models=[GUARD_MODEL], role="checker", **kw)   # Groq free tier
    t_in, t_out = tokens_of(raw)
    text = re.sub(r"<think>.*?</think>", "", raw or "", flags=re.S)     # Qwen may think aloud first
    m = re.search(r"\{[^{}]*\}\s*$", text.strip(), re.S) or re.search(r"\{.*\}", text, re.S)
    obj = json.loads(m.group(0)) if m else None
    if not isinstance(obj, dict) or not isinstance(obj.get("fits_situation"), bool) \
            or not isinstance(obj.get("unsupported_sentences", []), list):
        raise ValueError("the checker's answer could not be read")
    if getattr(raw, "cache_key", "") and not getattr(raw, "cached", False):
        cache.put(raw.cache_key, raw, GUARD_MODEL)          # only answers that were read successfully
    from src.generate import remember
    remember(raw, GUARD_MODEL)                              # A5 (12 Nov): same input in this run, same verdict
    hit = bool(getattr(raw, "cached", False))
    memo = bool(getattr(raw, "memo", False))
    bad = [n for n in obj.get("unsupported_sentences", []) if isinstance(n, int)]
    # 14 Nov 2026: a sentence copied word for word from its article cannot be unsupported; only the situation fit decides
    cleared = [n for n in bad if 1 <= n <= len(sentences) and exact_copy(sentences[n - 1], articles)]
    bad = [n for n in bad if n not in cleared]
    ok = obj["fits_situation"] and not bad
    why = str(obj.get("reason", ""))[:200] + (f"; sentences {cleared} are exact copies of the article" if cleared else "")
    if ok:
        return Check("grounding_model", True, f"fits and supported ({why})", tokens_in=t_in, tokens_out=t_out,
                     cached=hit, memo=memo)
    parts = ([] if obj["fits_situation"] else ["the article does not fit the situation"]) + \
            ([f"sentences {bad} not supported"] if bad else [])
    return Check("grounding_model", False, "; ".join(parts) + f" ({why})", tokens_in=t_in, tokens_out=t_out,
                 cached=hit, memo=memo, bad=tuple(bad), trimmable=bool(obj["fits_situation"] and bad))


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
    # 11 Nov: the new layout's additions (headings, "Here is what to do:", bullet dashes, "(also in: ...)", and from
    # PR-01 v1.6 the line "Common causes listed in the article:") are not
    # counted, so the limit stays exactly as strict as before; the greeting, steps and notice still count.
    own = re.sub(r"\s*\(also in: [^)]*\)", "", reply.replace(" Here is what to do:", ""))
    own = " ".join(l[2:] if l.startswith("- ") else l for l in own.splitlines()
                   if not l.startswith("From our help article") and l != "Common causes listed in the article:")
    limit = MAX_WORDS_TWO_ARTICLES if reply.count("From our help article") >= 2 else MAX_WORDS
    if len(own.split()) > limit:
        found.append(f"too long ({len(own.split())} words, limit {limit})")
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


# ---------- 10 Nov: trim instead of block (experiment 1B; on by default from 12 Nov) ----------
TRIM_MAX_SHARE = 0.5     # at most half of the sentences may be removed; otherwise the reply is not enough


def trim(draft, report):
    """A copy of the draft without the sentences that failed, or None when trimming is not allowed.
    Allowed only when every failed check is a grounding check that named its sentences, and the
    article fits the situation. Private data, instructions, tone and confidence are never trimmed."""
    import dataclasses
    from src.generate import assemble
    failed = [c for c in report.checks if not c.passed]
    if not failed or any(c.error or c.name not in ("grounding_words", "grounding_model") or not c.trimmable
                         for c in failed):
        return None
    bad = {n for c in failed for n in c.bad}
    keep = [s for k, s in enumerate(draft.sentences, 1) if k not in bad]
    if not keep or len(bad) > TRIM_MAX_SHARE * len(draft.sentences):
        return None
    cited = tuple(dict.fromkeys(d for s in keep for d in s["doc_ids"]))
    return dataclasses.replace(draft, sentences=tuple(keep), reply=assemble(keep), cited_doc_ids=cited)
