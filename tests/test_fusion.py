from apps.api.search import fusion
from apps.api.schemas.common import SearchHit


def test_rrf_merges_ranks() -> None:
    a = [SearchHit(id=1, title="A"), SearchHit(id=2, title="B")]
    b = [SearchHit(id=2, title="B"), SearchHit(id=1, title="A")]
    fused = fusion.reciprocal_rank_fusion([a, b], limit=2)
    ids = [h.id for h in fused]
    assert ids == [1, 2] or ids == [2, 1] or ids == [1, 2]
    assert fused[0].score >= fused[1].score


def test_rrf_dedups() -> None:
    a = [SearchHit(id=1, title="A"), SearchHit(id=2, title="B")]
    b = [SearchHit(id=2, title="B")]
    fused = fusion.reciprocal_rank_fusion([a, b], limit=5)
    assert len(fused) == 2
