import uuid
from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.base import Base
from src.domain.aircraft import Aircraft
from src.domain.airport import Airport

from src.domain.flight import Flight, FlightStatus
from src.domain.flight_crew import FlightCrew
from src.domain.in_flight_employee import EmployeePosition, InFlightEmployee, InFlightStatus
from src.domain.route import Route
from src.repositories.aircraft_repository import AircraftRepository
from src.repositories.airport_repository import AirportRepository
from src.repositories.flight_crew_repository import FlightCrewRepository
from src.repositories.flight_repository import FlightRepository
from src.repositories.in_flight_employee_repository import InFlightEmployeeRepository
from src.repositories.route_repository import RouteRepository
from src.domain.aircraft import AircraftStatus

@pytest.fixture(scope="function")
def test_db():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = SessionLocal()

    yield session

    session.close()
    engine.dispose()

class TestAirportRepository:
    def test_create_and_get_airport(self, test_db):
        repo = AirportRepository(test_db)
        airport = Airport(
            airport_code="TEST",
            airport_name="Test Airport",
            airport_country="Test Country",
            airport_city="Test City",
            airport_address="123 Test St",
            longitude=10.0,
            latitude=20.0,
        )
        repo.create(airport)

        # Assuming the model uses 'airport_id' as the primary key
        retrieved = repo.get(airport.airport_id)
        assert retrieved is not None
        assert retrieved.airport_name == "Test Airport"
        assert retrieved.airport_code == "TEST"

    def test_get_nonexistent_airport(self, test_db):
        repo = AirportRepository(test_db)
        retrieved = repo.get(uuid.uuid4())
        assert retrieved is None

    def test_list_all_airports(self, test_db):
        repo = AirportRepository(test_db)
        a1 = Airport(airport_code="T1", airport_name="A1", airport_country="C", airport_city="City", airport_address="Add", longitude=0, latitude=0)
        a2 = Airport(airport_code="T2", airport_name="A2", airport_country="C", airport_city="City", airport_address="Add", longitude=0, latitude=0)
        repo.create(a1)
        repo.create(a2)

        airports = repo.list_all()
        assert len(airports) == 2
        codes = {a.airport_code for a in airports}
        assert "T1" in codes and "T2" in codes

    def test_update_airport(self, test_db):
        repo = AirportRepository(test_db)
        airport = Airport(
            airport_code="OLD",
            airport_name="Old Name",
            airport_country="Test",
            airport_city="Old City",
            airport_address="123 St",
            longitude=0.0,
            latitude=0.0,
        )
        repo.create(airport)

        # FIXED: Using correct attribute names defined in your Airport domain
        airport.airport_name = "Updated Name"
        airport.airport_city = "Updated City"
        repo.update(airport)

        retrieved = repo.get(airport.airport_id)
        assert retrieved.airport_name == "Updated Name"
        assert retrieved.airport_city == "Updated City"

    def test_delete_airport(self, test_db):
        repo = AirportRepository(test_db)
        airport = Airport(airport_code="DEL", airport_name="Delete Me", airport_country="C", airport_city="C", airport_address="A", longitude=0, latitude=0)
        repo.create(airport)
        
        repo.delete(airport.airport_id)
        assert repo.get(airport.airport_id) is None

