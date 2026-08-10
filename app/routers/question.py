from fastapi import APIRouter, HTTPException, status
from app.schemas import question
from app.services import rag


router = APIRouter(
    prefix="/question",
    tags=["Questions"]
)


@router.post("/chat")
async def chat(payload: question.QuestionRequest):

    answer = await rag.chat(payload.user_question)

    if answer:
        response = {
            "answer": answer["response"],
            "metadata" : {
                "sources": answer["sources"],
                "subjects": answer["subjects"]
            }
        }
        
        return response
    else:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Model Problem"
        )


