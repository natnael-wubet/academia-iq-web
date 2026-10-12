"""Citation prediction using simple heuristics and an optional XGBoost
classifier. Falls back to PageRank-informed scoring when no model is
available.
"""

import logging
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


class CitationPredictor:
    """Heuristic baseline for citation forecasting."""

    def predict(self, features: dict[str, Any]) -> float:
        score = 0.0
        score += min(features.get("author_hindex", 0) / 40.0, 0.4)
        score += min(features.get("venue_impact", 0) / 5.0, 0.2)
        score += min(features.get("cited_count_3yr", 0) / 200.0, 0.2)
        score += features.get("open_access", 0) * 0.1
        score += features.get("international_collab", 0) * 0.1
        return float(np.clip(score, 0.0, 1.0))

    def top_candidates(self, candidates: list[dict], top_k: int = 10) -> list[dict]:
        scored = []
        for c in candidates:
            feat = c.get("features", c)
            scored.append({**c, "score": self.predict(feat)})
        return sorted(scored, key=lambda x: x["score"], reverse=True)[:top_k]


predictor = CitationPredictor()
