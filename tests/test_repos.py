import pytest
import uuid
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.base import Base
from src.domain.aircraft import Aircraft
from src.domain.airline import Airline
from src.domain.airport import Airport
from src.domain.flight import Flight, FlightStatus
from src.domain.flight_crew import FlightCrew
from src.domain.in_flight_employee import InFlightEmployee, EmployeePosition
from src.domain.operates import Operates
from src.domain.route import Route

from src.repositories.aircraft_repository import AircraftRepository
from src.repositories.airline_repository import AirlineRepository
from src.repositories.airport_repository import AirportRepository
from src.repositories.flight_repository import FlightRepository
from src.repositories.flight_crew_repository import FlightCrewRepository
from src.repositories.in_flight_employee_repository import InFlightEmployeeRepository
from src.repositories.operates_repository import OperatesRepository
from src.repositories.route_repository import RouteRepository


# ============================================================================
# Test Database Setup
# ============================================================================

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


# ============================================================================
# Airline Repository Tests
# ============================================================================

class TestAirlineRepository:
    """Tests for AirlineRepository CRUD operations."""
    
    def test_create_airline(self, test_db):
        """Test creating a new airline."""
        repo = AirlineRepository(test_db)
        airline = Airline(airline_designator="AA", name="American Airlines")
        
        result = repo.create(airline)
        
        assert result.airline_designator == "AA"
        assert result.name == "American Airlines"
    
    def test_create_multiple_airlines(self, test_db):
        """Test creating multiple airlines."""
        repo = AirlineRepository(test_db)
        airline1 = Airline(airline_designator="AA", name="American Airlines")
        airline2 = Airline(airline_designator="UA", name="United Airlines")
        
        repo.create(airline1)
        repo.create(airline2)
        
        assert repo.list_all().__len__() == 2
    
    def test_get_airline_by_designator(self, test_db):
        """Test retrieving an airline by designator."""
        repo = AirlineRepository(test_db)
        airline = Airline(airline_designator="AA", name="American Airlines")
        repo.create(airline)
        
        result = repo.get("AA")
        
        assert result is not None
        assert result.airline_designator == "AA"
        assert result.name == "American Airlines"
    
    def test_get_nonexistent_airline(self, test_db):
        """Test retrieving a nonexistent airline returns None."""
        repo = AirlineRepository(test_db)
        
        result = repo.get("XX")
        
        assert result is None
    
    def test_list_all_airlines(self, test_db):
        """Test listing all airlines."""
        repo = AirlineRepository(test_db)
        airlines = [
            Airline(airline_designator="AA", name="American Airlines"),
            Airline(airline_designator="UA", name="United Airlines"),
            Airline(airline_designator="DL", name="Delta Airlines"),
        ]
        for airline in airlines:
            repo.create(airline)
        
        result = repo.list_all()
        
        assert len(result) == 3
        assert all(isinstance(a, Airline) for a in result)
    
    def test_list_all_airlines_empty(self, test_db):
        """Test listing all airlines when none exist."""
        repo = AirlineRepository(test_db)
        
        result = repo.list_all()
        
        assert result == []
    
    def test_update_airline(self, test_db):
        """Test updating an airline."""
        repo = AirlineRepository(test_db)
        airline = Airline(airline_designator="AA", name="American Airlines")
        repo.create(airline)
        
        airline.name = "American Airlines Updated"
        result = repo.update(airline)
        
        assert result.name == "American Airlines Updated"
        assert result.airline_designator == "AA"
    
    def test_update_nonexistent_airline(self, test_db):
        """Test updating a nonexistent airline raises ValueError."""
        repo = AirlineRepository(test_db)
        airline = Airline(airline_designator="XX", name="Unknown Airlines")
        
        with pytest.raises(ValueError, match="Airline not found"):
            repo.update(airline)
    
    def test_delete_airline(self, test_db):
        """Test deleting an airline."""
        repo = AirlineRepository(test_db)
        airline = Airline(airline_designator="AA", name="American Airlines")
        repo.create(airline)
        
        repo.delete("AA")
        
        result = repo.get("AA")
        assert result is None
    
    def test_delete_nonexistent_airline(self, test_db):
        """Test deleting a nonexistent airline raises ValueError."""
        repo = AirlineRepository(test_db)
        
        with pytest.raises(ValueError, match="no airline found"):
            repo.delete("XX")

