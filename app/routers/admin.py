from fastapi import APIRouter, Request, Cookie, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import insert

from utils.jwt_auth import is_admin, user_login
from utils.models.challenge import ChallengeInfo
from db.session import get_db
from db.base import Challenge

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)

templates = Jinja2Templates(directory='templates')

@router.get('/', response_class=HTMLResponse)
def admin_main(request: Request, UserToken: Annotated[str | None, Cookie()] = None, db: Session = Depends(get_db)):
    if not is_admin(UserToken, db):
        return '<script>alert("You are not admin!"); location.href="/"</script>'
    
@router.get('/challenge', response_class=HTMLResponse)
def admin_challenge(request: Request, UserToken: Annotated[str | None, Cookie()] = None, db: Session = Depends(get_db)):
    if not is_admin(UserToken, db):
        return '<script>alert("You are not admin!"); location.href="/"</script>'
    
    current_user = user_login(UserToken)
    
    return templates.TemplateResponse(
        'admin_challenge.html',
        {
            'request': request,
            'user_id': current_user
        }
    )

@router.post('/challenge')
def update_challenge(challengeinfo: ChallengeInfo, UserToken: Annotated[str | None, Cookie()] = None, db: Session = Depends(get_db)):
    # 중복 방지를 위한 id 검사
    chall_id = db.query(Challenge).filter(Challenge.id == challengeinfo.problemNumber).first()
    if chall_id is not None:
        print(chall_id)

    print(challengeinfo)
    
    # 문제 업데이트
    if challengeinfo.problemNumber is None:
        stmt = (
            insert(Challenge).values(challName=challengeinfo.problemName, challScore=challengeinfo.problemScore, challExplain=challengeinfo.problemContent, category=challengeinfo.problemCategory)
        )

        try:
            result = db.execute(stmt)
            db.commit()

            if result.rowcount == 0:
                raise HTTPException(status_code=400, detail='Problem Insert Error')
        except Exception as e:
            db.rollback()
            print(e)
            raise HTTPException(
                status_code=500,
                detail='Internal Server Error'
            )