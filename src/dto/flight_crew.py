from uuid import UUID
from pydantic import AliasChoices, BaseModel, Field


class FlightCrewCreate(BaseModel):
    flight_id: UUID
    employee_id: UUID


class FlightCrewRead(BaseModel):
    flight_id: UUID
    employee_id: UUID

    model_config = {"from_attributes": True}
    
class FlightCrewScheduleRequest(BaseModel):
    employee_ids: list[UUID] = Field(
        validation_alias=AliasChoices("employee_ids", "employee_id")
    )