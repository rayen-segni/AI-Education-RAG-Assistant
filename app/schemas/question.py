from pydantic import BaseModel


class QuestionBase(BaseModel):
    pass


class QuestionRequest(QuestionBase):
    user_question: str

class QuestionResponse(QuestionBase):
    answer: str
    metadata: dict

