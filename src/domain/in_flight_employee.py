import uuid
from sqlalchemy import Column, String, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID

from src.base import Base
from enum import Enum

class EmployeePosition(Enum):
    CAPTAIN = "CAPTAIN"
    COPILOT = "COPILOT"
    FLIGHT_MANAGER = "FLIGHT_MANAGER"
    FLIGHT_ATTENDANT = "FLIGHT_ATTENDANT"

class InFlightStatus(Enum):
    AVAILABLE = "AVAILABLE"
    SCHEDULED = "SCHEDULED"
    
class InFlightEmployee(Base):
    __tablename__ = 'in_flight_employee'
    
    employee_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    #airline_designator = Column(String, ForeignKey('airline.airline_designator'), nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    position = Column(SQLEnum(EmployeePosition), nullable=False)
    status = Column(SQLEnum(InFlightStatus), nullable=False)
    superviser = Column(UUID(as_uuid=True), ForeignKey('in_flight_employee.employee_id'))

    


