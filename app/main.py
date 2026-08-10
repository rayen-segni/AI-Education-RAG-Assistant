from fastapi import FastAPI
from .routers import documents, question


app = FastAPI()


@app.get("/")
def root():
    return {"message": "Welcome To RAG assistant"}


app.include_router(documents.router)
app.include_router(question.router)

