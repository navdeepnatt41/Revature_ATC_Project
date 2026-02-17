from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict
from uuid import UUID, uuid4
from unittest.mock import MagicMock

import pytest

from src.domain.aircraft import Aircraft, AircraftStatus
from src.domain.airport import Airport
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
from src.domain.route import Route
from src.repositories.aircraft_repository_protocol import AircraftRepositoryProtocol
from src.repositories.airport_repository_protocol import AirportRepositoryProtocol
from src.repositories.flight_crew_repository_protocol import FlightCrewRepositoryProtocol
from src.repositories.flight_repository_protocol import FlightRepositoryProtocol
from src.repositories.in_flight_employee_repository_protocol import (
    InFlightEmployeeRepositoryProtocol,
)
from src.repositories.route_repository_protocol import RouteRepositoryProtocol
from src.services.aircraft_service import AircraftService
from src.services.flight_service import FlightService
from src.services.in_flight_employee_service import InFlightEmployeeService
from src.services.route_service import RouteService


RepositoryMap = Dict[str, MagicMock]


@pytest.fixture
def mock_repositories() -> RepositoryMap:
    return {
        "airport_repo": MagicMock(spec=AirportRepositoryProtocol),
        "aircraft_repo": MagicMock(spec=AircraftRepositoryProtocol),
        "in_flight_employee_repo": MagicMock(
            spec=InFlightEmployeeRepositoryProtocol
        ),
        "route_repo": MagicMock(spec=RouteRepositoryProtocol),
        "flight_repo": MagicMock(spec=FlightRepositoryProtocol),
        "flight_crew_repo": MagicMock(spec=FlightCrewRepositoryProtocol),
    }


