from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from src.base import Base

class Operate(Base):
    __tablename__ = 'operate'
    
    IATA_code = Column(String, ForeignKey('airline.IATA_code'), nullable=False)
    airport_code = Column(UUID(as_uuid=True), ForeignKey('airport.airport_code'), nullable=False)