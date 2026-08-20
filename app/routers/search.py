from fastapi import APIRouter

from app.schemas.search_sch import SearchRequest
from app.retrieval import retriever, reranker


router = APIRouter(
    prefix="/search",
    tags=["Search"]
)


@router.api_route("/", methods=["QUERY"])
async def search_documents(payload: SearchRequest):

    filters = None
    if payload.filters:
        filters = payload.filters.model_dump()


    chunks_rows = await retriever.retrieval(
        query=payload.query,
        filters=filters,
        top_k=20,
        threshold=payload.threshold,
        )

    final_chunks = await reranker.reranker(
        payload.query, 
        [chunk[2] for chunk in chunks_rows]
        )

    

    response = {
        "query": payload.query,
        "filters": filters,
        "result": chunks_rows
    }

    return response


