"""The Groq free tier's limits, as Groq reports them on every model call (the web page's limit bars).

Attribution: written with Claude (Anthropic), reviewed and run by Mohnish Grover.
Every answer from Groq carries headers saying how much of its limits is left: requests per day
(x-ratelimit-limit-requests / -remaining-requests) and tokens per minute (x-ratelimit-limit-tokens /
-remaining-tokens), with the time until each refills. call_model (src/generate.py) passes them here after every
call, including refused ones (HTTP 429), so the page can show how close each model is to its limit without making
any extra call. check_now() makes one tiny call to each model on request. Nothing here changes a decision.
"""
import os
import re
import threading
import time

_LOCK = threading.Lock()
_SEEN = {}                      # model -> what the last answer said about its limits
_REFUSED = {}                   # model -> times of HTTP 429 answers
WINDOW = 600                    # refusals counted over the last 10 minutes


def _number(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def seconds(v) -> float:
    """Groq's refill times ("285ms", "7.66s", "1m26.4s", "2h3m4s") in seconds."""
    if v is None:
        return 0.0
    v = str(v).strip()
    if re.fullmatch(r"[\d.]+", v):
        return float(v)
    total = 0.0
    for amount, unit in re.findall(r"([\d.]+)(ms|h|m|s)", v):
        total += float(amount) * {"ms": 0.001, "s": 1, "m": 60, "h": 3600}[unit]
    return round(total, 3)


def note(model, headers, status, now=None) -> None:
    """Called by call_model after every answer from the provider."""
    now = time.time() if now is None else now
    h = {k.lower(): v for k, v in dict(headers or {}).items()}
    with _LOCK:
        if status == 429:
            _REFUSED.setdefault(model, []).append(now)
        old = _SEEN.get(model, {})
        if "x-ratelimit-limit-tokens" in h or not old:
            _SEEN[model] = {
                "at": now, "status": status,
                "requests_limit": _number(h.get("x-ratelimit-limit-requests")),
                "requests_left": _number(h.get("x-ratelimit-remaining-requests")),
                "requests_reset_s": seconds(h.get("x-ratelimit-reset-requests")),
                "tokens_limit": _number(h.get("x-ratelimit-limit-tokens")),
                "tokens_left": _number(h.get("x-ratelimit-remaining-tokens")),
                "tokens_reset_s": seconds(h.get("x-ratelimit-reset-tokens")),
                "retry_after_s": _number(h.get("retry-after")),
            }
        else:                                   # a refusal without limit headers: keep the last figures
            old.update(at_refused=now, status=status, retry_after_s=_number(h.get("retry-after")))


def role_of(model) -> str:
    names = {os.getenv("MODEL_NAME", "openai/gpt-oss-20b"): "writer",
             os.getenv("BACKUP_MODEL_NAME", "openai/gpt-oss-120b"): "backup writer",
             os.getenv("GUARDRAIL_MODEL", "qwen/qwen3.8-27b"): "grounding check"}
    return names.get(model, "model")


def snapshot(now=None) -> list:
    """Each model seen so far: how much of each limit is used now (0 once the refill time has passed)."""
    now = time.time() if now is None else now
    out = []
    with _LOCK:
        for model, s in _SEEN.items():
            age = now - s["at"]
            def used(limit, left, reset):
                if limit is None or left is None:
                    return None
                return 0.0 if age >= reset else max(0.0, limit - left)
            refused = [t for t in _REFUSED.get(model, []) if now - t <= WINDOW]
            _REFUSED[model] = refused
            out.append({"model": model, "role": role_of(model), "seconds_ago": round(age, 1),
                        "status": s.get("status"),
                        "tokens_limit": s["tokens_limit"],
                        "tokens_used": used(s["tokens_limit"], s["tokens_left"], s["tokens_reset_s"]),
                        "tokens_refill_in": round(max(0.0, s["tokens_reset_s"] - age), 1),
                        "requests_limit": s["requests_limit"],
                        "requests_used": used(s["requests_limit"], s["requests_left"], s["requests_reset_s"]),
                        "refused_last_10_min": len(refused),
                        "last_refused_ago": round(now - refused[-1], 1) if refused else None})
    order = {"writer": 0, "backup writer": 1, "grounding check": 2}
    return sorted(out, key=lambda r: order.get(r["role"], 3))


def models() -> list:
    return [os.getenv("MODEL_NAME", "openai/gpt-oss-20b"), os.getenv("BACKUP_MODEL_NAME", "openai/gpt-oss-120b"),
            os.getenv("GUARDRAIL_MODEL", "qwen/qwen3.8-27b")]


def check_now(call=None) -> list:
    """One tiny call to each model ("Reply with the word ready.", at most 20 tokens back), so the page shows fresh
    figures. A refusal is shown, never raised."""
    if call is None:
        from src.generate import call_model as call
    results = []
    for model in models():
        try:
            call([{"role": "user", "content": "Reply with the word ready."}], model, max_tokens=20,
                 role="checker" if role_of(model) == "grounding check" else "writer")
            results.append({"model": model, "answer": "works"})
        except Exception as e:  # noqa: BLE001 - the page says what happened
            results.append({"model": model, "answer": f"{type(e).__name__}: {e}"})
    return results


def clear() -> None:
    """Forget everything seen (tests)."""
    with _LOCK:
        _SEEN.clear()
        _REFUSED.clear()
