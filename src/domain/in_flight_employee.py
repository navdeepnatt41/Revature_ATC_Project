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
    __tablename__ = "in_flight_employee"

    employee_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String)
    last_name = Column(String)
    position = Column(SQLEnum(EmployeePosition))
    employee_status = Column(SQLEnum(InFlightStatus))
    supervisor = Column(UUID, ForeignKey("in_flight_employee.employee_id"))
    employee_location = Column(
        String, ForeignKey("airport.airport_code"), nullable=False
    )
