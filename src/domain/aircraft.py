import uuid
from sqlalchemy import Column, ForeignKey, String, Integer, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID
from src.base import Base

class Aircraft(Base):
    __tablename__ = "aircraft"

    aircraft_id = Column(String, primary_key=True)

    airline_designator = Column(String, ForeignKey("airline.airline_designator"), nullable=False)

    manufacturer = Column(String, nullable=True)
    aircraft_model = Column(String, nullable=True)