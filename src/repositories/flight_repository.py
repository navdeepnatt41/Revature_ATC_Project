from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.domain.flight import Flight
from src.repositories.flight_repository_protocol import FlightRepositoryProtocol
from src.domain.route import Route
from src.domain.airport import Airport


class FlightRepository(FlightRepositoryProtocol):
    def __init__(self, session: Session):
        self.session = session

    def create(self, flight: Flight) -> Flight:
        self.session.add(flight)
        self.session.commit()
        self.session.refresh(flight)
        return flight

    def get(self, flight_id: UUID) -> Optional[Flight]:
        return (
            self.session.query(Flight)
            .filter(Flight.flight_id == flight_id)
            .one_or_none()  # returning None if none is found
        )

    def list_all(self) -> list[Flight]:
        return self.session.query(Flight).all()

    def update(self, flight: Flight) -> Flight:
        existing = self.session.get(Flight, flight.flight_id)
        if existing is None:
            raise ValueError("Flight not found")

        # existing.flight_id = flight.flight_id
        existing.route_id = flight.route_id
        existing.aircraft_id = flight.aircraft_id
        existing.flight_status = flight.flight_status
        existing.arrival_time = flight.arrival_time
        existing.dept_time = flight.dept_time

        self.session.commit()
        self.session.refresh(existing)
        return existing

    def delete(self, flight_id: UUID) -> None:
        flight = self.session.get(Flight, flight_id)
        if flight is None:
            raise ValueError("Flight not found")
        self.session.delete(flight)
        self.session.commit()

    def get_scheduled_by_city(self, origin_city: str) -> list[Flight]:
        print(origin_city)
        flights = (
        self.session.execute(
            select(Flight)
            .join(Route, Flight.route_id == Route.route_id)
            .join(Airport, Route.origin_airport_code == Airport.airport_code)
            .where(
                Flight.flight_status == "SCHEDULED",
                Airport.airport_city == origin_city,
            )
        )
        .scalars()
        .all()
        )
        print(flights[0].flight_id)
        return flights