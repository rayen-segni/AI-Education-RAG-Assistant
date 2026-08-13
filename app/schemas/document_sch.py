""""
Document schemas
"""

from pydantic import BaseModel

class DocumentBase(BaseModel):
    pass

class DocumentMetadata(BaseModel):
    course: str
    subject: str

    model_config = {
        "extra": "allow"
    }



class DocumentRequest(DocumentBase):
    chunk_size: int = 500
    overlap_size: float = 0.1
    subject: str = ""
    metadata: dict = {}

class DocumentResponse(DocumentBase):
    status: bool