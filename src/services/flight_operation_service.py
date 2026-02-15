from typing import Optional
from uuid import UUID
from datetime import timedelta, datetime

from src.domain.exceptions import NotFoundException, AppErrorException, PermissionDeniedException, EntityAlreadyExistsException
from src.domain.route import Route
from src.domain.in_flight_employee import InFlightEmployee, InFlightStatus, EmployeePosition
from src.domain.aircraft import Aircraft, AircraftStatus
from src.domain.flight_crew import FlightCrew
from src.domain.flight import Flight, FlightStatus

from src.dto import aircraft
from src.repositories.aircraft_repository_protocol import AircraftRepositoryProtocol
from src.repositories.airport_repository_protocol import AirportRepositoryProtocol
from src.repositories.flight_crew_repository_protocol import (
    FlightCrewRepositoryProtocol,
)
from src.repositories.flight_repository_protocol import FlightRepositoryProtocol
from src.repositories.in_flight_employee_repository_protocol import (
    InFlightEmployeeRepositoryProtocol,
)
from src.repositories.route_repository_protocol import RouteRepositoryProtocol


class FlightOperationService:
    # ===================================================================
    # Initialization with all repositories needed for operations
    # ===================================================================
    def __init__(
        self,
        aircraft_repo: AircraftRepositoryProtocol,
        airport_repo: AirportRepositoryProtocol,
        flight_crew_repo: FlightCrewRepositoryProtocol,
        flight_repo: FlightRepositoryProtocol,
        in_flight_employee_repo: InFlightEmployeeRepositoryProtocol,
        route_repo: RouteRepositoryProtocol,
    ):
        self.aircraft_repo = aircraft_repo
        self.airport_repo = airport_repo
        self.flight_crew_repo = flight_crew_repo
        self.flight_repo = flight_repo
        self.in_flight_employee_repo = in_flight_employee_repo
        self.route_repo = route_repo

    # ===================================================================

    # ===================================================================
    # ROUTE SERVICE
    # ===================================================================
    def route_create(self, origin_airport_code: str, destination_airport_code: str) -> Route:
        self._validate_route(origin_airport_code, destination_airport_code, require_id=False)
        route = Route(
            origin_airport_code=origin_airport_code,
            destination_airport_code=destination_airport_code,
        )
        return self.route_repo.create(route)

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
        self.route_repo.delete(route_id)

    def _validate_route(self, origin_airport_code, destination_airport_code, require_id: bool, route_id=None) -> None:
        if require_id and not route_id:
            raise ValueError("route_id is required for update")
        if not origin_airport_code:
            raise ValueError("origin_airport_code is required")
        if not destination_airport_code:
            raise ValueError("destination_airport_code is required")
        if origin_airport_code == destination_airport_code:
            raise ValueError("origin and destination airports must be different")
        if self.airport_repo.get(origin_airport_code) is None:
            raise NotFoundException("Origin airport cannot be found")
        if self.airport_repo.get(destination_airport_code) is None:
            raise NotFoundException("Destination airport cannot be found")
        # Check if this route exists already:
        existing_route = self.route_repo.get_by_airports(origin_airport_code, destination_airport_code)
        if existing_route:
            raise EntityAlreadyExistsException("Proposed route already exists")

    # ===================================================================

    # ===================================================================
    # IN-FLIGHT EMPLOYEE SERVICE
    # ===================================================================
    ALLOWED_STATUSES = {InFlightStatus.AVAILABLE, InFlightStatus.SCHEDULED}

    def update_status(
        self, employee: InFlightEmployee, status: InFlightStatus
    ) -> InFlightEmployee:
        return self.in_flight_employee_repo.update_status(employee, status)

    def get(self, employee_id: UUID) -> Optional[InFlightEmployee]:
        return self.in_flight_employee_repo.get(employee_id)

    def listall(self) -> list[InFlightEmployee]:
        return self.in_flight_employee_repo.list_all()

    # ===================================================================

    # ===================================================================
    # Flight Service
    # ===================================================================
 
    def confirm_flight_landed(self, flight_id: UUID) -> Aircraft:
        flight = self.flight_repo.get(flight_id)
        if flight is None:
            raise NotFoundException("Flight cannot be found")
        if flight.flight_status != FlightStatus.IN_FLIGHT:
            raise AppErrorException("The flight is already grounded")

        aircraft = self.aircraft_repo.get(flight.aircraft_id)
        crew = self.flight_crew_repo.get_by_flight(flight_id)
        route = self.route_repo.get(flight.route_id)

        flight.flight_status = FlightStatus.ARRIVED
        self.flight_repo.update(flight)

        for crew_member in crew:
            employee = self.in_flight_employee_repo.get(crew_member.employee_id)
            self.in_flight_employee_repo.update_status_location(
                employee,
                InFlightStatus.AVAILABLE,
                route.destination_airport_code,
            )

        aircraft.aircraft_location = route.destination_airport_code
        aircraft.current_distance += 100  # REPLACE WITH DISTANCE CALCULATION
        if aircraft.current_distance > aircraft.maintenance_interval:
            aircraft.aircraft_status = AircraftStatus.AOG
        else:
            aircraft.aircraft_status = AircraftStatus.AVAILABLE

        return self.aircraft_repo.update(aircraft)

    def update_flight_status(self, flight_id: UUID, status: FlightStatus):
        flight = self.flight_repo.get(flight_id)
        if flight is None:
            raise NotFoundException("Flight cannot be found")
        flight.flight_status = status
        return self.flight_repo.update(flight)
    
    def schedule_flight(
        self,
        route_id: UUID,
        aircraft_id: UUID,
        arrival: datetime,
        departure: datetime
    ) -> Flight:
        route = self.route_repo.get(route_id)
        if route is None:
            raise NotFoundException("Route cannot be found")
        
        aircraft = self.aircraft_repo.get(aircraft_id)
        if aircraft is None:
            raise NotFoundException("Aircraft cannot be found")
        
        if aircraft.aircraft_location != route.origin_airport_code:
            raise PermissionDeniedException(
                "Aircraft is not located at the route origin airport"
            )
        
        if aircraft.aircraft_status != AircraftStatus.AVAILABLE:
            raise PermissionDeniedException("Aircraft is not available")
        
        if departure >= arrival:
            raise AppErrorException("Departure time must be before arrival time")
        
        new_flight = Flight(
            route_id=route_id,
            aircraft_id=aircraft_id,
            flight_status=FlightStatus.SCHEDULED,
            arrival_time=arrival,
            departure_time=departure
        )
        
        created_flight = self.flight_repo.create(new_flight)
        
        aircraft.aircraft_status = AircraftStatus.DEPLOYED
        self.aircraft_repo.update(aircraft)
        
        return created_flight
    
    def delay_flight(self, flight_id: UUID, extra_minutes: int):
        flight = self.flight_repo.get(flight_id)
        if flight is None:
            raise NotFoundException("Flight cannot be found")
        
        if flight.departure_time:
            flight.departure_time += timedelta(minutes= extra_minutes)
        
        if flight.arrival_time:
            flight.arrival_time += timedelta(minutes= extra_minutes)

        return self.flight_repo.update(flight)
    
    def delete_flight(self, flight_id: UUID):
        self.flight_repo.delete(flight_id)

    def change_aircraft_for_flight(self, flight_id: UUID, aircraft_id: UUID) -> Flight:
        flight = self.flight_repo.get(flight_id)
        aircraft = self.aircraft_repo.get(aircraft_id)

        if flight is None:
            raise NotFoundException("Flight cannot be found")
        if aircraft is None:
            raise NotFoundException("Aircraft cannot be found")

        flight.aircraft_id = aircraft_id
        return self.flight_repo.update(flight)        
    def schedule_employees(self, flight_id: UUID, employee_ids: list[UUID]) -> list[FlightCrew]:
        flight = self.flight_repo.get(flight_id)
        if flight is None:
            raise NotFoundException("Flight cannot be found")

        route = self.route_repo.get(flight.route_id)
        if route is None:
            raise NotFoundException("Route for flight cannot be found")

        if not employee_ids:
            raise AppErrorException("At least one employee must be scheduled for the flight")

        unique_ids = list(set(employee_ids))
        if len(unique_ids) != len(employee_ids):
            raise AppErrorException("Duplicate employee IDs are not allowed")

        required_positions = {
            EmployeePosition.CAPTAIN,
            EmployeePosition.COPILOT,
            EmployeePosition.FLIGHT_MANAGER,
            EmployeePosition.FLIGHT_ATTENDANT,
        }

        employees: list[InFlightEmployee] = []
        found_positions = set()

        for employee_id in unique_ids:
            employee = self.in_flight_employee_repo.get(employee_id)
            if employee is None:
                raise NotFoundException(f"Employee with ID {employee_id} cannot be found")

            if employee.employee_location != route.origin_airport_code:
                raise PermissionDeniedException(
                    f"Employee {employee_id} is not located at the route origin airport"
                )

            if employee.employee_status != InFlightStatus.AVAILABLE:
                raise PermissionDeniedException(f"Employee {employee_id} is not available")

            existing_assignment = self.flight_crew_repo.get(flight.flight_id, employee_id)
            if existing_assignment is not None:
                raise AppErrorException(
                    f"Employee {employee_id} is already assigned to this flight"
                )

            employees.append(employee)
            found_positions.add(employee.position)

        missing_positions = required_positions - found_positions
        if missing_positions:
            missing = ", ".join(sorted([p.value for p in missing_positions]))
            raise AppErrorException(f"Missing required employee positions: {missing}")

        created_assignments: list[FlightCrew] = []
        for employee in employees:
            assignment = self.flight_crew_repo.create(
                FlightCrew(
                    flight_id=flight.flight_id,
                    employee_id=employee.employee_id,
                )
            )
            created_assignments.append(assignment)

            self.in_flight_employee_repo.update_status_location(
                employee,
                InFlightStatus.SCHEDULED,
                employee.employee_location,
            )

        return created_assignments
    # ===================================================================