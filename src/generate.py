"""Generate: a reply written only from the articles found, with citations (FR-05, FR-07, FR-11).

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
The model call follows the Setup Guide's own request (scripts/check_model.py), with
retries and the backup model added (FR-11, Module 2: retry temporary errors with
increasing random waits, fail fast on permanent ones, then fall back). The prompt
lives in prompts/build/ and is versioned there (Stage 3 prompt register).

Never raises: any failure returns a Draft with ok=False and the reason, and the
caller escalates the ticket (fail closed).
"""
import json
import os
import random
import re
import time
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import requests
from dotenv import load_dotenv

from src import cache

load_dotenv()
ROOT = Path(__file__).resolve().parent.parent
PROMPT_DIR = ROOT / "prompts" / "build"
# The prompt file can be chosen per run (PR01_FILE) and its version is read from the file itself.
# 12 Nov 2026: the default is the final prompt, v1.7; rollback = PR01_FILE=PR-01_draft_reply.md (v1.2).
_PR01_FILE = os.getenv("PR01_FILE", "PR-01_draft_reply_v1.7.md")
_v = re.search(r"\*\*Version:\*\*\s*([0-9.]+)", (Path(__file__).resolve().parent.parent / "prompts" / "build" / _PR01_FILE)
               .read_text(encoding="utf-8"))
ACTIVE_PROMPT = (_PR01_FILE, f"PR-01 v{_v.group(1) if _v else '?'}")
# PR-01 v1.4 (11 Nov): extractive. The model chooses labelled article pieces; the code copies them word for word.
EXTRACTIVE = "**Mode:** extractive" in (PROMPT_DIR / _PR01_FILE).read_text(encoding="utf-8")
# PR-01 v1.6 (11 Nov): the code adds every Resolution step of each article the model answers from (Mohnish Grover).
ALL_STEPS = "**Steps:** all" in (PROMPT_DIR / _PR01_FILE).read_text(encoding="utf-8")
# PR-01 v1.7 (11 Nov): for the main article, every Note and Common cause as well (the whole article minus Symptoms).
WHOLE_ARTICLE = "**Pieces:** whole article" in (PROMPT_DIR / _PR01_FILE).read_text(encoding="utf-8")
NO_ANSWER = ("The help articles we have do not cover this question, so I have passed your ticket "
             "to a specialist, who will reply to you directly.")
NOTICE = ("\n\nThis reply was written automatically from the help {articles} named above. "
          "If it does not solve your problem, just reply to this message and a member of our "
          "support team will pick it up.")          # FR-08: added by code, never by the model
# 11 Nov: the customer sees each step under the article it came from, with no [n] numbers (Ravi: "here is the
# page it came from"; Build Spec: citations attached to claims). These lines are written by code, not the model.
HEADING = 'From our help article "{title}":'
ALSO = ' (also in: {titles})'
CAUSES = "Common causes listed in the article:"   # 11 Nov (v1.6): written by code; the causes below it are Ines's words
MAX_TRIES, BASE_WAIT, MAX_WAIT = 6, 1.0, 60.0   # 8 Nov: 4 quick tries were not enough for a 429 on the free tier
TOP_ARTICLES = int(os.getenv("WRITER_ARTICLES", "3"))   # PR-01 v1.1: whole articles (Module 5)
_ARTICLES = {}


class Reply(str):
    """The model's text, carrying the provider's token counts (8 Nov: measure the budget, don't guess)."""
    usage: dict = {}
    cached: bool = False          # True: reused from the reply cache, no call made (D-025)
    cache_key: str = ""


def tokens_of(text) -> tuple:
    u = getattr(text, "usage", None) or {}
    return int(u.get("prompt_tokens", 0) or 0), int(u.get("completion_tokens", 0) or 0)


class PermanentError(Exception):
    """Wrong key, bad request, unknown model: retrying will not help."""


class TransientError(Exception):
    """Rate limit, server error, timeout, network: worth retrying."""

    def __init__(self, message="", retry_after=0.0):
        super().__init__(message)
        self.retry_after = retry_after    # seconds the provider asked us to wait (Retry-After header)


@dataclass
class Draft:
    ok: bool                      # False: escalate (model unavailable, unparseable, or not answered)
    answered: bool = False
    reply: str = ""               # assembled by the code from the sentences, before the notice
    sentences: tuple = ()         # ({"text", "sources", "doc_ids"}, ...): each sentence keeps its source
    citations: tuple = ()         # passage numbers, 1-based
    cited_doc_ids: tuple = ()
    sure: str = "not sure"
    summary: str = ""
    unsure_about: str = ""
    model: str = ""
    prompt_version: str = ACTIVE_PROMPT[1]
    calls: int = 0
    cached: bool = False          # reused from the reply cache (D-025)
    tokens_in: int = 0            # as reported by the provider, for the budget (NFR-07)
    tokens_out: int = 0
    latency_ms: int = 0
    error: str = ""
    raw: str = field(default="", repr=False)