@pytest.fixture
def test_data(mock_repositories: RepositoryMap) -> dict[str, Any]:
    airport_repo = mock_repositories["airport_repo"]
    aircraft_repo = mock_repositories["aircraft_repo"]
    in_flight_employee_repo = mock_repositories["in_flight_employee_repo"]
    route_repo = mock_repositories["route_repo"]
    flight_repo = mock_repositories["flight_repo"]
    flight_crew_repo = mock_repositories["flight_crew_repo"]

    airports: Dict[str, Airport] = {
        "JFK": Airport(
            airport_code="JFK",
            airport_name="John F. Kennedy",
            airport_country="USA",
            airport_city="New York",
            airport_address="Queens",
            longitude="-73.7781",
            latitude="40.6413",
        ),
        "LAX": Airport(
            airport_code="LAX",
            airport_name="Los Angeles",
            airport_country="USA",
            airport_city="Los Angeles",
            airport_address="1 World Way",
            longitude="-118.4085",
            latitude="33.9416",
        ),
    }

    airport_repo.get.side_effect = lambda code: airports.get(code)
    airport_repo.list_all.return_value = list(airports.values())

    aog_id = uuid4()
    available_id = uuid4()
    deployed_id = uuid4()
    spare_id = uuid4()

    aircraft_store: Dict[UUID, Aircraft] = {
        aog_id: Aircraft(
            aircraft_id=aog_id,
            manufacturer="Boeing",
            aircraft_model="737",
            current_distance=600.0,
            maintenance_interval=2000.0,
            aircraft_status=AircraftStatus.AOG,
            aircraft_location="JFK",
        ),
        available_id: Aircraft(
            aircraft_id=available_id,
            manufacturer="Airbus",
            aircraft_model="A320",
            current_distance=200.0,
            maintenance_interval=1500.0,
            aircraft_status=AircraftStatus.AVAILABLE,
            aircraft_location="JFK",
        ),
        deployed_id: Aircraft(
            aircraft_id=deployed_id,
            manufacturer="Boeing",
            aircraft_model="787",
            current_distance=100.0,
            maintenance_interval=2500.0,
            aircraft_status=AircraftStatus.DEPLOYED,
            aircraft_location="LAX",
        ),
        spare_id: Aircraft(
            aircraft_id=spare_id,
            manufacturer="Embraer",
            aircraft_model="E195",
            current_distance=50.0,
            maintenance_interval=1200.0,
            aircraft_status=AircraftStatus.AVAILABLE,
            aircraft_location="JFK",
        ),
    }

    def save_aircraft(aircraft: Aircraft) -> Aircraft:
        aircraft_store[aircraft.aircraft_id] = aircraft
        return aircraft

    aircraft_repo.get.side_effect = lambda aircraft_id: aircraft_store.get(aircraft_id)
    aircraft_repo.list_all.side_effect = lambda: list(aircraft_store.values())
    aircraft_repo.update.side_effect = save_aircraft
    aircraft_repo.create.side_effect = save_aircraft
    aircraft_repo.delete.side_effect = lambda aircraft_id: aircraft_store.pop(
        aircraft_id, None
    )
    aircraft_repo.available_aircraft_by_airport.side_effect = (
        lambda code: [
            aircraft
            for aircraft in aircraft_store.values()
            if aircraft.aircraft_location == code
            and aircraft.aircraft_status == AircraftStatus.AVAILABLE
        ]
    )

    captain_id = uuid4()
    copilot_id = uuid4()
    manager_id = uuid4()
    attendant_id = uuid4()
    scheduled_employee_id = uuid4()

    def employee_template(
        employee_id: UUID,
        first: str,
        last: str,
        position: EmployeePosition,
        status: InFlightStatus,
    ) -> InFlightEmployee:
        return InFlightEmployee(
            employee_id=employee_id,
            first_name=first,
            last_name=last,
            position=position,
            employee_status=status,
            supervisor=employee_id,
            employee_location="JFK",
        )

    employee_store: Dict[UUID, InFlightEmployee] = {
        captain_id: employee_template(
            captain_id, "Alex", "Avery", EmployeePosition.CAPTAIN, InFlightStatus.AVAILABLE
        ),
        copilot_id: employee_template(
            copilot_id, "Casey", "Cole", EmployeePosition.COPILOT, InFlightStatus.AVAILABLE
        ),
        manager_id: employee_template(
            manager_id,
            "Morgan",
            "Moore",
            EmployeePosition.FLIGHT_MANAGER,
            InFlightStatus.AVAILABLE,
        ),
        attendant_id: employee_template(
            attendant_id,
            "Parker",
            "Poe",
            EmployeePosition.FLIGHT_ATTENDANT,
            InFlightStatus.AVAILABLE,
        ),
        scheduled_employee_id: InFlightEmployee(
            employee_id=scheduled_employee_id,
            first_name="Sam",
            last_name="Smith",
            position=EmployeePosition.FLIGHT_ATTENDANT,
            employee_status=InFlightStatus.SCHEDULED,
            supervisor=scheduled_employee_id,
            employee_location="JFK",
        ),
    }

    in_flight_employee_repo.get.side_effect = lambda employee_id: employee_store.get(
        employee_id
    )
    in_flight_employee_repo.list_all.side_effect = lambda: list(employee_store.values())
    in_flight_employee_repo.available_employees_at_airport.side_effect = (
        lambda code: [
            employee
            for employee in employee_store.values()
            if employee.employee_location == code
            and employee.employee_status == InFlightStatus.AVAILABLE
        ]
    )

    def update_employee_status(
        employee: InFlightEmployee, status: InFlightStatus, location: str
    ) -> InFlightEmployee:
        employee.employee_status = status
        employee.employee_location = location
        employee_store[employee.employee_id] = employee
        return employee

    in_flight_employee_repo.update_status_location.side_effect = update_employee_status
    in_flight_employee_repo.delete.side_effect = lambda employee_id: employee_store.pop(
        employee_id, None
    )

    route_store: Dict[UUID, Route] = {}

    def create_route(origin: str, destination: str) -> Route:
        route = Route(
            route_id=uuid4(),
            origin_airport_code=origin,
            destination_airport_code=destination,
        )
        route_store[route.route_id] = route
        return route

    route_repo.create.side_effect = create_route
    route_repo.get_by_id.side_effect = lambda route_id: route_store.get(route_id)
    route_repo.get_by_airport_codes.side_effect = (
        lambda origin, destination: next(
            (
                route
                for route in route_store.values()
                if route.origin_airport_code == origin
                and route.destination_airport_code == destination
            ),
            None,
        )
    )
    route_repo.list_all.side_effect = lambda: list(route_store.values())
    route_repo.update.side_effect = lambda route: (
        route_store.__setitem__(route.route_id, route) or route
    )
    route_repo.delete.side_effect = lambda route_id: route_store.pop(route_id, None)
    route_repo.deletion_proposal.return_value = ([], [])

    default_route = create_route("JFK", "LAX")

    flight_store: Dict[UUID, Flight] = {}

    def create_flight(flight: Flight) -> Flight:
        if getattr(flight, "flight_id", None) is None:
            flight.flight_id = uuid4()
        flight_store[flight.flight_id] = flight
        return flight

    def update_flight(flight: Flight) -> Flight:
        flight_store[flight.flight_id] = flight
        return flight

    flight_repo.get.side_effect = lambda flight_id: flight_store.get(flight_id)
    flight_repo.list_all.side_effect = lambda: list(flight_store.values())
    flight_repo.create.side_effect = create_flight
    flight_repo.update.side_effect = update_flight
    flight_repo.delete.side_effect = lambda flight_id: flight_store.pop(flight_id, None)
    flight_repo.get_scheduled_by_city.return_value = []

    def update_in_flight(flight_id: UUID) -> Flight:
        flight = flight_store.get(flight_id)
        if flight is None:
            raise NotFoundException("Flight cannot be found")
        flight.flight_status = FlightStatus.IN_FLIGHT
        flight_store[flight_id] = flight
        return flight

    flight_repo.update_flight_status_in_flight.side_effect = update_in_flight

    flight_crew_store: Dict[tuple[UUID, UUID], FlightCrew] = {}

    def create_assignment(assignment: FlightCrew) -> FlightCrew:
        if getattr(assignment, "flight_crew_id", None) is None:
            assignment.flight_crew_id = uuid4()
        flight_crew_store[(assignment.flight_id, assignment.employee_id)] = assignment
        return assignment

    flight_crew_repo.list_all.side_effect = lambda: list(flight_crew_store.values())
    flight_crew_repo.delete.side_effect = (
        lambda flight_id, employee_id: flight_crew_store.pop((flight_id, employee_id), None)
    )
    flight_crew_repo.get_by_flight.side_effect = (
        lambda flight_id: [
            assignment
            for assignment in flight_crew_store.values()
            if assignment.flight_id == flight_id
        ]
    )
    flight_crew_repo.get.side_effect = (
        lambda flight_id, employee_id: flight_crew_store.get((flight_id, employee_id))
    )
    flight_crew_repo.create.side_effect = create_assignment

    aircraft_service = AircraftService(
        aircraft_repo=aircraft_repo,
        airport_repo=airport_repo,
    )
    in_flight_employee_service = InFlightEmployeeService(
        in_flight_employee_repo=in_flight_employee_repo,
        airport_repo=airport_repo,
    )
    route_service = RouteService(
        airport_repo=airport_repo,
        flight_crew_repo=flight_crew_repo,
        flight_repo=flight_repo,
        route_repo=route_repo,
    )
    flight_service = FlightService(
        aircraft_repo=aircraft_repo,
        airport_repo=airport_repo,
        flight_crew_repo=flight_crew_repo,
        flight_repo=flight_repo,
        in_flight_employee_repo=in_flight_employee_repo,
        route_repo=route_repo,
    )

    return {
        "aircraft_service": aircraft_service,
        "in_flight_employee_service": in_flight_employee_service,
        "route_service": route_service,
        "flight_service": flight_service,
        "aircraft_store": aircraft_store,
        "employee_store": employee_store,
        "aircraft_ids": {
            "aog": aog_id,
            "available": available_id,
            "deployed": deployed_id,
            "spare": spare_id,
        },
        "employee_ids": {
            "captain": captain_id,
            "copilot": copilot_id,
            "manager": manager_id,
            "attendant": attendant_id,
            "scheduled": scheduled_employee_id,
        },
        "routes_store": route_store,
        "route_ids": {"jfk_lax": default_route.route_id},
        "flight_store": flight_store,
        "mocks": mock_repositories,
    }


