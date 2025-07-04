from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.orm import Session
from hashlib import sha256

from db.models.user import User
from db.session import get_db

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

@router.get('/login')
def login():
    return 'login page'

@router.post('/login')
def login_db(userid: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.userid == userid and User.password == sha256(password.encode()).hexdigest()).first()
    if user is not None:
        return user
    raise HTTPException(status_code=400, detail='User Not Exist')

@router.get('/register')
def register():
    return 'register page'

@router.post('/register')
def register_db(userid: str, password: str, nickname: str, db: Session = Depends(get_db)):
    stmt = (
        insert(User).values(userid=userid, password=sha256(password.encode()).hexdigest(), nickname=nickname)
    )
    result = db.execute(stmt)
    db.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=400, detail='User already exist')
    
    return {'message': 'user create successfully'}