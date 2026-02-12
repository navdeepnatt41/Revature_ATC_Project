from typing import Optional
from sqlalchemy.orm import Session
from src.repositories.airline_repository_protocol import AirlineRepositoryProtocol
from src.domain.airline import Airline

class AirlineRepository(AirlineRepositoryProtocol):
    def __init__(self, session: Session ) -> None:
        self.session = session

    def create(self, airline: Airline) -> Airline:
        self.session.add(airline)
        self.session.commit()
        self.session.refresh(airline)
        return airline
    
    def get(self, airline_designator: str) -> Optional[Airline]:
        return (
            self.session.query(Airline)
            .filter(Airline.airline_designator == airline_designator)
            .one_or_none()
        )

    def list_all(self) -> list[Airline]:
        return self.session.query(Airline).all() 

    def update(self, airline: Airline) -> Airline:
        existing = self.session.get(Airline, airline.airline_designator)
        if existing is None:
            raise ValueError("Airline not found")

        existing.name = airline.name
        
        self.session.commit()
        self.session.refresh(existing)
        return existing

    def delete(self, airline_designator: str) -> None:
        airline = self.session.get(Airline, airline_designator)
        if airline is None:
            raise ValueError("no airline found")
        self.session.delete(airline)
        self.session.commit()