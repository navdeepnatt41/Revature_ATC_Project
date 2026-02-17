from typing import Optional
from uuid import UUID

from src.domain.route import Route
from src.domain.flight import Flight
from src.domain.flight_crew import FlightCrew


class RouteRepositoryMock:
    def create(self, route: Route) -> Route:
        return route

    def get_by_id(self, route_id: UUID) -> Optional[Route]:
        return Route(
            route_id=route_id, origin_airport_code="JFK", destination_airport_code="JFK"
        )
    
    def get_by_airport_codes(
        self, origin_airport_code: str, destination_airport_code: str
    ) -> Optional[Route]:
        return Route(
            route_id="b1111111-1111-1111-1111-111111111111", origin_airport_code=origin_airport_code, destination_airport_code=destination_airport_code
        )

    def list_all(self) -> list[Route]:
        return [
            Route(
                route_id="b1111111-1111-1111-1111-111111111111",
                origin_airport_code="JFK",
                destination_airport_code="LAX",
            ),
            Route(
                route_id="b2222222-2222-2222-2222-222222222222",
                origin_airport_code="LAX",
                destination_airport_code="JFK",
            ),
        ]

    def update(self, route: Route) -> Route:
        return route

    def delete(self, route_id: UUID) -> None:
        pass

    def deletion_proposal(
        self, route_id: UUID
    ) -> tuple[list[Flight], list[FlightCrew]]:
        return (
            [],
            []
        )