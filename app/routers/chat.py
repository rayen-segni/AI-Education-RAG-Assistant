from fastapi import APIRouter, HTTPException, status
from app.schemas import chat_sch
from app.services import rag_service


router = APIRouter(
    prefix="/chat",
    tags=["Questions"]
)


@router.post("/")
async def chat(payload: chat_sch.QuestionRequest):

    result = await rag_service.chat(payload.user_question, payload.conversation_id)

    if result:
        return {
            "conversation_id": result["conversation_id"],
            "result": result["response"],
            "metadata" : {
                "sources": result["sources"],
                "subjects": result["subjects"]
            }
        }
        
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Model Problem"
        )


