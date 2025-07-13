from fastapi import APIRouter, Request, Cookie, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.sql import func
from sqlalchemy.orm import Session
from sqlalchemy import insert, update, delete, literal_column, union_all, desc, select
from typing import Annotated
from datetime import timedelta
from hashlib import sha256

from utils.jwt_auth import is_admin, user_login
from utils.models.challenge import ChallengeInfo
from utils.models.useredit import UserEdit
from utils.models.usercreate import UserCreate
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
    solve_prob_cnt = db.query(UserChallenge).count()
    infos['solve_prob_cnt'] = solve_prob_cnt

    # 활성 사용자 수
    # accessDate로부터 2일 내에 있는 사용자를 활성 사용자로 계산
    active_users = db.query(User).filter(User.accessDate >= (func.now() - timedelta(days=2))).count()
    infos['active_users'] = active_users

    # 1. 각 이벤트 유형에 대한 쿼리 생성
    # 각 쿼리는 동일한 수의 컬럼과 호환되는 데이터 타입을 가져야 합니다.
    # 컬럼 이름을 'event_time', 'user_id', 'event_type', 'event_detail'로 통일합니다.

    # 챌린지 해결 이벤트 쿼리
    challenge_events_query = db.query(
        UserChallenge.solveTime.label('event_time'), # 해결 시간을 이벤트 시간으로
        UserChallenge.userid.label('user_id'), # 사용자 ID
        literal_column("'문제 해결'").label('event_type'), # 이벤트 타입 고정 문자열
        UserChallenge.challName.label('event_detail') # 문제 이름을 상세 정보로
    )

    # 회원가입 이벤트 쿼리
    registration_events_query = db.query(
        User.registerDate.label('event_time'), # 가입 시간을 이벤트 시간으로
        User.userid.label('user_id'), # 사용자 ID
        literal_column("'회원가입'").label('event_type'), # 이벤트 타입 고정 문자열
        User.nickname.label('event_detail') # 닉네임을 상세 정보로
    )

    # 2. 두 쿼리를 UNION ALL로 결합하고 서브쿼리로 만듭니다.
    # union_all은 두 SELECT 문의 결과 구조(컬럼 수, 타입)가 동일해야 합니다.
    combined_events_subquery = union_all(challenge_events_query, registration_events_query).subquery()

    # 3. 서브쿼리에서 최신 5개 이벤트를 조회합니다.
    # 'event_time' 컬럼을 기준으로 내림차순 정렬 후 5개만 가져옵니다.
    # literal_column을 사용하여 서브쿼리의 컬럼 이름을 참조합니다.
    final_query = db.query(combined_events_subquery).order_by(
        desc(literal_column("event_time"))
    ).limit(5)

    recent_events = final_query.all()
    infos['recent_events'] = recent_events

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
def delete_challenge(problemId: int, UserToken: Annotated[str | None, Cookie()] = None, db: Session = Depends(get_db)):
    admin = is_admin(UserToken, db)
    if not admin:
        return 'You are not admin'
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
    
@router.get('/users', response_class=HTMLResponse)
def users_info(request: Request, UserToken: Annotated[str | None, Cookie()] = None, db: Session = Depends(get_db)):
    admin = is_admin(UserToken, db)
    current_user = user_login(UserToken)
    if not admin:
        raise HTTPException(
            status_code=401,
            detail='Unauthorized'
        )
    
    users = db.query(User)

    # 점수 계산
    for row in users:
        subquery = select(UserChallenge.challName).where(UserChallenge.userid == row.userid)
        score = db.query(func.sum(Challenge.challScore)).filter(Challenge.challName.in_(subquery)).scalar()
        if score is None: score = 0 # 점수가 존재하지 않으면 0으로 초기화

        row.score = score
    
    return templates.TemplateResponse(
        'admin_users.html',
        {
            'request': request,
            'admin': admin,
            'user_id': current_user,
            'users': users
        }
    )

@router.post('/users/edit')
def edit_user(userinfo: UserEdit, UserToken: Annotated[str | None, Cookie()] = None, db: Session = Depends(get_db)):
    admin = is_admin(UserToken, db)
    if not admin:
        return {'error': True, 'message': 'You are not admin'}

    try:
        if userinfo.password is None or userinfo.password == '' or userinfo.password == None:
            if userinfo.admin is None or userinfo.admin == None:
                stmt = (
                    update(User)
                    .where(User.id == userinfo.Id)
                    .values(
                        userid = userinfo.userid,
                        nickname = userinfo.nickname,
                        updateDate = func.now()
                    )
                )
            else:
                stmt = (
                    update(User)
                    .where(User.id == userinfo.Id)
                    .values(
                        userid = userinfo.userid,
                        nickname = userinfo.nickname,
                        admin = userinfo.admin,
                        updateDate = func.now()
                    )
                )
        else:
            if userinfo.admin is None or userinfo.admin == None:
                stmt = (
                    update(User)
                    .where(User.id == userinfo.Id)
                    .values(
                        userid = userinfo.userid,
                        nickname = userinfo.nickname,
                        password = sha256(userinfo.password.encode()).hexdigest(),
                        updateDate = func.now()
                    )
                )
            else:
                stmt = (
                    update(User)
                    .where(User.id == userinfo.Id)
                    .values(
                        userid = userinfo.userid,
                        nickname = userinfo.nickname,
                        password = sha256(userinfo.password.encode()).hexdigest(),
                        admin = userinfo.admin,
                        updateDate = func.now()
                    )
                )

        db.execute(stmt)
        db.commit()

        return {'error': False}
    except Exception as e:
        db.rollback()
        print(e)
        raise HTTPException(
            status_code=500,
            detail='Internal Server Error'
        )
    
@router.post('/users/create')
def create_user(userinfo: UserCreate, UserToken: Annotated[str | None, Cookie()] = None, db: Session = Depends(get_db)):
    admin = is_admin(UserToken, db)
    if not admin:
        return {'error': True, 'message': 'You are not admin'}

    # 사용자 존재 여부 검사
    is_user = db.query(User).filter(User.userid == userinfo.userid).first()

    if is_user:
        return {'error': True, 'message': 'Already Exist User'}
    
    # 사용자 생성
    try:
        stmt = (
            insert(User)
            .values(
                userid = userinfo.userid,
                password = sha256(userinfo.password.encode()).hexdigest(),
                nickname = userinfo.nickname,
                admin = userinfo.admin,
                registerDate = func.now(),
                updateDate = func.now(),
                accessDate = func.now(),
                score = 0
            )
        )

        db.execute(stmt)
        db.commit()

        return {'error': False}
    except Exception as e:
        db.rollback()
        print(e)
        raise HTTPException(
            status_code=500,
            detail='Internal Server Error'
        )

@router.get('/users/delete/{userId}')
def delete_user(userId: int, UserToken: Annotated[str | None, Cookie()] = None, db: Session = Depends(get_db)):
    admin = is_admin(UserToken, db)
    if not admin:
        return 'You are not admin'
    
    print(userId)
    try:
        stmt = (
            delete(User).filter(User.id == userId)
        )
        db.execute(stmt)
        db.commit()
    except Exception as e:
        db.rollback()
        print(e)
        raise HTTPException(
            status_code=500,
            detail='Internal Server Error'
        )