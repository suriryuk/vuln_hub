from fastapi import APIRouter, Request, Cookie, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import insert, update, delete

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
    admin = is_admin(UserToken, db)
    current_user = user_login(UserToken)
    if not admin:
        return '<script>alert("You are not admin!"); location.href="/"</script>'

    return templates.TemplateResponse(
        'admin.html',
        {
            'request': request,
            'admin': admin,
            'user_id': current_user,
        }
    )
    
@router.get('/challenge', response_class=HTMLResponse)
def admin_challenge(request: Request, UserToken: Annotated[str | None, Cookie()] = None, db: Session = Depends(get_db)):
    if not is_admin(UserToken, db):
        return '<script>alert("You are not admin!"); location.href="/"</script>'
    
    current_user = user_login(UserToken)

    # 문제 목록 출력을 위한 문제 목록 조회
    challs = db.query(Challenge)
    
    return templates.TemplateResponse(
        'admin_challenge.html',
        {
            'request': request,
            'user_id': current_user,
            'challenges': challs
        }
    )

@router.post('/challenge')
def update_challenge(challengeinfo: ChallengeInfo, UserToken: Annotated[str | None, Cookie()] = None, db: Session = Depends(get_db)):
    # 문제 업데이트
    if challengeinfo.problemNumber is None:
        stmt = (
            insert(Challenge).values(challName=challengeinfo.problemName, challScore=challengeinfo.problemScore, challExplain=challengeinfo.problemContent, category=challengeinfo.problemCategory, challAnswer=challengeinfo.problemAnswer)
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
    else:
        stmt = (
            update(Challenge)
            .where(Challenge.id == challengeinfo.problemNumber)
            .values(challName=challengeinfo.problemName, challScore=challengeinfo.problemScore, challExplain=challengeinfo.problemContent, category=challengeinfo.problemCategory, challAnswer=challengeinfo.problemAnswer)
        )

        try:
            db.execute(stmt)
            db.commit()
        except Exception as e:
            db.rollback()
            print(e)
            raise HTTPException(
                status_code=500,
                detail='Internal Server Error'
            )

@router.get('/challenge/delete/{problemId}')
def delete_challenge(problemId: int, db: Session = Depends(get_db)):
    # 삭제 쿼리
    stmt = (
        delete(Challenge).where(Challenge.id == problemId)
    )

    try:
        db.execute(stmt)
        db.commit()
    except Exception as e:
        db.rollback()
        print(e)
        raise HTTPException(
            status_code=500,
            detail='Internal Server Error'
        )