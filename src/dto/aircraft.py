from uuid import UUID
from pydantic import BaseModel

class AircraftCreate(BaseModel):
    aircraft_id : UUID
    airline_designator: str
    manufacturer: str
    aircraft_model: str

class AircraftRead(BaseModel):
    aircraft_id : UUID
    airline_designator: str
    manufacturer: str
    aircraft_model: str

    class Config:
        from_attributes = True
        fields = {
            "aircraft_id" : ... ,
            "airline_designator" : ... ,
            "manufacturer" : ... ,
            "aircraft_model" : ...
        }