from pydantic import BaseModel


class QuestionBase(BaseModel):
    pass


class QuestionRequest(QuestionBase):
    user_question: str
    conversation_id: str | None = None

class QuestionResponse(QuestionBase):
    conversation_id: str
    answer: str
    metadata: dict



