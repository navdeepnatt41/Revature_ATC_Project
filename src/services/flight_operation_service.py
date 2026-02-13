from typing import Optional
from uuid import UUID
from src.domain.route import Route
from src.domain.in_flight_employee import InFlightEmployee, InFlightStatus
from src.domain.aircraft import Aircraft
from src.domain.airport import Airport
from src.domain.flight_crew import FlightCrew
from src.domain.flight import Flight

from src.repositories.aircraft_repository_protocol import AircraftRepositoryProtocol
from src.repositories.airport_repository_protocol import AirportRepositoryProtocol
from src.repositories.flight_crew_repository_protocol import FlightCrewRepositoryProtocol
from src.repositories.flight_repository_protocol import FlightRepositoryProtocol
from src.repositories.in_flight_employee_repository_protocol import InFlightEmployeeRepositoryProtocol
from src.repositories.route_repository_protocol import RouteRepositoryProtocol
from src.repositories.in_flight_employee_repository import InFlightEmployeeRepositoryProtocol

class FlightOperationService:
    #
    # Initialization with all repositories needed for operations
    #-----------------------------------------------------------------
    def __init__(
        self, 
        aircraft_repo: AircraftRepositoryProtocol,
        airport_repo: AirportRepositoryProtocol,
        flight_crew_repo: FlightCrewRepositoryProtocol,
        flight_repo: FlightRepositoryProtocol,
        in_flight_employee_repo: InFlightEmployeeRepositoryProtocol,
        route_repo: RouteRepositoryProtocol 
    ):
        self.aircraft_repo = aircraft_repo
        self.airport_repo = airport_repo
        self.flight_crew_repo = flight_crew_repo
        self.flight_repo = flight_repo
        self.in_flight_employee_repo = in_flight_employee_repo
        self.repo = route_repo
    #------------------------------------------------------------------
    
    #
    # ROUTE SERVICE
    #-------------------------------------------------------------------
    def route_create(self, route: Route) -> Route:
        self._validate_route(route, require_id=False)
        return self.route_repo.create(route)

    def route_get(self, route_id: UUID) -> Optional[Route]:
        return self.route_repo.get(route_id)

    def route_list_all(self) -> list[Route]:
        return self.route_repo.list_all()

    def route_update(self, route: Route) -> Route:
        self._validate_route(route, require_id=True)
        return self.route_repo.update(route)

    def route_delete(self, route_id: UUID) -> None:
        self.route_repo.delete(route_id)

    def _validate_route(self, route: Route, require_id: bool) -> None:
        if require_id and not route.route_id:
            raise ValueError("route_id is required for update")
        if not route.origin_airport_code:
            raise ValueError("origin_airport_code is required")
        if not route.destination_airport_code:
            raise ValueError("destination_airport_code is required")
        if route.origin_airport_code == route.destination_airport_code:
            raise ValueError("origin and destination airports must be different")
    #-------------------------------------------------------------------
    
    #
    # IN-FLIGHT EMPLOYEE SERVICE
    #-------------------------------------------------------------------
    ALLOWED_STATUSES = {InFlightStatus.AVAILABLE, InFlightStatus.SCHEDULED}

    def update_status(self, employee: InFlightEmployee, status: InFlightStatus) -> InFlightEmployee:
        return self.in_flight_employee_repo.update_status(employee, status)
    
    def get(self, employee_id: UUID) -> Optional[InFlightEmployee]:
        return self.in_flight_employee_repo.get(employee_id)

    def listall(self) -> list[InFlightEmployee]:
        return self.in_flight_employee_repo.list_all()
    
    #-------------------------------------------------------------------
    