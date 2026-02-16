"""
Data Transfer Objects (DTOs) for Flight Crew assignments.
"""
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class FlightCrewScheduleRequest(BaseModel):
    """
    Payload for assigning a list of employees to a flight.
    This matches the 'payload' argument in schedule_flight_crew endpoint.
    """
    employee_ids: list[UUID] = Field(..., min_length=1, description="List of employee IDs to assign to the flight")


class FlightCrewBase(BaseModel):
    """
    Base properties for a crew-to-flight assignment.
    """
    flight_id: UUID
    employee_id: UUID


class FlightCrewRead(FlightCrewBase):
    """
    Schema representing a successful crew assignment.
    """

    model_config = ConfigDict(from_attributes=True)