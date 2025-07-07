from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from ..base_class import Base

class Challenge(Base):
    id = Column(Integer, primary_key=True)
    challName = Column(String(255), nullable=False, unique=True)
    challScore = Column(Integer, nullable=False)
    category = Column(String(255), nullable=False)