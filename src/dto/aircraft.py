from uuid import UUID
from pydantic import BaseModel
from enum import Enum

class AircraftStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    DEPLOYED = "DEPLOYED"
    AOG = "MAINTENANCE"

class AircraftCreate(BaseModel):
    manufacturer: str
    aircraft_model: str
    current_distance: float
    maintenance_interval: float
    aircraft_status: AircraftStatus
    aircraft_location: str


class AircraftRead(BaseModel):
    aircraft_id: UUID
    manufacturer: str
    aircraft_model: str
    current_distance: float
    maintenance_interval: float
    aircraft_status: AircraftStatus
    aircraft_location: str

    class Config:
        from_attributes = True
        fields = {
            "fields": ...,
            "manufacturer": ...,
            "aircraft_model": ...,
            "current_distance": ...,
            "maintenance_interval": ...,
            "aircraft_status": ...,
            "aircraft_location": ...,
        }
