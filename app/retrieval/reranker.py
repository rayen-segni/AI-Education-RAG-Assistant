"""
Reranker of retrieved chunks
"""
from sentence_transformers import CrossEncoder

from app.config import settings

MODEL = CrossEncoder(settings.CROSS_ENCODER_MODEL)

async def reranker(
    query: str,
    candidates: list[str],
    top_k: int = 5
):

    pairs = [
        (query, candidate)
        for candidate in candidates
    ]

    scores = MODEL.predict(pairs)

    ranked = sorted(zip(candidates, scores),
                    key=lambda x : x[1],
                    reverse=True)

    return [
        {
            "candidate": candidate,
            "rank_score": float(score)
        }
        for candidate, score in ranked[:top_k]
    ]
