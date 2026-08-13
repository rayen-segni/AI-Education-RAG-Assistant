"""
Manage Documents path operations
"""

from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from pydantic import ValidationError

from app.ingestion import storage
from app.schemas import document_sch
from app.services.file_service import FileProcessor



router = APIRouter(
    prefix="/document",
    tags=["Documents"]
)

@router.post("/")
async def upload_file(
    file: UploadFile = File(...),
    metadata: str = Form("{}"),
):
    """Take the file and save it in the disk and in the database,
    chunk it and save its chunks in the database

    Args:
        file (UploadFile, optional): The file to save. required.
        metadata (str, optional): The metadata of the file . Defaults to Form("{}").

    Raises:
        HTTPException 422: Missed fields in metadata
        HTTPException 409: Document Already exist
    """

    # Save the file
    path = await storage.save_uploaded_file(file)

    # Validate metadata:
    try:
        metadata_obj = document_sch.DocumentMetadata.model_validate_json(metadata)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.errors()
        )

    processor = FileProcessor(path, metadata_obj.model_dump())

    chunks = processor.chunking_file()
    doc_id = await processor.insert_file(chunks)

    if doc_id is not None:
        await processor.insert_chunks(doc_id, chunks)

    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="File already exist"
    )