def load_prompt(name=ACTIVE_PROMPT[0]):
    text = (PROMPT_DIR / name).read_text(encoding="utf-8")
    system = text.split("### SYSTEM", 1)[1].split("### USER", 1)[0].strip()
    user = text.split("### USER", 1)[1].strip()
    return system, user


def articles_for(passages, top=TOP_ARTICLES) -> list:
    """Search finds small passages; the model reads the whole article each one came from
    (found on 7 Nov: a 400-character piece was often only the Symptoms list)."""
    if not _ARTICLES:
        from src.retrieve import load_documents
        _ARTICLES.update({d["doc_id"]: d for d in load_documents()})
    out = []
    for p in passages:
        if p.doc_id not in {a["doc_id"] for a in out}:
            doc = _ARTICLES.get(p.doc_id, {"doc_id": p.doc_id, "title": p.title, "content": p.text})
            out.append({"doc_id": doc["doc_id"], "title": doc["title"], "content": doc["content"]})
        if len(out) == top:
            break
    return out


def article_pieces(content) -> tuple:
    """11 Nov (PR-01 v1.4): an article as (symptoms, pieces). Pieces are ("R1", text) for each Resolution step
    (kept whole, so a step stays with its own explanation), ("C1", text) for each Common cause and ("N1", text)
    for each sentence of the Notes, all exactly as written."""
    sections = dict(re.findall(r"^## (.+?)\n(.*?)(?=^## |\Z)", content, re.M | re.S))
    bullets = lambda s: [b.strip() for b in re.findall(r"^\s*-\s+(.+)$", s or "", re.M)]
    steps = [x.strip() for x in re.findall(r"^\s*\d+\.\s+(.+)$", sections.get("Resolution", ""), re.M)]
    notes = [x.strip() for x in re.split(r"(?<=[.!?])\s+", " ".join((sections.get("Notes") or "").split())) if x.strip()]
    pieces = ([(f"R{i}", t) for i, t in enumerate(steps, 1)] + [(f"C{i}", t) for i, t in enumerate(bullets(sections.get("Common causes")), 1)]
              + [(f"N{i}", t) for i, t in enumerate(notes, 1)])
    return bullets(sections.get("Symptoms")), pieces


def number_pieces(articles) -> str:
    """The articles as the extractive writer sees them: symptoms for matching, then every piece with its label."""
    out = []
    for k, a in enumerate(articles, 1):
        symptoms, pieces = article_pieces(a["content"])
        out.append(f"[{k}] {a['doc_id']} · {a['title']}\nSymptoms (for matching only, never chosen): {'; '.join(symptoms)}\n"
                   "Pieces you may choose:\n" + "\n".join(f"{k}.{code}  {text}" for code, text in pieces))
    return "\n\n".join(out)


def parse_pieces(raw: str, labels: dict):
    """Module 2's defensive parse for v1.4: every chosen label must exist; nothing else is accepted."""
    s = re.sub(r"^`{3}(?:json)?|`{3}$", "", (raw or "").strip(), flags=re.M).strip()
    m = re.search(r"\{.*\}", s, re.S)
    if not m:
        raise ValueError("no JSON object")
    obj = json.loads(m.group(0))
    problems = []
    if not isinstance(obj.get("answered"), bool):
        problems.append("answered must be true or false")
    chosen = obj.get("pieces")
    if not isinstance(chosen, list):
        problems.append("pieces is not a list")
        chosen = []
    unknown = [c for c in chosen if c not in labels]
    if unknown:
        problems.append(f"labels that do not exist: {unknown[:5]}")
    if obj.get("answered") is True and not chosen:
        problems.append("an answer with no pieces")
    if len(chosen) > 8:
        problems.append("more than eight pieces")
    if obj.get("sure") not in ("sure", "not sure"):
        problems.append("sure must be 'sure' or 'not sure'")
    if problems:
        raise ValueError("; ".join(problems))
    obj["pieces"] = list(dict.fromkeys(chosen))
    return obj


