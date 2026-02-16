"""
Defines the SQLAlchemy ORM for the InFlightEmployee table that represents employees.
"""

import uuid
from enum import Enum
from dataclasses import dataclass

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from src.base import Base


class EmployeePosition(Enum):
    """
    An Enum that defines the different roles each employee has

    Attributes:
        CAPTAIN (str): The leading pilot for the flight
        COPILOT (str): The co-pilot assisting the captain
        FLIGHT_MANAGER (str): The onboard flight manager
        FLIGHT_ATTENDANT (str): The flight attendant
    """
    CAPTAIN = "CAPTAIN"
    COPILOT = "COPILOT"
    FLIGHT_MANAGER = "FLIGHT_MANAGER"
    FLIGHT_ATTENDANT = "FLIGHT_ATTENDANT"


class InFlightStatus(Enum):
    """
    An Enum that provides statuses as to whether an employee can be assigned
    to a flight or is already busy.

    Attributes:
        AVAILABLE (str): The employee can be scheduled for a flight
        SCHEDULED (str): The employee is already scheduled and can not be re-scheduled
    """
    AVAILABLE = "AVAILABLE"
    SCHEDULED = "SCHEDULED"


@dataclass
class InFlightEmployee(Base):
    """
    The SQLAlchemy ORM object that represents the InFlightEmployee Table

    Attributes:
        empolyee_id (UUID): The unique id for an employee
        first_name (str): Employee first name
        last_name (str): Employee last name
        postion (EmployeePosition): Which position (or job) an employee holds
        supervisor (UUID): The employee's supervisor (in case of already being one,
                            this column is simply the employee's)
        employee_locaiton (str): The IATA code for the airport the employee currently is at
    """
    __tablename__ = "in_flight_employee"

    employee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
    position: Mapped[EmployeePosition] = mapped_column(SQLEnum(EmployeePosition))
    employee_status: Mapped[InFlightStatus] = mapped_column(SQLEnum(InFlightStatus))
    supervisor: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("in_flight_employee.employee_id"))
    employee_location: Mapped[str] = mapped_column(
        String, ForeignKey("airport.airport_code"), nullable=False
    )
