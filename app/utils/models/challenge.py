from pydantic import BaseModel
from typing import Optional

class ChallengeInfo(BaseModel):
    problemNumber: Optional[int] = None
    problemName: str
    problemContent: str
    problemScore: int
    problemCategory: str
    problemAnswer: str