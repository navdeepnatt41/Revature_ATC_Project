from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from src.base import Base

class Operate(Base):
    __tablename__ = 'operates'
    
    airline_designator = Column(String, ForeignKey('airline.airline_designator'), primary_key=True, nullable=False) #composite key
    airport_code = Column(String, ForeignKey('airport.airport_code'), primary_key=True, nullable=False) #composite key