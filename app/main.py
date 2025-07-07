from fastapi import FastAPI, Request, Cookie, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.sql import func
from typing import Annotated
import datetime

from db.session import db_engine, get_db
from db.base import Base, Challenge, UserChallenge, User
from routers import auth
from utils.jwt_auth import get_current_user
from utils.userinfo import get_userinfo

def create_table():
    # Base.metadata.drop_all(bind=db_engine)
    Base.metadata.create_all(bind=db_engine)

def get_application():
    app = FastAPI()
    create_table()
    return app

templates = Jinja2Templates(directory='templates')

app = get_application()

# 로그인/회원가입 경로 추가
app.include_router(auth.router)

# CSS, Javascript 파일 경로 적용
app.mount('/assets', StaticFiles(directory='static'))

@app.get('/', response_class=HTMLResponse)
def root(request: Request, UserToken: Annotated[str | None, Cookie()] = None, db: Session = Depends(get_db)):
    if not UserToken:
        return '<script>alert("Missing UserToken in cookies."); location.href="/auth/login"</script>'
        # raise HTTPException(status_code=401, detail="Missing UserToken in cookies.")

    current_user = get_current_user(UserToken)
    if current_user is None:
        return '<script>alert("Invalid authentication token."); location.href="/auth/login"</script>'
        # raise HTTPException(status_code=401, detail="Invalid authentication token.")

    UserInfo = get_userinfo(current_user, db)

    # 템플릿 렌더링
    return templates.TemplateResponse(
        "main.html",
        {
            "request": request, 
            "user_id": current_user, 
            "user_info": UserInfo,
            "error": ""
        }
    )
