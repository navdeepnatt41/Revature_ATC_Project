from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

class FlightCreate(BaseModel):
    flight_id: UUID # TODO: don't need UUID for Create(?)
    route_id: UUID
    flight_status: str
    aircraft_id: UUID
    arrival_time: datetime
    dept_time: datetime

class FlightRead(BaseModel):
    flight_id: UUID
    route_id: UUID
    flight_status: str
    aircraft_id: UUID
    arrival_time: datetime
    dept_time: datetime

    class Config:
        from_attributes = True
        fields = {
            "flight_id": ...,
            "route_id": ...,
            "flight_status": ...,
            "aircraft_id": ...,
            "arrival_tie": ...,
            "dept_time": ...,
        }