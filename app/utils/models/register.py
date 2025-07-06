from pydantic import BaseModel

class RegisterInfo(BaseModel):
    userid: str
    password: str
    nickname: str
    confirmPassword: str
    