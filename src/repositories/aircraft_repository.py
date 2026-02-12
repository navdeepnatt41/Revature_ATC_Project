from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from src.repositories.aircraft_repository_protocol import AircraftRepositoryProtocol
from src.domain.aircraft import Aircraft

class AircraftRepository(AircraftRepositoryProtocol):
    def __init__(self, session: Session):
        self.session = session

    def create(self, aircraft: Aircraft) -> Aircraft:
        self.session.add(aircraft)
        self.session.commit()
        self.session.refresh(aircraft)
        return aircraft
    
    def get(self, aircraft_id: UUID) -> Optional[Aircraft]:
        return (
            self.session.query(Aircraft)
            .filter(Aircraft.aircraft_id == aircraft_id)
            .one_or_none()
        )

    def list_all(self) -> list[Aircraft]:
        return self.session.query(Aircraft).all()
    
    def update(self, aircraft: Aircraft) -> Aircraft:
        cur_aircraft = self.session.get(Aircraft, aircraft.aircraft_id)
        if cur_aircraft is None:
            raise ValueError("Aircraft not found")
        cur_aircraft.aircraft_model = aircraft.aircraft_model
        cur_aircraft.airline_designator = aircraft.airline_designator
        cur_aircraft.manufacturer = aircraft.manufacturer
        self.session.commit()
        self.session.refresh(cur_aircraft)
        return cur_aircraft

    
    def delete(self, aircraft_id: UUID) -> None:
        aircraft = self.session.get(Aircraft, aircraft_id)
        if aircraft is None:
            raise ValueError("Aircraft not found")
        self.session.delete(aircraft)
        self.session.commit()