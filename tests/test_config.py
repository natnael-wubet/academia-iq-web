from apps.api.core import config


def test_get_settings() -> None:
    cfg = config.get_settings()
    assert cfg.app_name == "Academia IQ"
    assert cfg.api_v1_prefix == "/api/v1"


def test_cache_key_order_insensitive() -> None:
    from apps.api.core import cache

    k1 = cache.cache_key("a", {"b": 1}, (1, 2))
    k2 = cache.cache_key((1, 2), {"b": 1}, "a")
    assert k1 == k2