class TestAircraftService:
    def test_service_get_available_aircraft_at_airport(
        self, test_data: dict[str, Any]
    ) -> None:
        service: AircraftService = test_data["aircraft_service"]

        available = service.available_aircraft_at_airport("JFK")

        assert len(available) == 1
        assert available[0].aircraft_id == test_data["aircraft_ids"]["available"]

    def test_service_get_available_aircraft_invalid_airport(
        self, test_data: dict[str, Any]
    ) -> None:
        service: AircraftService = test_data["aircraft_service"]

        with pytest.raises(NotFoundException):
            service.available_aircraft_at_airport("ORD")

    def test_service_repair_aircraft(self, test_data: dict[str, Any]) -> None:
        service: AircraftService = test_data["aircraft_service"]
        aircraft_id = test_data["aircraft_ids"]["aog"]

        repaired = service.repair_aircraft(aircraft_id)

        assert repaired.aircraft_status == AircraftStatus.AVAILABLE
        assert repaired.current_distance == 0

    def test_service_schedule_repair_aircraft(self, test_data: dict[str, Any]) -> None:
        service: AircraftService = test_data["aircraft_service"]
        aircraft_id = test_data["aircraft_ids"]["available"]

        scheduled = service.schedule_repair_aircraft(aircraft_id)

        assert scheduled.aircraft_status == AircraftStatus.AOG

    def test_service_schedule_repair_aircraft_rejects_busy_aircraft(
        self, test_data: dict[str, Any]
    ) -> None:
        service: AircraftService = test_data["aircraft_service"]
        aircraft_id = test_data["aircraft_ids"]["deployed"]

        with pytest.raises(PermissionDeniedException):
            service.schedule_repair_aircraft(aircraft_id)


