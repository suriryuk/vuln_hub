from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from ..base_class import Base

class UserChallenge(Base):
    id = Column(Integer, primary_key=True)
    challName = Column(String(255), ForeignKey('challenge.challName'), nullable=False)
    challId = Column(Integer, ForeignKey('challenge.id'), nullable=False)
    userid = Column(String(255), nullable=False)
    solveTime = Column(DateTime(), server_default=func.now())