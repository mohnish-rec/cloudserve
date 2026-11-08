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
from dataclasses import dataclass, field
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()
ROOT = Path(__file__).resolve().parent.parent
PROMPT_DIR = ROOT / "prompts" / "build"
ACTIVE_PROMPT = ("PR-01_draft_reply.md", "PR-01 v1.2")    # one pointer: rollback = change this line
NO_ANSWER = ("The help articles we have do not cover this question, so I have passed your ticket "
             "to a specialist, who will reply to you directly.")
NOTICE = ("\n\nThis reply was written automatically from our help article \"{title}\" ({doc_id}). "
          "If it does not solve your problem, just reply to this message and a member of our "
          "support team will pick it up.")          # FR-08: added by code, never by the model
MAX_TRIES, BASE_WAIT, MAX_WAIT = 4, 1.0, 20.0
TOP_ARTICLES = 3            # PR-01 v1.1: the model reads whole articles (small-to-big, Module 5)
_ARTICLES = {}


class PermanentError(Exception):
    """Wrong key, bad request, unknown model: retrying will not help."""


class TransientError(Exception):
    """Rate limit, server error, timeout, network: worth retrying."""


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


def number_passages(articles) -> str:
    return "\n\n".join(f"[{i}] {a['doc_id']} · {a['title']}\n{a['content']}" for i, a in enumerate(articles, 1))


def call_model(messages, model, max_tokens=1200):
    """The Setup Guide's request, raising TransientError or PermanentError on failure."""
    body = {"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": 0}
    if "gpt-oss" in model:
        body["reasoning_effort"] = "low"
    try:
        r = requests.post(f"{os.environ['LLM_BASE_URL']}/chat/completions",
                          headers={"Authorization": f"Bearer {os.environ['LLM_API_KEY']}"},
                          json=body, timeout=30)
    except (requests.ConnectionError, requests.Timeout) as e:
        raise TransientError(type(e).__name__) from e
    if r.status_code == 429 or r.status_code >= 500:
        raise TransientError(f"HTTP {r.status_code}")
    if r.status_code != 200:
        raise PermanentError(f"HTTP {r.status_code}: {r.text[:120]}")
    return r.json()["choices"][0]["message"].get("content") or ""


def call_with_fallback(messages, models=None, call=call_model, sleep=time.sleep):
    """Main model with retries, then the backup model; returns (text, model, calls)."""
    models = models or [os.getenv("MODEL_NAME", "openai/gpt-oss-20b"),
                        os.getenv("BACKUP_MODEL_NAME", "openai/gpt-oss-120b")]
    calls, last = 0, ""
    for model in models:
        for attempt in range(MAX_TRIES):
            calls += 1
            try:
                return call(messages, model), model, calls
            except PermanentError as e:
                last = f"{model}: {e}"
                break                                    # no retry: move to the backup model
            except TransientError as e:
                last = f"{model}: {e}"
                if attempt < MAX_TRIES - 1:
                    sleep(random.uniform(0, min(MAX_WAIT, BASE_WAIT * 2 ** attempt)))
    raise TransientError(f"all models failed after {calls} calls (last: {last})")


GREETING = "Thanks for getting in touch."


def assemble(sentences) -> str:
    """The code, not the model, writes the greeting and the [n] numbers (PR-01 v1.2)."""
    parts = [GREETING]
    for s in sentences:
        marks = "".join(f"[{n}]" for n in dict.fromkeys(s["sources"]))
        text = re.sub(r"\s*(\[\d+\])+", "", s["text"]).strip()
        # An item holding two sentences gets the source on each (found on 8 Nov, DEV-0004).
        for piece in (x for x in re.split(r"(?<=[.!?])\s+(?=[A-Z])", text) if x.strip()):
            if piece[-1] in ".!?":
                parts.append(f"{piece[:-1]} {marks}{piece[-1]}")
            else:
                parts.append(f"{piece} {marks}.")
    return " ".join(parts)


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
    messages = [{"role": "system", "content": system},
                {"role": "user", "content": user.format(no_answer=NO_ANSWER, intent=intent,
                                                        passages=number_passages(articles),
                                                        ticket=ticket_text.replace("</ticket>", "< /ticket>"))}]
    try:
        raw, model, calls = call_with_fallback(messages, call=call, sleep=sleep)
    except Exception as e:  # noqa: BLE001 - model unavailable: escalate with the reason
        return Draft(ok=False, error=f"model unavailable: {e}",
                     latency_ms=int((time.perf_counter() - start) * 1000))
    ms = int((time.perf_counter() - start) * 1000)
    try:
        obj = parse(raw, len(articles))
    except Exception as e:  # noqa: BLE001 - output we cannot parse is escalated, never sent (FR-05)
        return Draft(ok=False, model=model, calls=calls, latency_ms=ms, raw=raw,
                     error=f"reply could not be read: {e}")
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
                 latency_ms=ms, raw=raw, error="" if answered else "the articles do not answer it")


def with_notice(draft: Draft, passages=None) -> str:
    """The customer-facing text: the model's reply plus the fixed notice (FR-08)."""
    articles_for(passages or [])                      # make sure the article titles are loaded
    doc_id = draft.cited_doc_ids[0]
    title = _ARTICLES.get(doc_id, {}).get("title") or next(
        (p.title for p in passages or [] if p.doc_id == doc_id), doc_id)
    return draft.reply + NOTICE.format(title=title, doc_id=doc_id)
