from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings): # pydantic의 BaseSettings 상속
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    class Config: # .env에 정의된 DB 환경 정보를 가져와 변수에 저장
        env_file = '.env'
    # model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

@lru_cache() # Settings 클래스 데이터를 캐싱하고 최초 인스턴스 생성 이후로는 캐싱된 인스턴스 반환 (캐싱된 데이터만 반환하면 되므로 속도가 빨라짐)
def get_setting():
    return Settings()