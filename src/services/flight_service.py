from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
from math import radians, sin, cos, asin, sqrt

from src.domain.aircraft import Aircraft, AircraftStatus
from src.domain.exceptions import (
    AppErrorException,
    EntityAlreadyExistsException,
    NotFoundException,
    PermissionDeniedException,
)


from src.domain.flight import Flight, FlightStatus
from src.domain.flight_crew import FlightCrew
from src.domain.in_flight_employee import (
    EmployeePosition,
    InFlightEmployee,
    InFlightStatus,
)

from src.repositories.aircraft_repository_protocol import AircraftRepositoryProtocol
from src.repositories.airport_repository_protocol import AirportRepositoryProtocol
from src.repositories.flight_crew_repository_protocol import FlightCrewRepositoryProtocol
from src.repositories.flight_repository_protocol import FlightRepositoryProtocol
from src.repositories.in_flight_employee_repository_protocol import InFlightEmployeeRepositoryProtocol
from src.repositories.route_repository_protocol import RouteRepositoryProtocol


class FlightService:
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
        self.route_repo = route_repo
    
    def calculate_distance(self, from_coordinates: tuple, to_coordinates: tuple) -> int:
        """Calculate distance in miles between two coordinates using Haversine formula"""
        lon1, lat1 = from_coordinates
        lon2, lat2 = to_coordinates
        lon1 = float(lon1)
        lon2 = float(lon2)
        lat1 = float(lat1)
        lat2 = float(lat2)
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 3956  # miles
        return int(c * r)
    
    def confirm_flight_landed(self, flight_id: UUID) -> Aircraft:
        flight = self.flight_repo.get(flight_id)
        if flight is None:
            raise NotFoundException("Flight cannot be found")
        if flight.flight_status != FlightStatus.IN_FLIGHT:
            raise PermissionDeniedException("The flight is already grounded")

        aircraft = self.aircraft_repo.get(flight.aircraft_id)
        crew = self.flight_crew_repo.get_by_flight(flight_id)
        route = self.route_repo.get_by_id(flight.route_id)
        origin = self.airport_repo.get(route.origin_airport_code)
        destination = self.airport_repo.get(route.destination_airport_code)

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
        aircraft.current_distance += self.calculate_distance((origin.longitude, origin.latitude), (destination.longitude, destination.latitude))
        if aircraft.current_distance > aircraft.maintenance_interval:
            aircraft.aircraft_status = AircraftStatus.AOG
        else:
            aircraft.aircraft_status = AircraftStatus.AVAILABLE

        return self.aircraft_repo.update(aircraft)

    def cancel_flight(self, flight_id: UUID) -> Flight:
        flight = self.flight_repo.get(flight_id)
        if flight is None:
            raise NotFoundException("Flight cannot be found")

        if flight.flight_status not in [FlightStatus.SCHEDULED, FlightStatus.DELAYED]:
            raise PermissionDeniedException(
                "Only scheduled or delayed flights can be cancelled"
            )

        aircraft = self.aircraft_repo.get(flight.aircraft_id)
        if aircraft is None:
            raise NotFoundException("Associated aircraft cannot be found")

        # Cancel the flight:
        flight.flight_status = FlightStatus.CANCELLED
        updated_flight = self.flight_repo.update(flight)

        # Set Aircraft to available:
        aircraft.aircraft_status = AircraftStatus.AVAILABLE
        self.aircraft_repo.update(aircraft)

        # Unassign employees:
        assignments = self.flight_crew_repo.get_by_flight(flight_id)
        for assignment in assignments:
            employee = self.in_flight_employee_repo.get(assignment.employee_id)
            if employee is None:
                continue
            self.in_flight_employee_repo.update_status_location(
                employee,
                InFlightStatus.AVAILABLE,
                employee.employee_location,
            )

        return updated_flight

    def schedule_flight(
        self, route_id: UUID, aircraft_id: UUID, arrival: datetime, departure: datetime
    ) -> Flight:
        route = self.route_repo.get_by_id(route_id)
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
            raise PermissionDeniedException("Departure time must be before arrival time")

        print(f"{route_id} - {aircraft_id} - {arrival} - {departure}")
        new_flight = Flight(
            route_id=route_id,
            aircraft_id=aircraft_id,
            flight_status=FlightStatus.SCHEDULED,
            arrival_time=arrival,
            departure_time=departure,
        )

        created_flight = self.flight_repo.create(new_flight)

        aircraft.aircraft_status = AircraftStatus.DEPLOYED
        self.aircraft_repo.update(aircraft)

        return created_flight
    
    def launch_flight(self, flight_id: UUID) -> Flight:
        """
        Validates flight crew and launches the flight.
        
        Raises:
            NotFoundException: If flight or crew members not found
            PermissionDeniedException: If flight crew is missing or incomplete
        """
        flight = self.flight_repo.get(flight_id)
        if flight is None:
            raise NotFoundException("Flight cannot be found")
        
        if flight.flight_status not in [FlightStatus.SCHEDULED, FlightStatus.DELAYED]:
            raise PermissionDeniedException(
                "Only scheduled or delayed flights can be launched"
            )
        
        # Check if flight has a flight crew
        flight_crew = self.flight_crew_repo.get_by_flight(flight_id)
        if not flight_crew:
            raise PermissionDeniedException(
                "Flight cannot depart without a flight crew assigned"
            )

        # Check if flight crew has required positions
        required_positions = {
            EmployeePosition.CAPTAIN,
            EmployeePosition.COPILOT,
            EmployeePosition.FLIGHT_MANAGER,
            EmployeePosition.FLIGHT_ATTENDANT,
        }

        crew_positions: set = set()
        for assignment in flight_crew:
            employee = self.in_flight_employee_repo.get(assignment.employee_id)
            if employee is None:
                raise NotFoundException(
                    f"Employee with ID {assignment.employee_id} not found"
                )
            crew_positions.add(employee.position)

        if not required_positions.issubset(crew_positions):
            missing_positions = required_positions - crew_positions
            raise PermissionDeniedException(
                f"Flight cannot depart. Missing positions: {', '.join([p.value for p in missing_positions])}"
            )

        # Update flight status to IN-FLIGHT
        return self.flight_repo.update_flight_status_in_flight(flight_id)

    def delay_flight(self, flight_id: UUID, extra_minutes: int):
        flight = self.flight_repo.get(flight_id)
        if flight is None:
            raise NotFoundException("Flight cannot be found")
        if extra_minutes is None:
            raise AppErrorException("Need number of minutes to delay flight by ")
        if flight.flight_status not in [FlightStatus.DELAYED, FlightStatus.SCHEDULED]:
            raise PermissionDeniedException(f"Cannot delay flight that is {flight.flight_status}")

        if flight.departure_time:
            flight.departure_time += timedelta(minutes=extra_minutes)

        if flight.arrival_time:
            flight.arrival_time += timedelta(minutes=extra_minutes)

        if flight.flight_status:
            flight.flight_status = FlightStatus.DELAYED

        return self.flight_repo.update(flight)

    def delete_flight(self, flight_id: UUID):
        self.flight_repo.delete(flight_id)

    def change_aircraft_for_flight(self, flight_id: UUID, aircraft_id: UUID) -> Flight:
        flight = self.flight_repo.get(flight_id)
        aircraft = self.aircraft_repo.get(aircraft_id)
        old_aircraft = self.aircraft_repo.get(flight.aircraft_id)

        if flight is None:
            raise NotFoundException("Flight cannot be found")
        if aircraft is None:
            raise NotFoundException("New Aircraft cannot be found")
        if old_aircraft is None:
            raise NotFoundException("Associated aircraft cannot be found")
        if old_aircraft.aircraft_id == aircraft_id:
            raise AppErrorException("Aircraft already assigned to this Flight")
        if old_aircraft.aircraft_location != aircraft.aircraft_location:
            raise PermissionDeniedException("Aircraft not in the same airport as Flight")
        if aircraft.aircraft_status == AircraftStatus.DEPLOYED:
            raise AppErrorException(
                f"Aircraft: {aircraft.aircraft_id} is already assigned or deployed"
            )

        # Set new Aircraft to deployed and old aircraft to available:
        old_aircraft.aircraft_status = AircraftStatus.AVAILABLE
        self.aircraft_repo.update(old_aircraft)
        aircraft.aircraft_status = AircraftStatus.DEPLOYED
        self.aircraft_repo.update(aircraft)

        flight.aircraft_id = aircraft_id

        return self.flight_repo.update(flight)

    def schedule_employees(
        self, flight_id: UUID, employee_ids: list[UUID]
    ) -> list[FlightCrew]:
        flight = self.flight_repo.get(flight_id)
        if flight is None:
            raise NotFoundException("Flight cannot be found")

        route = self.route_repo.get_by_id(flight.route_id)
        if route is None:
            raise NotFoundException("Route for flight cannot be found")

        if not employee_ids:
            raise AppErrorException(
                "At least one employee must be scheduled for the flight"
            )

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
                raise NotFoundException(
                    f"Employee with ID {employee_id} cannot be found"
                )

            if employee.employee_location != route.origin_airport_code:
                raise PermissionDeniedException(
                    f"Employee {employee_id} is not located at the route origin airport"
                )

            if employee.employee_status != InFlightStatus.AVAILABLE:
                raise PermissionDeniedException(
                    f"Employee {employee_id} is not available"
                )

            existing_assignment = self.flight_crew_repo.get(
                flight.flight_id, employee_id
            )
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