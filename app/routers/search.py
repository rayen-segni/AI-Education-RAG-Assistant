from fastapi import APIRouter

from app.schemas.search_sch import SearchRequest
from app.retrieval import retrieval


router = APIRouter(
    prefix="/search",
    tags=["Search"]
)


@router.api_route("/", methods=["QUERY"])
async def search_documents(payload: SearchRequest):

    chunks = await retrieval.retrieval(payload.query, payload.filters.model_dump())

