"""
Reranker of retrieved chunks
"""
from sentence_transformers import CrossEncoder

from app.config import settings

MODEL: CrossEncoder | None = None

async def reranker(
    query: str,
    candidates: list[str],
    top_k: int = 5
):

    # Fallback in case load_model wasn't called
    if MODEL is None:
        load_model()

    pairs = [
        (query, candidate)
        for candidate in candidates
    ]

    scores = MODEL.predict(pairs) # type: ignore

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



def load_model():
    """Load reranker weights into memory."""
    global MODEL
    if MODEL is None:
        print("Loading CrossEncoder reranker model...")
        MODEL = CrossEncoder(settings.CROSS_ENCODER_MODEL, device="cpu")