"""
# ============================================================================
# Airport Repository Tests
# ============================================================================

class TestAirportRepository:
    #Tests for AirportRepository CRUD operations.
    
    def test_create_airport(self, test_db):
        #Test creating a new airport.
        repo = AirportRepository(test_db)
        airport = Airport(
            airport_code="JFK",
            airport_name="John F. Kennedy International Airport",
            airport_country="USA",
            airport_city="New York",
            airport_address="Jamaica, Queens, New York"
        )
        
        result = repo.create(airport)
        
        assert result.airport_code == "JFK"
        assert result.airport_name == "John F. Kennedy International Airport"
    
    def test_create_multiple_airports(self, test_db):
        #Test creating multiple airports.
        repo = AirportRepository(test_db)
        airports = [
            Airport(airport_code="JFK", airport_name="JFK", airport_country="USA", 
                   airport_city="New York", airport_address="Jamaica, Queens"),
            Airport(airport_code="LAX", airport_name="LAX", airport_country="USA",
                   airport_city="Los Angeles", airport_address="El Segundo"),
        ]
        for airport in airports:
            repo.create(airport)
        
        assert len(repo.list_all()) == 2
    
    def test_get_airport_by_code(self, test_db):
        #Test retrieving an airport by code.#
        repo = AirportRepository(test_db)
        airport = Airport(
            airport_code="JFK", airport_name="JFK",
            airport_country="USA", airport_city="New York",
            airport_address="Jamaica, Queens"
        )
        repo.create(airport)
        
        result = repo.get("JFK")
        
        assert result is not None
        assert result.airport_code == "JFK"
    
    def test_get_nonexistent_airport(self, test_db):
        #Test retrieving a nonexistent airport returns None.#
        repo = AirportRepository(test_db)
        
        result = repo.get("XXX")
        
        assert result is None
    
    def test_list_all_airports(self, test_db):
        #Test listing all airports.#
        repo = AirportRepository(test_db)
        for code in ["JFK", "LAX", "ORD"]:
            airport = Airport(
                airport_code=code, airport_name=f"{code} Airport",
                airport_country="USA", airport_city="City",
                airport_address="Address"
            )
            repo.create(airport)
        
        result = repo.list_all()
        
        assert len(result) == 3
    
    def test_list_all_airports_empty(self, test_db):
        #Test listing all airports when none exist.#
        repo = AirportRepository(test_db)
        
        result = repo.list_all()
        
        assert result == []
    
    def test_update_airport(self, test_db):
        #Test updating an airport.#
        repo = AirportRepository(test_db)
        airport = Airport(
            airport_code="JFK", airport_name="JFK",
            airport_country="USA", airport_city="New York",
            airport_address="Jamaica, Queens"
        )
        repo.create(airport)
        
        airport.airport_name = "Kennedy International"
        airport.airport_city = "New York City"
        result = repo.update(airport)
        
        assert result.airport_name == "Kennedy International"
        assert result.airport_city == "New York City"
    
    def test_update_nonexistent_airport(self, test_db):
        #Test updating a nonexistent airport raises ValueError.#
        repo = AirportRepository(test_db)
        airport = Airport(
            airport_code="XXX", airport_name="Unknown",
            airport_country="Unknown", airport_city="Unknown",
            airport_address="Unknown"
        )
        
        with pytest.raises(ValueError, match="Airport not found"):
            repo.update(airport)
    
    def test_delete_airport(self, test_db):
        #Test deleting an airport.#
        repo = AirportRepository(test_db)
        airport = Airport(
            airport_code="JFK", airport_name="JFK",
            airport_country="USA", airport_city="New York",
            airport_address="Jamaica, Queens"
        )
        repo.create(airport)
        
        repo.delete("JFK")
        
        result = repo.get("JFK")
        assert result is None
    
    def test_delete_nonexistent_airport(self, test_db):
        #Test deleting a nonexistent airport raises ValueError.#
        repo = AirportRepository(test_db)
        
        with pytest.raises(ValueError, match="Airport not found"):
            repo.delete("XXX")


# ============================================================================
# Aircraft Repository Tests
# ============================================================================

class TestAircraftRepository:
    #Tests for AircraftRepository CRUD operations.#
    
    @pytest.fixture
    def airline_dependency(self, test_db):
        #Create an airline for aircraft tests.#
        airline = Airline(airline_designator="AA", name="American Airlines")
        test_db.add(airline)
        test_db.commit()
        return airline
    
    def test_create_aircraft(self, test_db, airline_dependency):
        #Test creating a new aircraft.#
        repo = AircraftRepository(test_db)
        aircraft = Aircraft(
            aircraft_id=uuid.uuid4(),
            airline_designator="AA",
            manufacturer="Boeing",
            aircraft_model="747"
        )
        
        result = repo.create(aircraft)
        
        assert result.manufacturer == "Boeing"
        assert result.aircraft_model == "747"
        assert result.airline_designator == "AA"
    
    def test_create_multiple_aircraft(self, test_db, airline_dependency):
        #Test creating multiple aircraft.#
        repo = AircraftRepository(test_db)
        aircraft1 = Aircraft(aircraft_id=uuid.uuid4(), airline_designator="AA",
                            manufacturer="Boeing", aircraft_model="747")
        aircraft2 = Aircraft(aircraft_id=uuid.uuid4(), airline_designator="AA",
                            manufacturer="Airbus", aircraft_model="A380")
        
        repo.create(aircraft1)
        repo.create(aircraft2)
        
        assert len(repo.list_all()) == 2
    
    def test_get_aircraft_by_id(self, test_db, airline_dependency):
        #Test retrieving an aircraft by ID.#
        repo = AircraftRepository(test_db)
        aircraft_id = uuid.uuid4()
        aircraft = Aircraft(
            aircraft_id=aircraft_id,
            airline_designator="AA",
            manufacturer="Boeing",
            aircraft_model="747"
        )
        repo.create(aircraft)
        
        result = repo.get(aircraft_id)
        
        assert result is not None
        assert result.aircraft_id == aircraft_id
        assert result.manufacturer == "Boeing"
    
    def test_get_nonexistent_aircraft(self, test_db):
        #Test retrieving a nonexistent aircraft returns None.#
        repo = AircraftRepository(test_db)
        
        result = repo.get(uuid.uuid4())
        
        assert result is None
    
    def test_list_all_aircraft(self, test_db, airline_dependency):
        #Test listing all aircraft.#
        repo = AircraftRepository(test_db)
        for i in range(3):
            aircraft = Aircraft(
                aircraft_id=uuid.uuid4(),
                airline_designator="AA",
                manufacturer=f"Manufacturer{i}",
                aircraft_model=f"Model{i}"
            )
            repo.create(aircraft)
        
        result = repo.list_all()
        
        assert len(result) == 3
    
    def test_list_all_aircraft_empty(self, test_db):
        #Test listing all aircraft when none exist.#
        repo = AircraftRepository(test_db)
        
        result = repo.list_all()
        
        assert result == []
    
    def test_update_aircraft(self, test_db, airline_dependency):
        #Test updating an aircraft.#
        repo = AircraftRepository(test_db)
        aircraft_id = uuid.uuid4()
        aircraft = Aircraft(
            aircraft_id=aircraft_id,
            airline_designator="AA",
            manufacturer="Boeing",
            aircraft_model="747"
        )
        repo.create(aircraft)
        
        aircraft.aircraft_model = "777"
        aircraft.manufacturer = "Boeing Updated"
        result = repo.update(aircraft)
        
        assert result.aircraft_model == "777"
        assert result.manufacturer == "Boeing Updated"
    
    def test_update_nonexistent_aircraft(self, test_db):
        #Test updating a nonexistent aircraft raises ValueError.#
        repo = AircraftRepository(test_db)
        aircraft = Aircraft(
            aircraft_id=uuid.uuid4(),
            airline_designator="AA",
            manufacturer="Boeing",
            aircraft_model="747"
        )
        
        with pytest.raises(ValueError, match="Aircraft not found"):
            repo.update(aircraft)
    
    def test_delete_aircraft(self, test_db, airline_dependency):
        #Test deleting an aircraft.#
        repo = AircraftRepository(test_db)
        aircraft_id = uuid.uuid4()
        aircraft = Aircraft(
            aircraft_id=aircraft_id,
            airline_designator="AA",
            manufacturer="Boeing",
            aircraft_model="747"
        )
        repo.create(aircraft)
        
        repo.delete(aircraft_id)
        
        result = repo.get(aircraft_id)
        assert result is None
    
    def test_delete_nonexistent_aircraft(self, test_db):
        #Test deleting a nonexistent aircraft raises ValueError.#
        repo = AircraftRepository(test_db)
        
        with pytest.raises(ValueError, match="Aircraft not found"):
            repo.delete(uuid.uuid4())


# ============================================================================
# Route Repository Tests
# ============================================================================

class TestRouteRepository:
    #Tests for RouteRepository CRUD operations.#
    
    @pytest.fixture
    def airports_dependency(self, test_db):
        #Create airports for route tests.#
        airports = [
            Airport(airport_code="JFK", airport_name="JFK", airport_country="USA",
                   airport_city="New York", airport_address="Jamaica"),
            Airport(airport_code="LAX", airport_name="LAX", airport_country="USA",
                   airport_city="Los Angeles", airport_address="El Segundo"),
        ]
        for airport in airports:
            test_db.add(airport)
        test_db.commit()
        return airports
    
    def test_create_route(self, test_db, airports_dependency):
        #Test creating a new route.#
        repo = RouteRepository(test_db)
        route = Route(
            route_id=uuid.uuid4(),
            origin_airport_code="JFK",
            destination_airport_code="LAX"
        )
        
        result = repo.create(route)
        
        assert result.origin_airport_code == "JFK"
        assert result.destination_airport_code == "LAX"
    
    def test_create_multiple_routes(self, test_db, airports_dependency):
        #Test creating multiple routes.#
        repo = RouteRepository(test_db)
        route1 = Route(route_id=uuid.uuid4(), origin_airport_code="JFK",
                      destination_airport_code="LAX")
        route2 = Route(route_id=uuid.uuid4(), origin_airport_code="LAX",
                      destination_airport_code="JFK")
        
        repo.create(route1)
        repo.create(route2)
        
        assert len(repo.list_all()) == 2
    
    def test_get_route_by_id(self, test_db, airports_dependency):
        #Test retrieving a route by ID.#
        repo = RouteRepository(test_db)
        route_id = uuid.uuid4()
        route = Route(
            route_id=route_id,
            origin_airport_code="JFK",
            destination_airport_code="LAX"
        )
        repo.create(route)
        
        result = repo.get(route_id)
        
        assert result is not None
        assert result.route_id == route_id
        assert result.origin_airport_code == "JFK"
    
    def test_get_nonexistent_route(self, test_db):
        #Test retrieving a nonexistent route returns None.#
        repo = RouteRepository(test_db)
        
        result = repo.get(uuid.uuid4())
        
        assert result is None
    
    def test_list_all_routes(self, test_db, airports_dependency):
        #Test listing all routes.#
        repo = RouteRepository(test_db)
        for i in range(3):
            route = Route(
                route_id=uuid.uuid4(),
                origin_airport_code="JFK",
                destination_airport_code="LAX"
            )
            repo.create(route)
        
        result = repo.list_all()
        
        assert len(result) == 3
    
    def test_list_all_routes_empty(self, test_db):
        #Test listing all routes when none exist.#
        repo = RouteRepository(test_db)
        
        result = repo.list_all()
        
        assert result == []
    
    def test_update_route(self, test_db, airports_dependency):
        #Test updating a route.#
        repo = RouteRepository(test_db)
        route_id = uuid.uuid4()
        route = Route(
            route_id=route_id,
            origin_airport_code="JFK",
            destination_airport_code="LAX"
        )
        repo.create(route)
        
        route.destination_airport_code = "LAX"
        result = repo.update(route)
        
        assert result.destination_airport_code == "LAX"
    
    def test_update_nonexistent_route(self, test_db):
        #Test updating a nonexistent route raises ValueError.#
        repo = RouteRepository(test_db)
        route = Route(
            route_id=uuid.uuid4(),
            origin_airport_code="JFK",
            destination_airport_code="LAX"
        )
        
        with pytest.raises(ValueError, match="Route not found"):
            repo.update(route)
    
    def test_delete_route(self, test_db, airports_dependency):
        #Test deleting a route.#
        repo = RouteRepository(test_db)
        route_id = uuid.uuid4()
        route = Route(
            route_id=route_id,
            origin_airport_code="JFK",
            destination_airport_code="LAX"
        )
        repo.create(route)
        
        repo.delete(route_id)
        
        result = repo.get(route_id)
        assert result is None
    
    def test_delete_nonexistent_route(self, test_db):
        #Test deleting a nonexistent route raises ValueError.#
        repo = RouteRepository(test_db)
        
        with pytest.raises(ValueError, match="Route not found"):
            repo.delete(uuid.uuid4())


# ============================================================================
# Flight Repository Tests
# ============================================================================

class TestFlightRepository:
    #Tests for FlightRepository CRUD operations.#
    
    @pytest.fixture
    def flight_dependencies(self, test_db):
        #Create dependencies for flight tests.#
        # Create airline
        airline = Airline(airline_designator="AA", name="American Airlines")
        test_db.add(airline)
        
        # Create airports
        airports = [
            Airport(airport_code="JFK", airport_name="JFK", airport_country="USA",
                   airport_city="New York", airport_address="Jamaica"),
            Airport(airport_code="LAX", airport_name="LAX", airport_country="USA",
                   airport_city="Los Angeles", airport_address="El Segundo"),
        ]
        for airport in airports:
            test_db.add(airport)
        
        # Create route
        route = Route(
            route_id=uuid.uuid4(),
            origin_airport_code="JFK",
            destination_airport_code="LAX"
        )
        test_db.add(route)
        
        # Create aircraft
        aircraft = Aircraft(
            aircraft_id=uuid.uuid4(),
            airline_designator="AA",
            manufacturer="Boeing",
            aircraft_model="747"
        )
        test_db.add(aircraft)
        
        test_db.commit()
        return {
            "route": route,
            "aircraft": aircraft,
            "airline": airline
        }
    
    def test_create_flight(self, test_db, flight_dependencies):
        #Test creating a new flight.#
        repo = FlightRepository(test_db)
        flight = Flight(
            flight_id=uuid.uuid4(),
            route_id=flight_dependencies["route"].route_id,
            aircraft_id=flight_dependencies["aircraft"].aircraft_id,
            flight_status=FlightStatus.SCHEDULED,
            dept_time=datetime(2026, 2, 12, 10, 0),
            arrival_time=datetime(2026, 2, 12, 14, 0)
        )
        
        result = repo.create(flight)
        
        assert result.flight_status == FlightStatus.SCHEDULED
        assert result.route_id == flight_dependencies["route"].route_id
    
    def test_create_multiple_flights(self, test_db, flight_dependencies):
        #Test creating multiple flights.#
        repo = FlightRepository(test_db)
        for i in range(3):
            flight = Flight(
                flight_id=uuid.uuid4(),
                route_id=flight_dependencies["route"].route_id,
                aircraft_id=flight_dependencies["aircraft"].aircraft_id,
                flight_status=FlightStatus.SCHEDULED,
                dept_time=datetime(2026, 2, 12, 10 + i, 0),
                arrival_time=datetime(2026, 2, 12, 14 + i, 0)
            )
            repo.create(flight)
        
        assert len(repo.list_all()) == 3
    
    def test_get_flight_by_id(self, test_db, flight_dependencies):
        #Test retrieving a flight by ID.#
        repo = FlightRepository(test_db)
        flight_id = uuid.uuid4()
        flight = Flight(
            flight_id=flight_id,
            route_id=flight_dependencies["route"].route_id,
            aircraft_id=flight_dependencies["aircraft"].aircraft_id,
            flight_status=FlightStatus.SCHEDULED,
            dept_time=datetime(2026, 2, 12, 10, 0),
            arrival_time=datetime(2026, 2, 12, 14, 0)
        )
        repo.create(flight)
        
        result = repo.get(flight_id)
        
        assert result is not None
        assert result.flight_id == flight_id
        assert result.flight_status == FlightStatus.SCHEDULED
    
    def test_get_nonexistent_flight(self, test_db):
        #Test retrieving a nonexistent flight returns None.#
        repo = FlightRepository(test_db)
        
        result = repo.get(uuid.uuid4())
        
        assert result is None
    
    def test_list_all_flights(self, test_db, flight_dependencies):
        #Test listing all flights.#
        repo = FlightRepository(test_db)
        for i in range(3):
            flight = Flight(
                flight_id=uuid.uuid4(),
                route_id=flight_dependencies["route"].route_id,
                aircraft_id=flight_dependencies["aircraft"].aircraft_id,
                flight_status=FlightStatus.SCHEDULED,
                dept_time=datetime(2026, 2, 12, 10 + i, 0),
                arrival_time=datetime(2026, 2, 12, 14 + i, 0)
            )
            repo.create(flight)
        
        result = repo.list_all()
        
        assert len(result) == 3
    
    def test_list_all_flights_empty(self, test_db):
        #Test listing all flights when none exist.#
        repo = FlightRepository(test_db)
        
        result = repo.list_all()
        
        assert result == []
    
    def test_update_flight(self, test_db, flight_dependencies):
        #Test updating a flight.#
        repo = FlightRepository(test_db)
        flight_id = uuid.uuid4()
        flight = Flight(
            flight_id=flight_id,
            route_id=flight_dependencies["route"].route_id,
            aircraft_id=flight_dependencies["aircraft"].aircraft_id,
            flight_status=FlightStatus.SCHEDULED,
            dept_time=datetime(2026, 2, 12, 10, 0),
            arrival_time=datetime(2026, 2, 12, 14, 0)
        )
        repo.create(flight)
        
        flight.flight_status = FlightStatus.DEPARTED
        result = repo.update(flight)
        
        assert result.flight_status == FlightStatus.DEPARTED
    
    def test_update_flight_all_fields(self, test_db, flight_dependencies):
        #Test updating all flight fields.#
        repo = FlightRepository(test_db)
        flight_id = uuid.uuid4()
        flight = Flight(
            flight_id=flight_id,
            route_id=flight_dependencies["route"].route_id,
            aircraft_id=flight_dependencies["aircraft"].aircraft_id,
            flight_status=FlightStatus.SCHEDULED,
            dept_time=datetime(2026, 2, 12, 10, 0),
            arrival_time=datetime(2026, 2, 12, 14, 0)
        )
        repo.create(flight)
        
        new_time = datetime(2026, 2, 13, 15, 0)
        flight.flight_status = FlightStatus.EN_ROUTE
        flight.dept_time = new_time
        flight.arrival_time = new_time
        result = repo.update(flight)
        
        assert result.flight_status == FlightStatus.EN_ROUTE
        assert result.dept_time == new_time
    
    def test_update_nonexistent_flight(self, test_db):
        #Test updating a nonexistent flight raises ValueError.#
        repo = FlightRepository(test_db)
        flight = Flight(
            flight_id=uuid.uuid4(),
            route_id=uuid.uuid4(),
            aircraft_id=uuid.uuid4(),
            flight_status=FlightStatus.SCHEDULED,
            dept_time=datetime.now(),
            arrival_time=datetime.now()
        )
        
        with pytest.raises(ValueError, match="Flight not found"):
            repo.update(flight)
    
    def test_delete_flight(self, test_db, flight_dependencies):
        #Test deleting a flight.#
        repo = FlightRepository(test_db)
        flight_id = uuid.uuid4()
        flight = Flight(
            flight_id=flight_id,
            route_id=flight_dependencies["route"].route_id,
            aircraft_id=flight_dependencies["aircraft"].aircraft_id,
            flight_status=FlightStatus.SCHEDULED,
            dept_time=datetime(2026, 2, 12, 10, 0),
            arrival_time=datetime(2026, 2, 12, 14, 0)
        )
        repo.create(flight)
        
        repo.delete(flight_id)
        
        result = repo.get(flight_id)
        assert result is None
    
    def test_delete_nonexistent_flight(self, test_db):
        #Test deleting a nonexistent flight raises ValueError.#
        repo = FlightRepository(test_db)
        
        with pytest.raises(ValueError, match="Flight not found"):
            repo.delete(uuid.uuid4())


# ============================================================================
# In-Flight Employee Repository Tests
# ============================================================================

class TestInFlightEmployeeRepository:
    #Tests for InFlightEmployeeRepository CRUD operations.#
    
    @pytest.fixture
    def airline_dependency(self, test_db):
        #Create an airline for employee tests.#
        airline = Airline(airline_designator="AA", name="American Airlines")
        test_db.add(airline)
        test_db.commit()
        return airline
    
    def test_create_employee(self, test_db, airline_dependency):
        #Test creating a new employee.#
        repo = InFlightEmployeeRepository(test_db)
        employee = InFlightEmployee(
            employee_id=uuid.uuid4(),
            airline_designator="AA",
            f_name="John",
            l_name="Doe",
            position=EmployeePosition.CAPTAIN,
            status="Active",
            supervised=None
        )
        
        result = repo.create(employee)
        
        assert result.f_name == "John"
        assert result.l_name == "Doe"
        assert result.position == EmployeePosition.CAPTAIN
    
    def test_create_multiple_employees(self, test_db, airline_dependency):
        #Test creating multiple employees.#
        repo = InFlightEmployeeRepository(test_db)
        positions = [EmployeePosition.CAPTAIN, EmployeePosition.COPILOT, EmployeePosition.FLIGHT_ATTENDANT]
        
        for i, position in enumerate(positions):
            employee = InFlightEmployee(
                employee_id=uuid.uuid4(),
                airline_designator="AA",
                f_name=f"Employee{i}",
                l_name=f"Last{i}",
                position=position,
                status="Active",
                supervised=None
            )
            repo.create(employee)
        
        assert len(repo.list_all()) == 3
    
    def test_get_employee_by_id(self, test_db, airline_dependency):
        #Test retrieving an employee by ID.#
        repo = InFlightEmployeeRepository(test_db)
        employee_id = uuid.uuid4()
        employee = InFlightEmployee(
            employee_id=employee_id,
            airline_designator="AA",
            f_name="John",
            l_name="Doe",
            position=EmployeePosition.CAPTAIN,
            status="Active",
            supervised=None
        )
        repo.create(employee)
        
        result = repo.get(employee_id)
        
        assert result is not None
        assert result.employee_id == employee_id
        assert result.f_name == "John"
    
    def test_get_nonexistent_employee(self, test_db):
        #Test retrieving a nonexistent employee returns None.#
        repo = InFlightEmployeeRepository(test_db)
        
        result = repo.get(uuid.uuid4())
        
        assert result is None
    
    def test_list_all_employees(self, test_db, airline_dependency):
        #Test listing all employees.#
        repo = InFlightEmployeeRepository(test_db)
        for i in range(3):
            employee = InFlightEmployee(
                employee_id=uuid.uuid4(),
                airline_designator="AA",
                f_name=f"Employee{i}",
                l_name=f"Last{i}",
                position=EmployeePosition.FLIGHT_ATTENDANT,
                status="Active",
                supervised=None
            )
            repo.create(employee)
        
        result = repo.list_all()
        
        assert len(result) == 3
    
    def test_list_all_employees_empty(self, test_db):
        #Test listing all employees when none exist.#
        repo = InFlightEmployeeRepository(test_db)
        
        result = repo.list_all()
        
        assert result == []
    
    def test_update_employee(self, test_db, airline_dependency):
        #Test updating an employee.#
        repo = InFlightEmployeeRepository(test_db)
        employee_id = uuid.uuid4()
        employee = InFlightEmployee(
            employee_id=employee_id,
            airline_designator="AA",
            f_name="John",
            l_name="Doe",
            position=EmployeePosition.CAPTAIN,
            status="Active",
            supervised=None
        )
        repo.create(employee)
        
        employee.f_name = "Jane"
        employee.position = EmployeePosition.COPILOT
        result = repo.update(employee)
        
        assert result.f_name == "Jane"
        assert result.position == EmployeePosition.COPILOT
    
    def test_update_employee_all_fields(self, test_db, airline_dependency):
        #Test updating all employee fields.#
        repo = InFlightEmployeeRepository(test_db)
        employee_id = uuid.uuid4()
        supervised_id = uuid.uuid4()
        
        employee = InFlightEmployee(
            employee_id=employee_id,
            airline_designator="AA",
            f_name="John",
            l_name="Doe",
            position=EmployeePosition.CAPTAIN,
            status="Active",
            supervised=None
        )
        repo.create(employee)
        
        employee.f_name = "Jane"
        employee.l_name = "Smith"
        employee.position = EmployeePosition.MANAGER
        employee.status = "Inactive"
        employee.supervised = supervised_id
        result = repo.update(employee)
        
        assert result.f_name == "Jane"
        assert result.l_name == "Smith"
        assert result.position == EmployeePosition.MANAGER
        assert result.status == "Inactive"
        assert result.supervised == supervised_id
    
    def test_update_nonexistent_employee(self, test_db):
        #Test updating a nonexistent employee raises ValueError.#
        repo = InFlightEmployeeRepository(test_db)
        employee = InFlightEmployee(
            employee_id=uuid.uuid4(),
            airline_designator="AA",
            f_name="John",
            l_name="Doe",
            position=EmployeePosition.CAPTAIN,
            status="Active",
            supervised=None
        )
        
        with pytest.raises(ValueError, match="Employee not found"):
            repo.update(employee)
    
    def test_delete_employee(self, test_db, airline_dependency):
        #Test deleting an employee.#
        repo = InFlightEmployeeRepository(test_db)
        employee_id = uuid.uuid4()
        employee = InFlightEmployee(
            employee_id=employee_id,
            airline_designator="AA",
            f_name="John",
            l_name="Doe",
            position=EmployeePosition.CAPTAIN,
            status="Active",
            supervised=None
        )
        repo.create(employee)
        
        repo.delete(employee_id)
        
        result = repo.get(employee_id)
        assert result is None
    
    def test_delete_nonexistent_employee(self, test_db):
        #Test deleting a nonexistent employee raises ValueError.#
        repo = InFlightEmployeeRepository(test_db)
        
        with pytest.raises(ValueError, match="Employee not found"):
            repo.delete(uuid.uuid4())


# ============================================================================
# Flight Crew Repository Tests
# ============================================================================

class TestFlightCrewRepository:
    #Tests for FlightCrewRepository CRUD operations.#
    
    @pytest.fixture
    def flight_crew_dependencies(self, test_db):
        #Create dependencies for flight crew tests.#
        # Create airline
        airline = Airline(airline_designator="AA", name="American Airlines")
        test_db.add(airline)
        
        # Create airports
        airports = [
            Airport(airport_code="JFK", airport_name="JFK", airport_country="USA",
                   airport_city="New York", airport_address="Jamaica"),
            Airport(airport_code="LAX", airport_name="LAX", airport_country="USA",
                   airport_city="Los Angeles", airport_address="El Segundo"),
        ]
        for airport in airports:
            test_db.add(airport)
        
        # Create route
        route = Route(
            route_id=uuid.uuid4(),
            origin_airport_code="JFK",
            destination_airport_code="LAX"
        )
        test_db.add(route)
        
        # Create aircraft
        aircraft = Aircraft(
            aircraft_id=uuid.uuid4(),
            airline_designator="AA",
            manufacturer="Boeing",
            aircraft_model="747"
        )
        test_db.add(aircraft)
        
        # Create flight
        flight = Flight(
            flight_id=uuid.uuid4(),
            route_id=route.route_id,
            aircraft_id=aircraft.aircraft_id,
            flight_status=FlightStatus.SCHEDULED,
            dept_time=datetime(2026, 2, 12, 10, 0),
            arrival_time=datetime(2026, 2, 12, 14, 0)
        )
        test_db.add(flight)
        
        # Create employee
        employee = InFlightEmployee(
            employee_id=uuid.uuid4(),
            airline_designator="AA",
            f_name="John",
            l_name="Doe",
            position=EmployeePosition.CAPTAIN,
            status="Active",
            supervised=None
        )
        test_db.add(employee)
        
        test_db.commit()
        return {
            "flight": flight,
            "employee": employee
        }
    
    def test_create_flight_crew(self, test_db, flight_crew_dependencies):
        #Test creating a new flight crew assignment.#
        repo = FlightCrewRepository(test_db)
        flight_crew = FlightCrew(
            flight_id=flight_crew_dependencies["flight"].flight_id,
            employee_id=flight_crew_dependencies["employee"].employee_id
        )
        
        result = repo.create(flight_crew)
        
        assert result.flight_id == flight_crew_dependencies["flight"].flight_id
        assert result.employee_id == flight_crew_dependencies["employee"].employee_id
    
    def test_create_multiple_flight_crews(self, test_db, flight_crew_dependencies):
        #Test creating multiple flight crew assignments.#
        repo = FlightCrewRepository(test_db)
        
        # Create additional employees
        for i in range(2):
            employee = InFlightEmployee(
                employee_id=uuid.uuid4(),
                airline_designator="AA",
                f_name=f"Employee{i}",
                l_name=f"Last{i}",
                position=EmployeePosition.FLIGHT_ATTENDANT,
                status="Active",
                supervised=None
            )
            test_db.add(employee)
        
        test_db.commit()
        employees = test_db.query(InFlightEmployee).all()
        
        for employee in employees:
            flight_crew = FlightCrew(
                flight_id=flight_crew_dependencies["flight"].flight_id,
                employee_id=employee.employee_id
            )
            repo.create(flight_crew)
        
        assert len(repo.list_all()) == 3
    
    def test_get_flight_crew(self, test_db, flight_crew_dependencies):
        #Test retrieving flight crew by flight and employee IDs.#
        repo = FlightCrewRepository(test_db)
        flight_id = flight_crew_dependencies["flight"].flight_id
        employee_id = flight_crew_dependencies["employee"].employee_id
        
        flight_crew = FlightCrew(flight_id=flight_id, employee_id=employee_id)
        repo.create(flight_crew)
        
        result = repo.get(flight_id, employee_id)
        
        assert result is not None
        assert result.flight_id == flight_id
        assert result.employee_id == employee_id
    
    def test_get_nonexistent_flight_crew(self, test_db):
        #Test retrieving a nonexistent flight crew returns None.#
        repo = FlightCrewRepository(test_db)
        
        result = repo.get(uuid.uuid4(), uuid.uuid4())
        
        assert result is None
    
    def test_list_all_flight_crews(self, test_db, flight_crew_dependencies):
        #Test listing all flight crew assignments.#
        repo = FlightCrewRepository(test_db)
        
        # Create additional employees and crews
        for i in range(2):
            employee = InFlightEmployee(
                employee_id=uuid.uuid4(),
                airline_designator="AA",
                f_name=f"Employee{i}",
                l_name=f"Last{i}",
                position=EmployeePosition.FLIGHT_ATTENDANT,
                status="Active",
                supervised=None
            )
            test_db.add(employee)
        
        test_db.commit()
        
        repo.create(FlightCrew(
            flight_id=flight_crew_dependencies["flight"].flight_id,
            employee_id=flight_crew_dependencies["employee"].employee_id
        ))
        
        employees = test_db.query(InFlightEmployee).all()
        for employee in employees[1:]:
            flight_crew = FlightCrew(
                flight_id=flight_crew_dependencies["flight"].flight_id,
                employee_id=employee.employee_id
            )
            repo.create(flight_crew)
        
        result = repo.list_all()
        
        assert len(result) >= 1
    
    def test_list_all_flight_crews_empty(self, test_db):
        #Test listing all flight crews when none exist.#
        repo = FlightCrewRepository(test_db)
        
        result = repo.list_all()
        
        assert result == []
    
    def test_update_flight_crew(self, test_db, flight_crew_dependencies):
        #Test updating a flight crew assignment.#
        repo = FlightCrewRepository(test_db)
        flight_id = flight_crew_dependencies["flight"].flight_id
        employee_id = flight_crew_dependencies["employee"].employee_id
        
        flight_crew = FlightCrew(flight_id=flight_id, employee_id=employee_id)
        repo.create(flight_crew)
        
        # Update should return the existing record
        result = repo.update(flight_crew)
        
        assert result.flight_id == flight_id
        assert result.employee_id == employee_id
    
    def test_update_nonexistent_flight_crew(self, test_db):
        #Test updating a nonexistent flight crew raises ValueError.#
        repo = FlightCrewRepository(test_db)
        flight_crew = FlightCrew(
            flight_id=uuid.uuid4(),
            employee_id=uuid.uuid4()
        )
        
        with pytest.raises(ValueError, match="Flight Crew assignment not found"):
            repo.update(flight_crew)
    
    def test_delete_flight_crew(self, test_db, flight_crew_dependencies):
        #Test deleting a flight crew assignment.#
        repo = FlightCrewRepository(test_db)
        flight_id = flight_crew_dependencies["flight"].flight_id
        employee_id = flight_crew_dependencies["employee"].employee_id
        
        flight_crew = FlightCrew(flight_id=flight_id, employee_id=employee_id)
        repo.create(flight_crew)
        
        repo.delete(flight_id, employee_id)
        
        result = repo.get(flight_id, employee_id)
        assert result is None
    
    def test_delete_nonexistent_flight_crew(self, test_db):
        #Test deleting a nonexistent flight crew raises ValueError.#
        repo = FlightCrewRepository(test_db)
        
        with pytest.raises(ValueError, match="Flight Crew assignment not found"):
            repo.delete(uuid.uuid4(), uuid.uuid4())


# ============================================================================
# Operates Repository Tests
# ============================================================================

class TestOperatesRepository:
    #Tests for OperatesRepository CRUD operations.#
    
    @pytest.fixture
    def operates_dependencies(self, test_db):
        #Create dependencies for operates tests.#
        # Create airline
        airline = Airline(airline_designator="AA", name="American Airlines")
        test_db.add(airline)
        
        # Create airport
        airport = Airport(
            airport_code="JFK",
            airport_name="JFK",
            airport_country="USA",
            airport_city="New York",
            airport_address="Jamaica"
        )
        test_db.add(airport)
        
        test_db.commit()
        return {
            "airline": airline,
            "airport": airport
        }
    
    def test_create_operates(self, test_db, operates_dependencies):
        #Test creating a new operates record.#
        repo = OperatesRepository(test_db)
        operates = Operates(
            airport_code="JFK",
            airline_designator="AA"
        )
        
        result = repo.create(operates)
        
        assert result.airport_code == "JFK"
        assert result.airline_designator == "AA"
    
    def test_create_multiple_operates(self, test_db, operates_dependencies):
        #Test creating multiple operates records.#
        repo = OperatesRepository(test_db)
        
        # Create additional airports
        for i in range(2):
            airport = Airport(
                airport_code=f"AP{i}",
                airport_name=f"Airport{i}",
                airport_country="USA",
                airport_city=f"City{i}",
                airport_address=f"Address{i}"
            )
            test_db.add(airport)
        
        test_db.commit()
        
        airports = ["JFK", "AP0", "AP1"]
        for airport_code in airports:
            operates = Operates(
                airport_code=airport_code,
                airline_designator="AA"
            )
            repo.create(operates)
        
        assert len(repo.list_all()) == 3
    
    def test_get_operates(self, test_db, operates_dependencies):
        #Test retrieving operates record by airport code and airline designator.#
        repo = OperatesRepository(test_db)
        operates = Operates(airport_code="JFK", airline_designator="AA")
        repo.create(operates)
        
        result = repo.get("JFK", "AA")
        
        assert result is not None
        assert result.airport_code == "JFK"
        assert result.airline_designator == "AA"
    
    def test_get_nonexistent_operates(self, test_db):
        #Test retrieving a nonexistent operates record returns None.#
        repo = OperatesRepository(test_db)
        
        result = repo.get("XXX", "ZZ")
        
        assert result is None
    
    def test_list_all_operates(self, test_db, operates_dependencies):
        #Test listing all operates records.#
        repo = OperatesRepository(test_db)
        
        # Create additional airports and operates records
        for i in range(2):
            airport = Airport(
                airport_code=f"AP{i}",
                airport_name=f"Airport{i}",
                airport_country="USA",
                airport_city=f"City{i}",
                airport_address=f"Address{i}"
            )
            test_db.add(airport)
        
        test_db.commit()
        
        for airport_code in ["JFK", "AP0", "AP1"]:
            operates = Operates(
                airport_code=airport_code,
                airline_designator="AA"
            )
            repo.create(operates)
        
        result = repo.list_all()
        
        assert len(result) == 3
    
    def test_list_all_operates_empty(self, test_db):
        #Test listing all operates records when none exist.#
        repo = OperatesRepository(test_db)
        
        result = repo.list_all()
        
        assert result == []
    
    def test_update_operates(self, test_db, operates_dependencies):
        #Test updating an operates record.#
        repo = OperatesRepository(test_db)
        operates = Operates(airport_code="JFK", airline_designator="AA")
        repo.create(operates)
        
        # Update should return the existing record
        result = repo.update(operates)
        
        assert result.airport_code == "JFK"
        assert result.airline_designator == "AA"
    
    def test_update_nonexistent_operates(self, test_db):
        #Test updating a nonexistent operates record raises ValueError.#
        repo = OperatesRepository(test_db)
        operates = Operates(airport_code="XXX", airline_designator="ZZ")
        
        with pytest.raises(ValueError, match="Operates record not found"):
            repo.update(operates)
    
    def test_delete_operates(self, test_db, operates_dependencies):
        #Test deleting an operates record.#
        repo = OperatesRepository(test_db)
        operates = Operates(airport_code="JFK", airline_designator="AA")
        repo.create(operates)
        
        repo.delete("JFK", "AA")
        
        result = repo.get("JFK", "AA")
        assert result is None
    
    def test_delete_nonexistent_operates(self, test_db):
        #Test deleting a nonexistent operates record raises ValueError.#
        repo = OperatesRepository(test_db)
        
        with pytest.raises(ValueError, match="Operates record not found"):
            repo.delete("XXX", "ZZ")
"""