"""
App Entry Point
"""

from fastapi import FastAPI
from .routers import document, question

app = FastAPI()

@app.get("/")
def get_root():
    """
    Root Function
    """
    return {"message": "Welcome To RAG assistant"}


app.include_router(document.router)
app.include_router(question.router)
