from pydantic import BaseModel
from typing import Optional
from app.schemas.document_sch import DocumentMetadata


class SearchBase(BaseModel):
    query: str

class SearchRequest(SearchBase):
    filters: Optional[DocumentMetadata] = None
    threshold: float = 0

class SearchResponse(SearchBase):
    filters: list[DocumentMetadata]
    result: list[str]
