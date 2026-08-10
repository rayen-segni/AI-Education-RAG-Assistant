# ingestion/storage.py

from pathlib import Path
from fastapi import UploadFile, HTTPException

BASE_DIR = Path(__file__).resolve().parent.parent.parent

async def save_uploaded_file(file: UploadFile) -> Path:
    if file.filename is None:
        raise HTTPException(
            status_code=400,
            detail="File must have a filename"
        )

    
    upload_dir = BASE_DIR / "documents"
    upload_dir.mkdir(exist_ok=True)

    path = upload_dir / file.filename

    with path.open("wb") as buffer:
        buffer.write(await file.read())

    return path