class TestAircraftRepository:
    def test_create_and_get_aircraft(self, test_db):
        repo = AircraftRepository(test_db)
        aircraft = Aircraft(
            manufacturer="Boeing",
            aircraft_model="737",
            current_distance=0.0,
            maintenance_interval=100.0,
            aircraft_status=AircraftStatus.AVAILABLE,
            aircraft_location="TST"
        )
        repo.create(aircraft)

        # FIXED: Consistency with aircraft_id
        retrieved = repo.get(aircraft.aircraft_id)
        assert retrieved is not None
        assert retrieved.aircraft_model == "737"
        assert retrieved.aircraft_id is not None # Validates UUID generation

    def test_list_all_aircrafts(self, test_db):
        repo = AircraftRepository(test_db)
        repo.create(Aircraft(manufacturer="A", aircraft_model="M1", current_distance=0, maintenance_interval=100, aircraft_status=AircraftStatus.AVAILABLE, aircraft_location="L"))
        repo.create(Aircraft(manufacturer="B", aircraft_model="M2", current_distance=0, maintenance_interval=100, aircraft_status=AircraftStatus.AVAILABLE, aircraft_location="L"))

        aircrafts = repo.list_all()
        assert len(aircrafts) == 2

    def test_available_aircraft_by_airport(self, test_db):
        # 1. Setup Dependencies
        airport_repo = AirportRepository(test_db)
        airport = Airport(
            airport_code="JFK",
            airport_name="John F Kennedy",
            airport_country="USA",
            airport_city="NY",
            airport_address="Queens",
            longitude=0,
            latitude=0
        )
        airport_repo.create(airport)

        # 2. Setup Aircraft
        aircraft_repo = AircraftRepository(test_db)
        a1 = Aircraft(
            manufacturer="Airbus",
            aircraft_model="A320",
            current_distance=0,
            maintenance_interval=500,
            aircraft_status=AircraftStatus.AVAILABLE,
            aircraft_location="JFK" # Matches airport_code
        )
        a2 = Aircraft(
            manufacturer="Airbus",
            aircraft_model="A380",
            current_distance=0,
            maintenance_interval=500,
            aircraft_status=AircraftStatus.AOG, # Out of service
            aircraft_location="JFK"
        )
        
        created_a1 = aircraft_repo.create(a1)
        aircraft_repo.create(a2)

        # 3. Test logic - Assuming search is done by the Airport's Primary Key (UUID)
        available = aircraft_repo.available_aircraft_by_airport(airport.airport_id)
        
        assert len(available) == 1
        assert available[0].aircraft_id == created_a1.aircraft_id
        assert available[0].aircraft_status == AircraftStatus.AVAILABLE


