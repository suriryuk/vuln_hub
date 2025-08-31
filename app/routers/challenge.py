from fastapi import APIRouter, Request, Cookie, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import insert, and_
from typing import Annotated
import docker

from utils.jwt_auth import user_login, is_admin
from utils.models.answer import Answer
from db.session import get_db
from db.base import Challenge, UserChallenge

templates = Jinja2Templates(directory='templates')

router = APIRouter(
    prefix='/challenge',
    tags=['challenge']
)

@router.get('/')
def challenge_main(request: Request, UserToken: Annotated[str | None, Cookie()] = None, db: Session = Depends(get_db)):
    current_user = user_login(UserToken, db)
    admin = is_admin(UserToken, db)

    # 문제 목록 조회
    challs = db.query(Challenge)

    # 현재 유저가 맞춘 문제 목록 조회
    solved_challs = []
    if current_user:
        solved_challs = [row.challName for row in db.query(UserChallenge).filter(UserChallenge.userid == current_user).all()]

    print(solved_challs)

    return templates.TemplateResponse(
        'challenge.html',
        {
            'request': request,
            'user_id': current_user,
            'admin': admin,
            'challenges': challs,
            'solved_challs': solved_challs
        }
    )

@router.get('/instance/{problemId}')
def create_instance(problemId: int, db: Session = Depends(get_db)):
    client = docker.from_env()
    for conid in client.containers.list():
        print(conid.attrs['NetworkSettings']['Networks']['vuln_hub_vuln_hub_internal']['DNSNames'])
        print('=====================')

@router.post('/answer')
def answer_flag(answer: Answer, UserToken: Annotated[str | None, Cookie()] = None, db: Session = Depends(get_db)):
    # 현재 유저
    current_user = user_login(UserToken, db)
    
    # 이미 정답을 맞춘 문제인지 검사
    already_solve = db.query(UserChallenge).filter(
        and_(
            UserChallenge.userid == current_user,
            UserChallenge.challName == answer.problem_name,
            UserChallenge.challId == answer.problem_id
        )
    ).first()

    if already_solve:
        return {'correct': False, 'message': 'Already solve'}

    # 정답 여부 검사
    correct = db.query(Challenge).filter(
        and_(
            Challenge.id==answer.problem_id,
            Challenge.challName == answer.problem_name,
            Challenge.challAnswer == answer.user_answer
        )
    ).first()
    
    if correct:
        stmt = (
            insert(UserChallenge)
            .values(challName=answer.problem_name, userid=current_user, challId=answer.problem_id)
        )

        try:
            db.execute(stmt)
            db.commit()

            return {'correct': True}
        except Exception as e:
            db.rollback()
            print(e)
            return {'correct': False}
    else:
        return {'correct': False}