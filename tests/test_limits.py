"""The free tier's limits for the web page's limit bars (src/limits.py), with made-up Groq headers: no real call."""
from src import limits

HEADERS = {"x-ratelimit-limit-requests": "1000", "x-ratelimit-remaining-requests": "990",
           "x-ratelimit-reset-requests": "14m24s", "x-ratelimit-limit-tokens": "8000",
           "x-ratelimit-remaining-tokens": "2000", "x-ratelimit-reset-tokens": "45.5s"}


def test_groq_refill_times_are_read_in_seconds():
    assert round(limits.seconds("285ms"), 3) == 0.285 and limits.seconds("7.66s") == 7.66
    assert limits.seconds("1m26.4s") == 86.4 and limits.seconds("2h3m4s") == 7384 and limits.seconds(None) == 0


def test_the_bars_show_what_is_used_and_empty_once_the_limit_refills():
    limits.clear()
    limits.note("qwen/qwen3.8-27b", HEADERS, 200, now=1000)
    m = limits.snapshot(now=1010)[0]
    assert m["role"] == "grounding check" and m["tokens_used"] == 6000 and m["tokens_limit"] == 8000
    assert m["requests_used"] == 10 and m["tokens_refill_in"] == 35.5 and m["refused_last_10_min"] == 0
    assert limits.snapshot(now=1050)[0]["tokens_used"] == 0          # 45.5 s later the minute's tokens are back


def test_refusals_are_counted_for_ten_minutes_and_keep_the_last_figures():
    limits.clear()
    limits.note("qwen/qwen3.8-27b", HEADERS, 200, now=1000)
    limits.note("qwen/qwen3.8-27b", {"retry-after": "3"}, 429, now=1005)
    m = limits.snapshot(now=1006)[0]
    assert m["refused_last_10_min"] == 1 and m["tokens_used"] == 6000 and m["status"] == 429
    assert limits.snapshot(now=1700)[0]["refused_last_10_min"] == 0


def test_check_now_calls_each_model_once_and_never_raises():
    limits.clear()
    called = []

    def fake(messages, model, max_tokens=2000, role="writer"):
        called.append((model, max_tokens))
        if "qwen" in model:
            raise RuntimeError("HTTP 429")
        limits.note(model, HEADERS, 200)
        limits.note_usage(model, {"total_tokens": 30})
    answers = limits.check_now(fake)
    assert limits.capacity()["tokens_per_ticket"]["writer"] == 1414    # the tiny check calls are not counted
    assert len(called) == 3 and all(t == 20 for _, t in called)
    assert [a["answer"] for a in answers][:2] == ["works", "works"] and "429" in answers[2]["answer"]


def test_how_many_tickets_can_be_answered_with_what_is_left(monkeypatch):
    for k in ("MODEL_NAME", "BACKUP_MODEL_NAME", "GUARDRAIL_MODEL"):
        monkeypatch.delenv(k, raising=False)
    limits.clear()
    full = dict(HEADERS, **{"x-ratelimit-remaining-tokens": "8000", "x-ratelimit-remaining-requests": "1000"})
    limits.note("openai/gpt-oss-20b", full, 200, now=1000)
    limits.note("qwen/qwen3.8-27b", HEADERS, 200, now=1000)          # 2,000 tokens left this minute, 990 requests
    c = limits.capacity(now=1001)
    assert c["tokens_per_ticket"] == {"writer": 1414, "grounding check": 492}     # development run figures
    assert c["now"] == 4 and c["per_minute"] == 5 and c["today"] == 990             # 2,000 // 492; 8,000 // 1,414
    limits.note_usage("qwen/qwen3.8-27b", {"total_tokens": 1000})
    c = limits.capacity(now=1001)
    assert c["tokens_per_ticket"]["grounding check"] == 1000 and c["now"] == 2 and "measured" in c["source"]["grounding check"]
