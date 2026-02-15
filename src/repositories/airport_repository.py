from typing import Optional
from sqlalchemy.orm import Session
from src.domain.airport import Airport
from src.repositories.airport_repository_protocol import AirportRepositoryProtocol


class AirportRepository(AirportRepositoryProtocol):
    def __init__(self, session: Session):
        self.session = session

    def create(self, airport: Airport) -> Airport:
        self.session.add(airport)
        self.session.commit()
        self.session.refresh(airport)
        return airport

    def get(self, airport_code: str) -> Optional[Airport]:  # returning one employee
        return (
            self.session.query(Airport)
            .filter(Airport.airport_code == airport_code)
            .one_or_none()  # returning None if none is found
        )

    def list_all(self) -> list[Airport]:
        return self.session.query(Airport).all()

    def update(self, airport: Airport) -> Airport:
        existing = self.session.get(Airport, airport.airport_code)
        if existing is None:
            raise ValueError("Airport not found")
        # dont need to update primary key(airport_code)
        existing.airport_name = airport.airport_name
        existing.airport_country = airport.airport_country
        existing.airport_city = airport.airport_city
        existing.airport_address = airport.airport_address

        self.session.commit()
        self.session.refresh(existing)
        return existing

    def delete(self, airport_code: str) -> None:
        airport = self.session.get(Airport, airport_code)
        if airport is None:
            raise ValueError("Airport not found")
        self.session.delete(airport)
        self.session.commit()