def complete_steps(chosen, labels) -> list:
    """PR-01 v1.6 (11 Nov): for every article the model took a Resolution step from, all of that article's steps, in
    the article's order; then the Notes and then the Common causes the model chose, each in the article's order.
    Articles keep the order in which the model first used them. Found 11 Nov: told to keep conditional steps, the
    model still left out the database-migration step in all 28 rollback replies. PR-01 v1.7: the main article (the
    first one the model took a step from) also brings every Note and Common cause; a second article only its steps."""
    order = lambda p: (p.split(".")[1][0] != "R", p.split(".")[1][0] == "C", int(p.split(".")[1][1:]))
    arts = list(dict.fromkeys(p.split(".")[0] for p in chosen))
    with_steps = {p.split(".")[0] for p in chosen if p.split(".")[1].startswith("R")}
    out = []
    main = next((a for a in arts if a in with_steps), None)
    for a in arts:
        mine = [p for p in chosen if p.split(".")[0] == a]
        if a in with_steps:
            mine += [p for p in labels if p.split(".")[0] == a and p.split(".")[1].startswith("R")]
        if WHOLE_ARTICLE and a == main:     # v1.7: the main article in full (its Notes and Common causes too)
            mine += [p for p in labels if p.split(".")[0] == a]
        out += sorted(dict.fromkeys(mine), key=order)
    return out


def number_passages(articles) -> str:
    return "\n\n".join(f"[{i}] {a['doc_id']} · {a['title']}\n{a['content']}" for i, a in enumerate(articles, 1))


def provider(role="writer") -> dict:
    """Both the writer and the checker use Groq's free tier directly (LLM_BASE_URL, LLM_API_KEY; D-024).
    The role is kept so the run memory's key names where an answer came from."""
    return {"base_url": os.environ["LLM_BASE_URL"], "api_key": os.environ["LLM_API_KEY"], "pin": ""}


def call_model(messages, model, max_tokens=2000, role="writer"):
    """The Setup Guide's request, raising TransientError or PermanentError on failure."""
    p = provider(role)
    body = {"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": 0}
    if "gpt-oss" in model:
        body["reasoning_effort"] = "low"
    try:
        r = requests.post(f"{p['base_url']}/chat/completions",
                          headers={"Authorization": f"Bearer {p['api_key']}"},
                          json=body, timeout=60)
    except (requests.ConnectionError, requests.Timeout) as e:
        raise TransientError(type(e).__name__) from e
    if r.status_code == 429 or r.status_code >= 500:
        try:
            wait = float(r.headers.get("retry-after", 0) or 0)
        except ValueError:
            wait = 0.0
        raise TransientError(f"HTTP {r.status_code}", retry_after=wait)
    if r.status_code != 200:
        raise PermanentError(f"HTTP {r.status_code}: {r.text[:120]}")
    data = r.json()
    out = Reply(data["choices"][0]["message"].get("content") or "")
    out.usage = data.get("usage") or {}
    return out


# 12 Nov 2026, acceptance criterion A5 ("the same input produces the same routing decision"): within one run the
# same model input gets the same answer. Found in the final development run: two identical tickets (DEV-0156 and
# DEV-0399, "user left company...") got different decisions, because the hosted models are not perfectly repeatable
# even at temperature 0. This memory lasts only for the life of the process and is never saved, so every evaluation
# run is still a fresh test (D-025, 9 Nov). Order: saved cache (if on), then this memory, then the model. Like the
# cache, it keeps only answers that were read successfully (remember()), so a garbled answer is retried, not repeated.
# Only real calls use it; tests with fake models never do.
_RUN_MEMO = {}
_RUN_MEMO_MAX = 20000


def remember(raw, model):
    """Keep a successfully read answer for the rest of this run (A5). Called where the cache stores answers."""
    k = getattr(raw, "memo_key", "")
    if k and len(_RUN_MEMO) < _RUN_MEMO_MAX:
        _RUN_MEMO[k] = (str(raw), model)


