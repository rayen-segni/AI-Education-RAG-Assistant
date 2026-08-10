from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from app.ingestion import storage
from pathlib import Path
from app.schemas import document
from app.services import rag
import json
from psycopg.errors import UniqueViolation



router = APIRouter(
    prefix="/document",
    tags=["Documents"]
)

@router.post("/save")
async def upload_file(
    file: UploadFile = File(...),
    chunk_size: int = Form(500),
    overlap_size: float = Form(0.1),
    subject: str = Form(""),
    metadata: str = Form("{}"),
):
    payload = document.DocumentRequest(
        chunk_size=chunk_size,
        overlap_size=overlap_size,
        subject=subject,
        metadata=json.loads(metadata),
    )

    path = await storage.save_uploaded_file(file)

    try: 
        await rag.insert_file(
            path,
            payload.chunk_size,
            overlap_ratio=payload.overlap_size,
            subject=payload.subject,
            metadata=payload.metadata
        )
    except UniqueViolation:
        raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="File Already exist"
                )
    except Exception:
        raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal Error"
                )




