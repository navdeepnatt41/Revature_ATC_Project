from typing import Optional
from uuid import UUID

from src.domain.exceptions import (
    AppErrorException,
    EntityAlreadyExistsException,
    NotFoundException,
)

from src.domain.route import Route
from src.repositories.airport_repository_protocol import AirportRepositoryProtocol
from src.repositories.flight_crew_repository_protocol import (
    FlightCrewRepositoryProtocol,
)
from src.repositories.flight_repository_protocol import FlightRepositoryProtocol
from src.repositories.route_repository_protocol import RouteRepositoryProtocol

class RouteService:
    def __init__(
            self,
            airport_repo: AirportRepositoryProtocol,
            flight_crew_repo: FlightCrewRepositoryProtocol,
            flight_repo: FlightRepositoryProtocol,
            route_repo: RouteRepositoryProtocol,
        ):
            self.airport_repo = airport_repo
            self.flight_crew_repo = flight_crew_repo
            self.flight_repo = flight_repo
            self.route_repo = route_repo
    
    def route_create(
        self, origin_airport_code: str, destination_airport_code: str
    ) -> Route:
        self._validate_route(
            origin_airport_code, destination_airport_code, require_id=False
        )
        return self.route_repo.create(origin_airport_code, destination_airport_code)

    def route_get(self, route_id: UUID) -> Optional[Route]:
        route = self.route_repo.get_by_id(route_id)
        if not route:
            raise NotFoundException("This route does not exist.")
        return route

    def route_list_all(self) -> list[Route]:
        return self.route_repo.list_all()

    def route_update(
        self,
        route_id: UUID,
        origin_airport_code: str,
        destination_airport_code: str,
    ) -> Route:
        self._validate_route(
            origin_airport_code,
            destination_airport_code,
            require_id=True,
            route_id=route_id,
        )
        route = Route(
            route_id=route_id,
            origin_airport_code=origin_airport_code,
            destination_airport_code=destination_airport_code,
        )
        return self.route_repo.update(route)

    def route_delete(self, route_id: UUID) -> None:
        route = self.route_repo.get_by_id(route_id)
        if not route:
            raise NotFoundException("This route does not exist.")
        
        candidate_flights = [
            flight
            for flight in self.flight_repo.list_all()
            if flight.route_id == route_id  
        ]

        target_flight_ids = [f.flight_id for f in candidate_flights]

        candidate_flight_crews = [
            crew
            for crew in self.flight_crew_repo.list_all()
            if crew.flight_id in target_flight_ids
        ]

        for cfc in candidate_flight_crews:
            self.flight_crew_repo.delete(cfc.flight_id, cfc.employee_id)

        for c_f in candidate_flights:
            self.flight_repo.delete(c_f.flight_id)

        # Third: Delete the Route itself
        self.route_repo.delete(route_id)

    def deletion_proposal(self, route_id: str):
        route = self.route_repo.get_by_id(route_id)
        if not route:
            raise NotFoundException("This route does not exist.")
        return self.route_repo.deletion_proposal(route_id=route_id)

    def _validate_route(
        self,
        origin_airport_code,
        destination_airport_code,
        require_id: bool,
        route_id=None,
    ) -> None:
        if require_id and not route_id:
            raise AppErrorException("route_id is required for update")
        if not origin_airport_code:
            raise AppErrorException("origin_airport_code is required")
        if not destination_airport_code:
            raise AppErrorException("destination_airport_code is required")
        if origin_airport_code == destination_airport_code:
            raise AppErrorException("origin and destination airports must be different")
        if self.airport_repo.get(origin_airport_code) is None:
            raise NotFoundException("Origin airport cannot be found")
        if self.airport_repo.get(destination_airport_code) is None:
            raise NotFoundException("Destination airport cannot be found")
        # Check if this route exists already:
        existing_route = self.route_repo.get_by_airport_codes(
            origin_airport_code, destination_airport_code
        )
        if existing_route:
            raise EntityAlreadyExistsException("Proposed route already exists")