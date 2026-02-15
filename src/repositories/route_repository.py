from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.domain.flight import Flight, FlightStatus
from src.domain.flight_crew import FlightCrew
from src.repositories.route_repository_protocol import RouteRepositoryProtocol
from src.domain.route import Route


class RouteRepository(RouteRepositoryProtocol):
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, origin_airport_code: str, destination_airport_code: str) -> Route:
        route = Route(origin_airport_code=origin_airport_code, destination_airport_code=destination_airport_code)
        self.session.add(route)
        self.session.commit()
        self.session.refresh(route)
        return route

    def get_by_id(self, route_id: UUID) -> Optional[Route]:
        return self.session.get(Route, route_id)

    def get_by_airport_codes(self, origin_airport_code: str, destination_airport_code: str) -> Optional[Route]:
        return (
            self.session.query(Route)
            .filter(Route.origin_airport_code == origin_airport_code, Route.destination_airport_code == destination_airport_code)
            .one_or_none()
        )

    def list_all(self) -> list[Route]:
        return self.session.query(Route).all()

    def update(self, route: Route) -> Route:
        existing = self.session.get(Route, route.route_id)
        if existing is None:
            raise ValueError("Route not found")

        existing.destination_airport_code = route.destination_airport_code
        existing.origin_airport_code = route.origin_airport_code

        self.session.commit()
        self.session.refresh(existing)
        return existing

    def delete(self, route_id: UUID) -> None:
        route = self.session.get(Route, route_id)
        if route is None:
            raise ValueError("Route not found")
        self.session.delete(route)
        self.session.commit()

    def deletion_proposal(self, route_id: UUID) -> tuple[list[Flight], list[FlightCrew]]:
        flights = (
            self.session.scalars(
                select(Flight)
                .where(Flight.route_id == route_id)
                .where(
                    Flight.flight_status == FlightStatus.SCHEDULED,
                    Flight.flight_status == FlightStatus.DELAYED
                )
            ).all()
        )

        flight_crew = (
            self.session.scalars(
                select(FlightCrew)
                .join(Flight, Flight.route_id == FlightCrew.flight_id)
                .where(Flight.route_id == route_id)
                .where(
                    Flight.flight_status == FlightStatus.SCHEDULED,
                    Flight.flight_status == FlightStatus.DELAYED
                )
            ).all()
        )
        
        return (flights, flight_crew)