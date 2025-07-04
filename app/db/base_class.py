from typing import Any
from sqlalchemy.ext.declarative import as_declarative, declared_attr

@as_declarative()
class Base:
    id: Any
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str: # 해당 Base 클래스를 상속받는 모든 클래스의 이름을 소문자로 바꾸고 이를 테이블 이름과 매핑 ( ex. class User(Base) -> 'user'라는 이름의 테이블 생성 )
        return cls.__name__.lower()