from collections.abc import Sequence

from app.services import embedding_service
from app.repository.documents import DocumentsRepository


async def retrieval(
    query: str,
    filters: dict | None = None,
    top_k: int = 5,
    threshold: float = 0
) -> list:

    response: Sequence[Sequence[float]] = await embedding_service.embedding(query)

    vector = list(response[0])

    chunks = await DocumentsRepository.search_chunks(vector,
                                                    filters,
                                                    top_k)

    filtred_chunks = [chunk for chunk in chunks if chunk[3] >= threshold]

    return filtred_chunks