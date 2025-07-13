from pydantic import BaseModel
from typing import Optional

class UserEdit(BaseModel):
    Id: int
    userid: str
    password: Optional[str] = None
    nickname: str
    admin: Optional[bool] = None