class TestFlightCrewRepository:
    def flight_crew_dependencies(self, test_db):
        # Create airports
        airport_repo = AirportRepository(test_db)
        jfk = Airport(
            airport_code="JFK",
            airport_name="John F Kennedy",
            airport_country="USA",
            airport_city="NY",
            airport_address="Queens",
            longitude=0,
            latitude=0,
        )
        lax = Airport(
            airport_code="LAX",
            airport_name="Los Angeles Intl",
            airport_country="USA",
            airport_city="LA",
            airport_address="LA Address",
            longitude=0,
            latitude=0,
        )
        airport_repo.create(jfk)
        airport_repo.create(lax)

        # Create route using RouteRepository
        route_repo = RouteRepository(test_db)
        route = route_repo.create(origin_airport_code="JFK", destination_airport_code="LAX")

        # Create aircraft
        aircraft_repo = AircraftRepository(test_db)
        aircraft = Aircraft(
            manufacturer="Boeing",
            aircraft_model="737",
            current_distance=0.0,
            maintenance_interval=100.0,
            aircraft_status=AircraftStatus.AVAILABLE,
            aircraft_location="JFK",
        )
        aircraft = aircraft_repo.create(aircraft)

        # Create flight
        flight_repo = FlightRepository(test_db)
        flight = Flight(
            route_id=route.route_id,
            aircraft_id=aircraft.aircraft_id,
            flight_status=FlightStatus.SCHEDULED,
            departure_time=datetime.utcnow(),
            arrival_time=datetime.utcnow(),
        )
        flight = flight_repo.create(flight)

        # Create employee
        employee_repo = InFlightEmployeeRepository(test_db)
        employee = InFlightEmployee(
            first_name="John",
            last_name="Doe",
            position=EmployeePosition.CAPTAIN,
            employee_status=InFlightStatus.AVAILABLE,
            supervisor=None,
            employee_location="JFK",
        )
        employee = employee_repo.create(employee)

        return {"flight": flight, "employee": employee}

    def test_create_and_get_flight_crew(self, test_db):
        deps = self.flight_crew_dependencies(test_db)
        repo = FlightCrewRepository(test_db)

        fc = FlightCrew(flight_id=deps["flight"].flight_id, employee_id=deps["employee"].employee_id)
        created = repo.create(fc)

        retrieved = repo.get(deps["flight"].flight_id, deps["employee"].employee_id)
        assert retrieved is not None
        assert retrieved.flight_id == created.flight_id
        assert retrieved.employee_id == created.employee_id

    def test_create_multiple_and_list_all(self, test_db):
        deps = self.flight_crew_dependencies(test_db)
        repo = FlightCrewRepository(test_db)
        employee_repo = InFlightEmployeeRepository(test_db)

        # create two more employees and assign to same flight
        e1 = InFlightEmployee(
            first_name="A",
            last_name="One",
            position=EmployeePosition.FLIGHT_ATTENDANT,
            employee_status=InFlightStatus.AVAILABLE,
            supervisor=None,
            employee_location="JFK",
        )
        e2 = InFlightEmployee(
            first_name="B",
            last_name="Two",
            position=EmployeePosition.FLIGHT_ATTENDANT,
            employee_status=InFlightStatus.AVAILABLE,
            supervisor=None,
            employee_location="JFK",
        )
        e1 = employee_repo.create(e1)
        e2 = employee_repo.create(e2)

        repo.create(FlightCrew(flight_id=deps["flight"].flight_id, employee_id=deps["employee"].employee_id))
        repo.create(FlightCrew(flight_id=deps["flight"].flight_id, employee_id=e1.employee_id))
        repo.create(FlightCrew(flight_id=deps["flight"].flight_id, employee_id=e2.employee_id))

        all_crews = repo.list_all()
        assert len(all_crews) >= 3

    def test_get_nonexistent_flight_crew(self, test_db):
        repo = FlightCrewRepository(test_db)
        result = repo.get(uuid.uuid4(), uuid.uuid4())
        assert result is None

    def test_get_by_flight(self, test_db):
        deps = self.flight_crew_dependencies(test_db)
        repo = FlightCrewRepository(test_db)

        repo.create(FlightCrew(flight_id=deps["flight"].flight_id, employee_id=deps["employee"].employee_id))
        by_flight = repo.get_by_flight(deps["flight"].flight_id)
        assert isinstance(by_flight, list)
        assert any(fc.employee_id == deps["employee"].employee_id for fc in by_flight)

    def test_update_flight_crew_and_update_nonexistent(self, test_db):
        deps = self.flight_crew_dependencies(test_db)
        repo = FlightCrewRepository(test_db)

        fc = FlightCrew(flight_id=deps["flight"].flight_id, employee_id=deps["employee"].employee_id)
        repo.create(fc)

        updated = repo.update(fc)
        assert updated.flight_id == fc.flight_id
        assert updated.employee_id == fc.employee_id

        # nonexistent
        with pytest.raises(ValueError):
            repo.update(FlightCrew(flight_id=uuid.uuid4(), employee_id=uuid.uuid4()))

    def test_delete_flight_crew_and_nonexistent(self, test_db):
        deps = self.flight_crew_dependencies(test_db)
        repo = FlightCrewRepository(test_db)

        fc = FlightCrew(flight_id=deps["flight"].flight_id, employee_id=deps["employee"].employee_id)
        repo.create(fc)

        repo.delete(deps["flight"].flight_id, deps["employee"].employee_id)
        assert repo.get(deps["flight"].flight_id, deps["employee"].employee_id) is None

        with pytest.raises(ValueError):
            repo.delete(uuid.uuid4(), uuid.uuid4())


