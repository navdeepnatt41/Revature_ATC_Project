from uuid import UUID
from enum import Enum
from pydantic import BaseModel


class EmployeePosition(str, Enum):
    CAPTAIN = "CAPTAIN"
    COPILOT = "COPILOT"
    FLIGHT_MANAGER = "FLIGHT_MANAGER"
    FLIGHT_ATTENDANT = "FLIGHT_ATTENDANT"


class InFlightStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    SCHEDULED = "SCHEDULED"


class InFlightEmployeeCreate(BaseModel):
    first_name: str
    last_name: str
    position: EmployeePosition
    employee_status: InFlightStatus
    supervisor: str | None = None        
    employee_location: str


class InFlightEmployeeRead(BaseModel):
    employee_id: UUID
    first_name: str
    last_name: str
    position: EmployeePosition
    employee_status: InFlightStatus
    supervisor: str | None = None         
    employee_location: str

    model_config = {"from_attributes": True}