def call_with_fallback(messages, models=None, call=call_model, sleep=time.sleep, role="writer"):
    """Main model with retries, then the backup model; returns (text, model, calls)."""
    models = models or [os.getenv("MODEL_NAME", "openai/gpt-oss-20b"),
                        os.getenv("BACKUP_MODEL_NAME", "openai/gpt-oss-120b")]
    k = ""
    real = call is call_model
    if real:
        call = (lambda m, mod, _r=role: call_model(m, mod, role=_r))
    if real and cache.enabled():            # only the real call; fake models never touch it
        route = provider(role)                   # 9 Nov: a different provider is a different answer
        k = cache.key(messages, models + [route["base_url"], route["pin"]])
        hit = cache.get(k)
        if hit:
            out = Reply(hit[0])
            out.cached, out.cache_key = True, k
            return out, hit[1], 0
    mkey = ""
    if real:                                     # A5: the same input earlier in this run, the same answer
        route = provider(role)
        mkey = cache.key(messages, models + [route["base_url"], route["pin"]])
        if mkey in _RUN_MEMO:
            text, model = _RUN_MEMO[mkey]
            out = Reply(text)
            out.memo = True
            return out, model, 0
    calls, last = 0, ""
    for model in models:
        for attempt in range(MAX_TRIES):
            calls += 1
            try:
                out = call(messages, model)
                if k and isinstance(out, Reply):
                    out.cache_key = k
                if mkey and isinstance(out, Reply):
                    out.memo_key = mkey
                return out, model, calls
            except PermanentError as e:
                last = f"{model}: {e}"
                break                                    # no retry: move to the backup model
            except TransientError as e:
                last = f"{model}: {e}"
                if attempt < MAX_TRIES - 1:
                    # Wait at least as long as the provider asks, plus backoff with jitter (Module 3).
                    backoff = random.uniform(0, min(MAX_WAIT, BASE_WAIT * 2 ** attempt))
                    sleep(min(MAX_WAIT, max(getattr(e, "retry_after", 0.0), backoff)))
    raise TransientError(f"all models failed after {calls} calls (last: {last})")


GREETING = "Thanks for getting in touch."


def _pieces(text):
    """One model sentence as clean sentences: no [n], normal spaces, a full stop at the end."""
    text = re.sub(r"\s*(\[\d+\])+", "", text).strip()
    # Unusual spaces and hyphens from the model showed as "corruptedartefact" on Windows (8 Nov).
    # Any Unicode space or invisible format character becomes a normal space (the first, narrower
    # list still left "migrationback", so the model uses another invisible character as well).
    text = "".join(" " if unicodedata.category(ch) in ("Zs", "Cf") else ch for ch in text.replace("\u2011", "-"))
    text = re.sub(r" {2,}", " ", text)
    # An item holding two sentences is split, each keeping the source (found on 8 Nov, DEV-0004).
    return [p if p[-1] in ".!?" else p + "." for p in (x.strip() for x in re.split(r"(?<=[.!?])\s+(?=[A-Z])", text)) if p]


def assemble(sentences) -> str:
    """The internal draft: greeting and [n] numbers written by the code (PR-01 v1.2). The guardrails' sentence
    numbers, the trim step and the answer library use it; the customer sees render() instead (11 Nov)."""
    parts = [GREETING]
    for s in sentences:
        marks = "".join(f"[{n}]" for n in dict.fromkeys(s["sources"]))
        parts += [f"{p[:-1]} {marks}{p[-1]}" for p in _pieces(s["text"])]
    return " ".join(parts)


def _title(doc_id, passages=None):
    articles_for(passages or [])                      # make sure the article titles are loaded
    return _ARTICLES.get(doc_id, {}).get("title") or next(
        (p.title for p in passages or [] if p.doc_id == doc_id), doc_id)


def render(draft: Draft, passages=None) -> str:
    """11 Nov: what a reader sees. Each step sits under the article it came from, in reading order, with no
    numbers; a step backed by two articles goes under the first and names the other as "(also in: ...)"."""
    groups = {}
    for s in draft.sentences:
        docs = list(dict.fromkeys(s["doc_ids"]))
        also = ALSO.format(titles=", ".join(f'"{_title(d, passages)}"' for d in docs[1:])) if docs[1:] else ""
        # 11 Nov: a piece copied from an article is shown exactly as Ines wrote it, with nothing added (a Common
        # cause has no full stop in the article, so none is added here either).
        texts = [s["text"].strip()] if s.get("verbatim") else _pieces(s["text"])
        kind = "cause" if ALL_STEPS and ".C" in s.get("piece", "") else "step"
        groups.setdefault(docs[0], []).extend((kind, f"- {p}{also}") for p in texts)
    lines = [f"{GREETING} Here is what to do:"]
    for doc_id, items in groups.items():
        lines += ["", HEADING.format(title=_title(doc_id, passages))] + [t for k, t in items if k == "step"]
        causes = [t for k, t in items if k == "cause"]
        lines += [CAUSES] + causes if causes else []
    return "\n".join(lines)


