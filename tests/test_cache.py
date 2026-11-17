"""The reply cache (D-025) and its read-only mode (15 Nov 2026, Mohnish Grover): REPLY_CACHE=read reuses stored
development answers but stores nothing new, so a validation run adds no validation answers to the cache."""
from src import cache


def test_a_stored_answer_is_found_again(tmp_path, monkeypatch):
    monkeypatch.setenv("CACHE_PATH", str(tmp_path / "c.db"))
    monkeypatch.setenv("REPLY_CACHE", "on")
    cache.put("k1", "reply", "model-a")
    assert cache.get("k1") == ("reply", "model-a")


def test_read_only_reuses_but_stores_nothing(tmp_path, monkeypatch):
    monkeypatch.setenv("CACHE_PATH", str(tmp_path / "c.db"))
    monkeypatch.setenv("REPLY_CACHE", "on")
    cache.put("dev", "development reply", "model-a")             # filled by a development run
    monkeypatch.setenv("REPLY_CACHE", "read")
    assert cache.enabled() and cache.read_only()
    assert cache.get("dev") == ("development reply", "model-a")  # reused
    cache.put("val", "validation reply", "model-a")              # a validation answer
    assert cache.get("val") is None                               # was not stored


def test_off_means_off(monkeypatch):
    monkeypatch.setenv("REPLY_CACHE", "off")
    assert not cache.enabled() and not cache.read_only()
