from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.orm import Session
from hashlib import sha256

from db.models.user import User
from db.session import get_db
from utils.models.login import LoginInfo
from utils.models.register import RegisterInfo
from utils.jwt_auth import create_access_token

templates = Jinja2Templates(directory='templates')

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

@router.get('/login', response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {'request': request, 'error': ''}
    )

@router.post('/login')
def login_db(userinfo: LoginInfo, response: Response, db: Session = Depends(get_db)):
    # user 조회 쿼리
    user = db.query(User).filter(User.userid == userinfo.userid and User.password == sha256(userinfo.password.encode()).hexdigest()).first()

    if user is not None:
        # JWT 토큰 생성
        token = create_access_token({'sub': userinfo.userid})

        # 쿠키 설정
        response.set_cookie(
            key='UserToken',
            value=token,
            httponly=True,
            secure=True,
            samesite='lax',
            path='/'
        )

        return {'message': 'login success <a href="/">메인으로 가기</a>'}
    
    raise HTTPException(status_code=400, detail='User Not Exist')

@router.get('/register', response_class=HTMLResponse)
def register(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {'request': request, 'error': ''}
    )

@router.post('/register')
def register_db(userinfo: RegisterInfo, db: Session = Depends(get_db)):
    # 비밀번호와 확인용 비밀번호 일치 여부 검사
    if userinfo.password != userinfo.confirmPassword:
        raise HTTPException(status_code=400, detail='The password and confirmation password do not match.')
    
    # user 조회 쿼리 ( 중복 사용자 생성 방지 )
    user = db.query(User).filter(User.userid == userinfo.userid and User.password == sha256(userinfo.password.encode()).hexdigest()).first()
    if user:
        raise HTTPException(status_code=400, detail='User already exist')
    
    stmt = (
        insert(User).values(userid=userinfo.userid, password=sha256(userinfo.password.encode()).hexdigest(), nickname=userinfo.nickname, score=0)
    )

    try:
        result = db.execute(stmt)
        db.commit()

        if result.rowcount == 0:
            raise HTTPException(status_code=400, detail='User already exist')
    except Exception as e:
        db.rollback()
        print(e)
        raise HTTPException(
            status_code=500,
            detail='Internal Server Error'
        )
    
    return {'message': 'user create successfully'}

@router.get('/logout', response_class=HTMLResponse)
def logout(response: Response):
    response.delete_cookie(
        key='UserToken'
    )

    return '<script>alert("logout success"); location.href="/auth/login"</script>'