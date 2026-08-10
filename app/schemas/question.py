from pydantic import BaseModel


class QuestionBase(BaseModel):
    user_question: str


class QuestionRequest(QuestionBase):
    pass

class QuestionResponse(QuestionBase):
    sources: list[dict]

