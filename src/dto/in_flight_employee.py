"""
Data Transfer Objects (DTOs) for In-Flight Employee management.
"""
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EmployeePosition(str, Enum):
    """
    Operational roles assigned to flight crew members.
    """
    CAPTAIN = "CAPTAIN"
    COPILOT = "COPILOT"
    FLIGHT_MANAGER = "FLIGHT_MANAGER"
    FLIGHT_ATTENDANT = "FLIGHT_ATTENDANT"


class InFlightStatus(str, Enum):
    """
    Availability status for flight crew personnel.
    """
    AVAILABLE = "AVAILABLE"
    SCHEDULED = "SCHEDULED"


class InFlightEmployeeCreate(BaseModel):
    """
    Data schema for registering a new employee into the system.
    """
    first_name: str = Field(..., description="Employee's legal first name")
    last_name: str = Field(..., description="Employee's legal last name")
    position: EmployeePosition = Field(..., description="The crew role the employee is qualified for")
    employee_status: InFlightStatus = Field(..., description="Current operational status")
    supervisor: str | None = Field(None, description="Optional identifier for the reporting manager")
    employee_location: str = Field(..., description="IATA code for the current airport base")


class InFlightEmployeeRead(BaseModel):
    """
    Data schema for returning employee details in API responses.
    """
    employee_id: UUID = Field(..., description="Unique internal identifier")
    first_name: str = Field(..., description="Employee's legal first name")
    last_name: str = Field(..., description="Employee's legal last name")
    position: EmployeePosition = Field(..., description="The crew role the employee is qualified for")
    employee_status: InFlightStatus = Field(..., description="Current operational status")
    supervisor: str | None = Field(None, description="Optional identifier for the reporting manager")
    employee_location: str = Field(..., description="IATA code for the current airport base")

    model_config = ConfigDict(from_attributes=True)