class TestInFlightEmployeeService:
    def test_service_available_employees_at_airport(
        self, test_data: dict[str, Any]
    ) -> None:
        service: InFlightEmployeeService = test_data["in_flight_employee_service"]

        employees = service.available_employees_at_airport("JFK")

        assert len(employees) == 1
        assert employees[0].employee_status == InFlightStatus.AVAILABLE

    def test_service_available_employees_airport_not_found(
        self, test_data: dict[str, Any]
    ) -> None:
        service: InFlightEmployeeService = test_data["in_flight_employee_service"]

        with pytest.raises(NotFoundException):
            service.available_employees_at_airport("ORD")


class TestRouteService:
    def test_service_create_route(self, test_data: dict[str, Any]) -> None:
        service: RouteService = test_data["route_service"]
        routes_store: Dict[UUID, Route] = test_data["routes_store"]

        route = service.route_create("JFK", "LAX")

        assert route.origin_airport_code == "JFK"
        assert route.route_id in routes_store

    def test_service_create_route_rejects_duplicates(
        self, test_data: dict[str, Any]
    ) -> None:
        service: RouteService = test_data["route_service"]

        service.route_create("JFK", "LAX")
        with pytest.raises(EntityAlreadyExistsException):
            service.route_create("JFK", "LAX")

    def test_service_create_route_rejects_identical_airports(
        self, test_data: dict[str, Any]
    ) -> None:
        service: RouteService = test_data["route_service"]

        with pytest.raises(AppErrorException):
            service.route_create("JFK", "JFK")