class TestInFlightEmployeeRepository:
    def test_create_employee(self, test_db):
        airport_repo = AirportRepository(test_db)
        airport = Airport(
            airport_code="JFK",
            airport_name="John F Kennedy",
            airport_country="USA",
            airport_city="NY",
            airport_address="Queens",
            longitude=0,
            latitude=0,
        )
        airport_repo.create(airport)

        repo = InFlightEmployeeRepository(test_db)
        emp = InFlightEmployee(
            first_name="Alice",
            last_name="Smith",
            position=EmployeePosition.COPILOT,
            employee_status=InFlightStatus.AVAILABLE,
            supervisor=None,
            employee_location="JFK",
        )

        created = repo.create(emp)
        assert created.employee_id is not None
        assert created.first_name == "Alice"

    def test_get_employee_by_id(self, test_db):
        airport = Airport(airport_code="LAX", airport_name="LAX", airport_country="USA", airport_city="LA", airport_address="Addr", longitude=0, latitude=0)
        AirportRepository(test_db).create(airport)

        repo = InFlightEmployeeRepository(test_db)
        emp = InFlightEmployee(
            first_name="Bob",
            last_name="Brown",
            position=EmployeePosition.CAPTAIN,
            employee_status=InFlightStatus.AVAILABLE,
            supervisor=None,
            employee_location="LAX",
        )
        created = repo.create(emp)

        fetched = repo.get(created.employee_id)
        assert fetched is not None
        assert fetched.employee_id == created.employee_id

    def test_get_nonexistent_employee(self, test_db):
        repo = InFlightEmployeeRepository(test_db)
        assert repo.get(uuid.uuid4()) is None

    def test_list_all_employees(self, test_db):
        AirportRepository(test_db).create(Airport(airport_code="AAA", airport_name="A", airport_country="C", airport_city="City", airport_address="Addr", longitude=0, latitude=0))
        repo = InFlightEmployeeRepository(test_db)
        for i in range(3):
            repo.create(InFlightEmployee(
                first_name=f"F{i}",
                last_name=f"L{i}",
                position=EmployeePosition.FLIGHT_ATTENDANT,
                employee_status=InFlightStatus.AVAILABLE,
                supervisor=None,
                employee_location="AAA",
            ))

        all_emps = repo.list_all()
        assert len(all_emps) == 3

    def test_update_status_location(self, test_db):
        AirportRepository(test_db).create(Airport(airport_code="SFO", airport_name="SFO", airport_country="USA", airport_city="SF", airport_address="Addr", longitude=0, latitude=0))
        repo = InFlightEmployeeRepository(test_db)
        emp = repo.create(InFlightEmployee(
            first_name="Cara",
            last_name="Lane",
            position=EmployeePosition.FLIGHT_MANAGER,
            employee_status=InFlightStatus.AVAILABLE,
            supervisor=None,
            employee_location="SFO",
        ))

        updated = repo.update_status_location(emp, InFlightStatus.SCHEDULED, "JFK")
        assert updated.employee_status == InFlightStatus.SCHEDULED
        assert updated.employee_location == "JFK"

    def test_update_nonexistent_employee_raises(self, test_db):
        repo = InFlightEmployeeRepository(test_db)
        fake = InFlightEmployee(employee_id=uuid.uuid4(), first_name="X", last_name="Y", position=EmployeePosition.COPILOT, employee_status=InFlightStatus.AVAILABLE, supervisor=None, employee_location="JFK")
        with pytest.raises(ValueError):
            repo.update_status_location(fake, InFlightStatus.SCHEDULED, "LAX")

    def test_delete_employee(self, test_db):
        AirportRepository(test_db).create(Airport(airport_code="DEL", airport_name="DEL", airport_country="C", airport_city="C", airport_address="A", longitude=0, latitude=0))
        repo = InFlightEmployeeRepository(test_db)
        emp = repo.create(InFlightEmployee(
            first_name="D",
            last_name="E",
            position=EmployeePosition.FLIGHT_ATTENDANT,
            employee_status=InFlightStatus.AVAILABLE,
            supervisor=None,
            employee_location="DEL",
        ))

        repo.delete(emp.employee_id)
        assert repo.get(emp.employee_id) is None

    def test_delete_nonexistent_employee_raises(self, test_db):
        repo = InFlightEmployeeRepository(test_db)
        with pytest.raises(ValueError):
            repo.delete(uuid.uuid4())

    def test_available_employees_at_airport(self, test_db):
        AirportRepository(test_db).create(Airport(airport_code="X1", airport_name="X1", airport_country="C", airport_city="C", airport_address="A", longitude=0, latitude=0))
        repo = InFlightEmployeeRepository(test_db)
        # one available at X1
        repo.create(InFlightEmployee(first_name="Avail", last_name="One", position=EmployeePosition.FLIGHT_ATTENDANT, employee_status=InFlightStatus.AVAILABLE, supervisor=None, employee_location="X1"))
        # one scheduled at X1 (should not be returned)
        repo.create(InFlightEmployee(first_name="Sched", last_name="Two", position=EmployeePosition.FLIGHT_ATTENDANT, employee_status=InFlightStatus.SCHEDULED, supervisor=None, employee_location="X1"))
        # available elsewhere
        AirportRepository(test_db).create(Airport(airport_code="Y1", airport_name="Y1", airport_country="C", airport_city="C", airport_address="A", longitude=0, latitude=0))
        repo.create(InFlightEmployee(first_name="Avail", last_name="Three", position=EmployeePosition.COPILOT, employee_status=InFlightStatus.AVAILABLE, supervisor=None, employee_location="Y1"))

        avail = repo.available_employees_at_airport("X1")
        assert all(e.employee_location == "X1" for e in avail)
        assert all(e.employee_status == InFlightStatus.AVAILABLE for e in avail)