def parse(raw: str, n_articles: int):
    """Module 2's defensive parse: strip fences, find the object, load, then check every value."""
    s = re.sub(r"^`{3}(?:json)?|`{3}$", "", (raw or "").strip(), flags=re.M).strip()
    m = re.search(r"\{.*\}", s, re.S)
    if not m:
        raise ValueError("no JSON object in the reply")
    obj = json.loads(m.group(0))
    problems = []
    if not isinstance(obj.get("answered"), bool):
        problems.append("answered is not true or false")
    sentences = obj.get("sentences")
    if not isinstance(sentences, list):
        problems.append("sentences is not a list")
        sentences = []
    for k, item in enumerate(sentences, 1):
        if not isinstance(item, dict) or not isinstance(item.get("text"), str) or not item["text"].strip():
            problems.append(f"sentence {k} has no text")
            continue
        src = item.get("sources")
        if not isinstance(src, list) or not src:
            problems.append(f"sentence {k} has no source")
        elif not all(isinstance(n, int) and 1 <= n <= n_articles for n in src):
            problems.append(f"sentence {k} names a source that is not one of the {n_articles} articles")
    if obj.get("answered") is True and not sentences:
        problems.append("an answer with no sentences")
    if obj.get("sure") not in ("sure", "not sure"):
        problems.append("sure must be 'sure' or 'not sure'")
    if problems:
        raise ValueError("; ".join(problems))
    return obj


def generate(ticket_text, intent, passages, call=call_model, sleep=time.sleep) -> Draft:
    if not passages:
        return Draft(ok=False, error="no passages to answer from")
    start = time.perf_counter()
    articles = articles_for(passages)
    system, user = load_prompt()
    labels = {f"{k}.{code}": (text, a["doc_id"], k) for k, a in enumerate(articles, 1)
              for code, text in article_pieces(a["content"])[1]} if EXTRACTIVE else {}
    messages = [{"role": "system", "content": system},
                {"role": "user", "content": user.format(no_answer=NO_ANSWER, intent=intent,
                                                        passages=number_pieces(articles) if EXTRACTIVE
                                                        else number_passages(articles),
                                                        ticket=ticket_text.replace("</ticket>", "< /ticket>"))}]
    try:
        raw, model, calls = call_with_fallback(messages, call=call, sleep=sleep)
    except Exception as e:  # noqa: BLE001 - model unavailable: escalate with the reason
        return Draft(ok=False, error=f"model unavailable: {e}",
                     latency_ms=int((time.perf_counter() - start) * 1000))
    ms = int((time.perf_counter() - start) * 1000)
    t_in, t_out = tokens_of(raw)
    try:
        obj = parse_pieces(raw, labels) if EXTRACTIVE else parse(raw, len(articles))
    except Exception as e:  # noqa: BLE001 - output we cannot parse is escalated, never sent (FR-05)
        return Draft(ok=False, model=model, calls=calls, latency_ms=ms, raw=raw, tokens_in=t_in, tokens_out=t_out,
                     error=f"reply could not be read: {e}")
    if getattr(raw, "cache_key", "") and not getattr(raw, "cached", False):
        cache.put(raw.cache_key, raw, model)               # only answers that were read successfully
    remember(raw, model)                                   # A5 (12 Nov): this run reuses it for the same input
    if EXTRACTIVE:                 # the article's own words, exactly as written; the label is kept for the log
        answered = obj["answered"] and bool(obj["pieces"])
        chosen = complete_steps(obj["pieces"], labels) if (answered and ALL_STEPS) else obj["pieces"]
        sentences = tuple({"text": labels[p][0], "sources": (labels[p][2],), "doc_ids": (labels[p][1],),
                           "piece": p, "verbatim": True} for p in chosen) if answered else ()
    else:
        answered = obj["answered"] and bool(obj["sentences"])
        sentences = tuple({"text": x["text"].strip(), "sources": tuple(dict.fromkeys(x["sources"])),
                           "doc_ids": tuple(dict.fromkeys(articles[n - 1]["doc_id"] for n in x["sources"]))}
                          for x in obj["sentences"]) if answered else ()
    cites = tuple(dict.fromkeys(n for x in sentences for n in x["sources"]))
    return Draft(ok=answered, answered=answered, reply=assemble(sentences) if answered else NO_ANSWER,
                 sentences=sentences, citations=cites,
                 cited_doc_ids=tuple(dict.fromkeys(articles[c - 1]["doc_id"] for c in cites)),
                 sure=obj["sure"], summary=str(obj.get("summary", ""))[:300],
                 unsure_about=str(obj.get("unsure_about", ""))[:300], model=model, calls=calls,
                 cached=bool(getattr(raw, "cached", False)), tokens_in=t_in, tokens_out=t_out,
                 latency_ms=ms, raw=raw, error="" if answered else "the articles do not answer it")


def with_notice(draft: Draft, passages=None) -> str:
    """The customer-facing text (what the guardrails check and what is sent): render() plus the fixed notice (FR-08)."""
    n = len(dict.fromkeys(d for s in draft.sentences for d in s["doc_ids"]))
    return render(draft, passages) + NOTICE.format(articles="articles" if n > 1 else "article")