class TestFlightService:
    def _schedule_basic_flight(self, test_data: dict[str, Any]) -> Flight:
        service: FlightService = test_data["flight_service"]
        route_id = test_data["route_ids"]["jfk_lax"]
        aircraft_id = test_data["aircraft_ids"]["available"]
        departure = datetime.utcnow()
        arrival = departure + timedelta(hours=5)

        return service.schedule_flight(route_id, aircraft_id, arrival, departure)

    def _schedule_required_employees(
        self, test_data: dict[str, Any], flight: Flight
    ) -> list[UUID]:
        service: FlightService = test_data["flight_service"]
        employee_ids = [
            test_data["employee_ids"]["captain"],
            test_data["employee_ids"]["copilot"],
            test_data["employee_ids"]["manager"],
            test_data["employee_ids"]["attendant"],
        ]
        service.schedule_employees(flight.flight_id, employee_ids)
        return employee_ids

    def test_service_schedule_flight_deploys_aircraft(
        self, test_data: dict[str, Any]
    ) -> None:
        flight = self._schedule_basic_flight(test_data)

        assert flight.flight_status == FlightStatus.SCHEDULED
        aircraft = test_data["aircraft_store"][test_data["aircraft_ids"]["available"]]
        assert aircraft.aircraft_status == AircraftStatus.DEPLOYED

    def test_service_schedule_employees_sets_required_positions(
        self, test_data: dict[str, Any]
    ) -> None:
        flight = self._schedule_basic_flight(test_data)
        self._schedule_required_employees(test_data, flight)

        employees = test_data["employee_store"]
        for role in ("captain", "copilot", "manager", "attendant"):
            employee = employees[test_data["employee_ids"][role]]
            assert employee.employee_status == InFlightStatus.SCHEDULED

    def test_service_launch_flight_with_complete_crew(
        self, test_data: dict[str, Any]
    ) -> None:
        service: FlightService = test_data["flight_service"]
        flight = self._schedule_basic_flight(test_data)
        self._schedule_required_employees(test_data, flight)

        launched = service.launch_flight(flight.flight_id)

        assert launched.flight_status == FlightStatus.IN_FLIGHT

    def test_service_delay_flight_updates_times_and_status(
        self, test_data: dict[str, Any]
    ) -> None:
        service: FlightService = test_data["flight_service"]
        flight = self._schedule_basic_flight(test_data)
        original_departure = flight.departure_time
        original_arrival = flight.arrival_time

        delayed = service.delay_flight(flight.flight_id, 30)

        assert delayed.flight_status == FlightStatus.DELAYED
        assert delayed.departure_time == original_departure + timedelta(minutes=30)
        assert delayed.arrival_time == original_arrival + timedelta(minutes=30)

    def test_service_cancel_flight_releases_resources(
        self, test_data: dict[str, Any]
    ) -> None:
        service: FlightService = test_data["flight_service"]
        flight = self._schedule_basic_flight(test_data)
        employee_ids = self._schedule_required_employees(test_data, flight)

        cancelled = service.cancel_flight(flight.flight_id)

        assert cancelled.flight_status == FlightStatus.CANCELLED
        aircraft = test_data["aircraft_store"][test_data["aircraft_ids"]["available"]]
        assert aircraft.aircraft_status == AircraftStatus.AVAILABLE
        for employee_id in employee_ids:
            assert (
                test_data["employee_store"][employee_id].employee_status
                == InFlightStatus.AVAILABLE
            )

    def test_service_change_aircraft_for_flight_updates_statuses(
        self, test_data: dict[str, Any]
    ) -> None:
        service: FlightService = test_data["flight_service"]
        flight = self._schedule_basic_flight(test_data)
        new_aircraft_id = test_data["aircraft_ids"]["spare"]

        updated_flight = service.change_aircraft_for_flight(
            flight.flight_id, new_aircraft_id
        )

        assert updated_flight.aircraft_id == new_aircraft_id
        original_aircraft = test_data["aircraft_store"][test_data["aircraft_ids"]["available"]]
        replacement_aircraft = test_data["aircraft_store"][new_aircraft_id]
        assert original_aircraft.aircraft_status == AircraftStatus.AVAILABLE
        assert replacement_aircraft.aircraft_status == AircraftStatus.DEPLOYED