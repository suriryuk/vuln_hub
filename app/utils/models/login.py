from pydantic import BaseModel, Field

class LoginInfo(BaseModel):
    userid: str
    password: str
    