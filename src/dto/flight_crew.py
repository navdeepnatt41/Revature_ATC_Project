from uuid import UUID
from pydantic import BaseModel


class FlightCrewCreate(BaseModel):
    flight_id: UUID
    employee_id: UUID


class FlightCrewRead(BaseModel):
    flight_id: UUID
    employee_id: UUID

    model_config = {"from_attributes": True}
    
class FlightCrewScheduleRequest(BaseModel):
    employee_id: list[UUID]