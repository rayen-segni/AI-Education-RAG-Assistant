from pydantic import BaseModel
from fastapi import UploadFile



class DocumentBase(BaseModel):
    pass

class DocumentRequest(DocumentBase):
    chunk_size: int = 500
    overlap_size: float = 0.1
    subject: str = ""
    metadata: dict = {}

class DocumentResponse(DocumentBase):
    status: bool