class TestFlightRepository:
    def test_create_and_get_flight(self, test_db):
        # create dependencies
        airport_repo = AirportRepository(test_db)
        airport_repo.create(Airport(airport_code="ORG", airport_name="Org", airport_country="C", airport_city="OriginCity", airport_address="A", longitude=0, latitude=0))

        route_repo = RouteRepository(test_db)
        route = route_repo.create(origin_airport_code="ORG", destination_airport_code="DST")

        aircraft_repo = AircraftRepository(test_db)
        aircraft = aircraft_repo.create(Aircraft(manufacturer="M", aircraft_model="X", current_distance=0, maintenance_interval=100, aircraft_status=AircraftStatus.AVAILABLE, aircraft_location="ORG"))

        repo = FlightRepository(test_db)
        flight = Flight(route_id=route.route_id, aircraft_id=aircraft.aircraft_id, flight_status=FlightStatus.SCHEDULED, departure_time=datetime.utcnow(), arrival_time=datetime.utcnow())
        created = repo.create(flight)

        fetched = repo.get(created.flight_id)
        assert fetched is not None
        assert fetched.flight_id == created.flight_id

    def test_list_all_flights(self, test_db):
        # setup
        airport_repo = AirportRepository(test_db)
        airport_repo.create(Airport(airport_code="A1", airport_name="A1", airport_country="C", airport_city="City1", airport_address="Addr", longitude=0, latitude=0))

        route_repo = RouteRepository(test_db)
        route = route_repo.create(origin_airport_code="A1", destination_airport_code="B1")

        aircraft_repo = AircraftRepository(test_db)
        ac = aircraft_repo.create(Aircraft(manufacturer="M", aircraft_model="X", current_distance=0, maintenance_interval=100, aircraft_status=AircraftStatus.AVAILABLE, aircraft_location="A1"))

        repo = FlightRepository(test_db)
        repo.create(Flight(route_id=route.route_id, aircraft_id=ac.aircraft_id, flight_status=FlightStatus.SCHEDULED, departure_time=datetime.utcnow(), arrival_time=datetime.utcnow()))
        repo.create(Flight(route_id=route.route_id, aircraft_id=ac.aircraft_id, flight_status=FlightStatus.DELAYED, departure_time=datetime.utcnow(), arrival_time=datetime.utcnow()))

        all_flights = repo.list_all()
        assert len(all_flights) >= 2

    def test_update_flight(self, test_db):
        # setup dependencies
        airport_repo = AirportRepository(test_db)
        airport_repo.create(Airport(airport_code="U1", airport_name="U1", airport_country="C", airport_city="UC", airport_address="Addr", longitude=0, latitude=0))

        route_repo = RouteRepository(test_db)
        r1 = route_repo.create(origin_airport_code="U1", destination_airport_code="D1")
        r2 = route_repo.create(origin_airport_code="U1", destination_airport_code="D2")

        aircraft_repo = AircraftRepository(test_db)
        a1 = aircraft_repo.create(Aircraft(manufacturer="M", aircraft_model="A1", current_distance=0, maintenance_interval=100, aircraft_status=AircraftStatus.AVAILABLE, aircraft_location="U1"))
        a2 = aircraft_repo.create(Aircraft(manufacturer="M", aircraft_model="A2", current_distance=0, maintenance_interval=100, aircraft_status=AircraftStatus.AVAILABLE, aircraft_location="U1"))

        repo = FlightRepository(test_db)
        flight = repo.create(Flight(route_id=r1.route_id, aircraft_id=a1.aircraft_id, flight_status=FlightStatus.SCHEDULED, departure_time=datetime.utcnow(), arrival_time=datetime.utcnow()))

        # modify and update
        flight.route_id = r2.route_id
        flight.aircraft_id = a2.aircraft_id
        flight.flight_status = FlightStatus.DELAYED
        updated = repo.update(flight)

        assert updated.route_id == r2.route_id
        assert updated.aircraft_id == a2.aircraft_id
        assert updated.flight_status == FlightStatus.DELAYED

    def test_update_nonexistent_flight_raises(self, test_db):
        repo = FlightRepository(test_db)
        fake = Flight(flight_id=uuid.uuid4(), route_id=uuid.uuid4(), aircraft_id=uuid.uuid4(), flight_status=FlightStatus.SCHEDULED, departure_time=datetime.utcnow(), arrival_time=datetime.utcnow())
        with pytest.raises(ValueError):
            repo.update(fake)

    def test_delete_flight(self, test_db):
        route = Route(origin_airport_code="DEL1", destination_airport_code="DEL2")
        test_db.add(route)
        test_db.commit()

        aircraft = Aircraft(manufacturer="M", aircraft_model="DM", current_distance=0, maintenance_interval=100, aircraft_status=AircraftStatus.AVAILABLE, aircraft_location="DEL1")
        test_db.add(aircraft)
        test_db.commit()

        repo = FlightRepository(test_db)
        flight = repo.create(Flight(route_id=route.route_id, aircraft_id=aircraft.aircraft_id, flight_status=FlightStatus.SCHEDULED, departure_time=datetime.utcnow(), arrival_time=datetime.utcnow()))

        repo.delete(flight.flight_id)
        assert repo.get(flight.flight_id) is None

    def test_delete_nonexistent_flight_raises(self, test_db):
        repo = FlightRepository(test_db)
        with pytest.raises(ValueError):
            repo.delete(uuid.uuid4())

    def test_get_scheduled_by_city(self, test_db):
        # create origin airport
        AirportRepository(test_db).create(Airport(airport_code="OC", airport_name="OC", airport_country="C", airport_city="OriginCity", airport_address="Addr", longitude=0, latitude=0))
        # route from OC to DC
        route = Route(origin_airport_code="OC", destination_airport_code="DC")
        test_db.add(route)
        test_db.commit()

        # aircraft
        aircraft = Aircraft(manufacturer="M", aircraft_model="F", current_distance=0, maintenance_interval=100, aircraft_status=AircraftStatus.AVAILABLE, aircraft_location="OC")
        test_db.add(aircraft)
        test_db.commit()

        # create scheduled flight
        repo = FlightRepository(test_db)
        flight = repo.create(Flight(route_id=route.route_id, aircraft_id=aircraft.aircraft_id, flight_status=FlightStatus.SCHEDULED, departure_time=datetime.utcnow(), arrival_time=datetime.utcnow()))

        found = repo.get_scheduled_by_city("OriginCity")
        assert any(f.flight_id == flight.flight_id for f in found)

    def test_update_flight_status_in_flight(self, test_db):
        # setup
        route = Route(origin_airport_code="UF", destination_airport_code="VF")
        test_db.add(route)
        test_db.commit()

        aircraft = Aircraft(manufacturer="M", aircraft_model="S", current_distance=0, maintenance_interval=100, aircraft_status=AircraftStatus.AVAILABLE, aircraft_location="UF")
        test_db.add(aircraft)
        test_db.commit()

        repo = FlightRepository(test_db)
        flight = repo.create(Flight(route_id=route.route_id, aircraft_id=aircraft.aircraft_id, flight_status=FlightStatus.SCHEDULED, departure_time=datetime.utcnow(), arrival_time=datetime.utcnow()))

        updated = repo.update_flight_status_in_flight(flight.flight_id)
        assert updated.flight_status == FlightStatus.IN_FLIGHT
