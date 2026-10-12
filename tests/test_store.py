from packages.ingestion import store


def test_normalize_name() -> None:
    assert store.normalize_name("Dr. Jane A. Doe!") == "dr jane a doe"
    assert store.normalize_name("Müller & Co.") == "muller co"


def test_hash_embed_fallback() -> None:
    from packages.embeddings import embed

    vec = embed._hash_embed("hello world")
    assert len(vec) == embed.settings.embedding_dim
    norm = sum(v * v for v in vec) ** 0.5
    assert abs(norm - 1.0) < 1e-6
