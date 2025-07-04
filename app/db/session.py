from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import get_setting

settings = get_setting()

SQLALCHEMY_DATABASE_URL = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(
    settings.DB_USER,
    settings.DB_PASSWORD,
    settings.DB_HOST,
    settings.DB_PORT,
    settings.DB_NAME,
)

db_engine = create_engine(SQLALCHEMY_DATABASE_URL) # SQLAlchemy 엔진 객체 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine) # 동일한 구성을 가진 세션을 생성하는 factory

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()