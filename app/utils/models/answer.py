from pydantic import BaseModel

class Answer(BaseModel):
    problem_id: int
    problem_name: str
    user_answer: str