from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os

SECRET_KEY = os.getenv('JWT_SECRET_KEY')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# JWT 토큰 생성
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    # 유저 정보
    user = data.copy()

    # 만료 시간
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    user.update({'exp': int(expire.timestamp())}) # 만료 시간을 토큰에 추가

    # JWT 인코딩
    enc_jwt = jwt.encode(user, SECRET_KEY, algorithm=ALGORITHM)
    return enc_jwt

# JWT 인증
def get_current_user(token: str):
    try:
        userid = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]).get('sub')
        if userid is None:
            return None
    except JWTError as e:
        print(f"JWT Decode error: {e}")
        return None

    return userid