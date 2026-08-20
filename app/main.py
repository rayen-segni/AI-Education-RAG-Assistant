"""
App Entry Point
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager

from .routers import chat, document, search
from app.retrieval import reranker
from app.services import embedding_service

@asynccontextmanager
async def lifesapn(app: FastAPI):
    yield


app = FastAPI(lifespan=lifesapn)

@app.get("/")
def get_root():
    """
    Root Function
    """
    return {"message": "Welcome To RAG assistant"}


app.include_router(document.router)
app.include_router(chat.router)
app.include_router(search.router)
