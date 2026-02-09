from datetime import datetime
import uuid
from dataclasses import dataclass
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID

from src.base import Base
from enum import Enum

class EmployeePosition(Enum):
    CAPTAIN = "Captain",
    COPILOT = "Co-pilot"
    MANAGER = "Flight Purser"
    FLIGHT_ATTENDANT = "Flight Attendant"
    
class InFlightEmployee(Base):
    __tablename__ = 'in_flight_employee'
    
    employee_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    IATA_code = Column(String, ForeignKey('airline.IATA_code'), nullable=False)
    f_name = Column(String, nullable=False)
    f_name = Column(String, nullable=False)
    position = Column(SQLEnum(EmployeePosition), nullable=False)
    status = Column(String, nullable=False)
    supervised = Column(UUID(as_uuid=True), ForeignKey('in_flight_employee.employee_id'))

    


