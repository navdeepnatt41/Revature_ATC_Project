from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from src.domain.aircraft import Aircraft

class MockAircraftRepository:
    def create(self, aircraft: Aircraft) -> Aircraft:
        return aircraft
    
    def get(self, aircraft_id: UUID) -> Optional[Aircraft]:
        return Aircraft(aircraft_id, "test", "test", 0, 100, 'IN_FLIGHT', 'JFK')

    def list_all(self) -> list[Aircraft]:
        return [Aircraft(manufacturer = "test", aircraft_model = "test", current_distance = 0, maintenance_interval = 100, aircraft_status = 'IN_FLIGHT', aircraft_location ='JFK'),
                Aircraft(Aircraft(manufacturer = "test2", aircraft_model = "test2", current_distance = 100, maintenance_interval = 100, aircraft_status = 'IN_FLIGHT', aircraft_location ='JFK'))]
    
    def update(self, aircraft: Aircraft) -> Aircraft:
        return aircraft

    
    def delete(self, aircraft_id: UUID) -> None:
        pass