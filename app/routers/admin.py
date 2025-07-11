from fastapi import APIRouter, Request, Cookie, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.sql import func
from sqlalchemy.orm import Session
from sqlalchemy import insert, update, delete
from typing import Annotated
from datetime import timedelta

from utils.jwt_auth import is_admin, user_login
from utils.models.challenge import ChallengeInfo
from db.session import get_db
from db.base import Challenge, User, UserChallenge

def get_dashboard_info(db: Session) -> dict:
    # 정보를 담을 딕셔너리
    infos = dict()

    # 전체 사용자 수
    all_user_cnt = db.query(User).count()
    infos['all_user_cnt'] = all_user_cnt

    # 총 문제 수
    all_prob_cnt = db.query(Challenge).count()
    infos['all_prob_cnt'] = all_prob_cnt

    # 해결된 문제 수
    # solve_prob_cnt = db.query(UserChallenge)

    # 활성 사용자 수
    # accessDate로부터 2일 내에 있는 사용자를 활성 사용자로 계산
    active_users = db.query(User).filter(User.accessDate >= (func.now() - timedelta(days=2))).count()
    infos['active_users'] = active_users

    return infos

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
    
    dash_info = get_dashboard_info(db)

    return templates.TemplateResponse(
        'admin.html',
        {
            'request': request,
            'admin': admin,
            'user_id': current_user,
            'dash_info': dash_info
        }
    )
    
@router.get('/challenge', response_class=HTMLResponse)
def admin_challenge(request: Request, UserToken: Annotated[str | None, Cookie()] = None, db: Session = Depends(get_db)):
    admin = is_admin(UserToken, db)
    current_user = user_login(UserToken)
    if not admin:
        return '<script>alert("You are not admin!"); location.href="/"</script>'
    
    current_user = user_login(UserToken)

    # 문제 목록 출력을 위한 문제 목록 조회
    challs = db.query(Challenge)
    for row in challs:
        if row.dockerImageNames is not None:
            row.dockerImageNames = row.dockerImageNames.split(',')
        print(row.dockerImageNames)
    
    return templates.TemplateResponse(
        'admin_challenge.html',
        {
            'request': request,
            'admin': admin,
            'user_id': current_user,
            'challenges': challs
        }
    )

@router.post('/challenge')
def update_challenge(challengeinfo: ChallengeInfo, UserToken: Annotated[str | None, Cookie()] = None, db: Session = Depends(get_db)):
    admin = is_admin(UserToken, db)
    if not admin:
        raise HTTPException(
            status_code=401,
            detail='Unauthorized'
        )
    # print(challengeinfo)
    docker_images = ','.join(challengeinfo.dockerImageNames) if len(challengeinfo.dockerImageNames) != 0 else None
    # 문제 업데이트
    if challengeinfo.problemNumber is None:
        stmt = (
            insert(Challenge).values(
                challName=challengeinfo.problemName, 
                challScore=challengeinfo.problemScore, 
                challExplain=challengeinfo.problemContent, 
                category=challengeinfo.problemCategory, 
                challAnswer=challengeinfo.problemAnswer, 
                hasDockerInstance=challengeinfo.hasDockerInstance,
                dockerImageNames=docker_images
            )
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
            .values(
                challName=challengeinfo.problemName, 
                challScore=challengeinfo.problemScore, 
                challExplain=challengeinfo.problemContent, 
                category=challengeinfo.problemCategory, 
                challAnswer=challengeinfo.problemAnswer, 
                hasDockerInstance=challengeinfo.hasDockerInstance
            )
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