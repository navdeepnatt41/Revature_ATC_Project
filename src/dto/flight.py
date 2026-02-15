from uuid import UUID
from datetime import datetime
from enum import Enum
from pydantic import BaseModel

class FlightStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    IN_FLIGHT = "IN-FLIGHT"
    ARRIVED = "ARRIVED"
    DELAYED = "DELAYED"
    CANCELLED = "CANCELLED"

class FlightCreate(BaseModel):
    route_id: UUID
    flight_status: FlightStatus = FlightStatus.SCHEDULED
    aircraft_id: UUID
    arrival_time: datetime | None = None
    departure_time: datetime | None = None

class FlightRead(BaseModel):
    flight_id: UUID
    route_id: UUID
    flight_status: FlightStatus
    aircraft_id: UUID
    arrival_time: datetime | None = None
    departure_time: datetime | None = None

    class Config:
        from_attributes = True
        fields = {
            "flight_id": ...,
            "route_id": ...,
            "flight_status": ...,
            "aircraft_id": ...,
            "arrival_time": ...,
            "departure_time": ...,
        }