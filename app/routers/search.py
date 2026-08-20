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

    sources = [chunk[4]["source"] for chunk in chunks_rows if "source" in chunk[4]]
    subjects = [chunk[4]["subject"] for chunk in chunks_rows if "subject" in chunk[4]]

    final_chunks = await reranker.reranker(
        payload.query, 
        [chunk[2] for chunk in chunks_rows]
        )

    response = {
        "query": payload.query,
        "filters": filters,
        "result": chunks_rows,
        "sources": list(dict.fromkeys(sources)),
        "subjects": list(dict.fromkeys(subjects))
    }

    return response


