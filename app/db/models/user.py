from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from ..base_class import Base

class User(Base):
    id = Column(Integer, primary_key=True)
    userid = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    registerDate = Column(DateTime(), server_default=func.now())
    updateDate = Column(DateTime(), server_default=func.now())
    nickname = Column(String(255), unique=True, nullable=False)
    score = Column(Integer, default=0, nullable=False)
    admin = Column(Boolean, nullable=False)