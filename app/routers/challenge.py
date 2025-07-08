from fastapi import APIRouter, Request, Cookie, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Annotated

from utils.jwt_auth import user_login, is_admin
from db.session import get_db

templates = Jinja2Templates(directory='templates')

router = APIRouter(
    prefix='/challenge',
    tags=['challenge']
)

@router.get('/')
def challenge_main(request: Request, UserToken: Annotated[str | None, Cookie()] = None, db: Session = Depends(get_db)):
    current_user = user_login(UserToken)
    admin = is_admin(UserToken, db)

    return templates.TemplateResponse(
        'challenge.html',
        {'request': request, 'user_id': current_user, 'admin': admin}
    )