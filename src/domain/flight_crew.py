import uuid
from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from src.base import Base

class FlightCrew(Base):
    __tablename__ = 'flight_crew'

    flight_id = Column(UUID(as_uuid=True), ForeignKey("flight.flight_id"), primary_key=True, nullable=False) #composite key
    employee_id = Column(UUID(as_uuid=True), ForeignKey("in_flight_employee.employee_id"), primary_key=True,  nullable=False) #composite key
