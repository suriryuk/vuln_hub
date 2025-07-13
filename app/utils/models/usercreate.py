from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    userid: str
    password: str
    nickname: str
    admin: Optional[bool] = False