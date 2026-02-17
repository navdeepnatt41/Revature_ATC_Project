import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from uuid import uuid4
from datetime import datetime

# Import the app and dependency getters
from src.main import (
    app, 
    get_flight_service, 
    get_route_service, 
    get_aircraft_service,
    get_in_flight_employee_service
)

client = TestClient(app)

# --- FIXTURES ---

@pytest.fixture
def mock_flight_svc():
    svc = MagicMock()
    app.dependency_overrides[get_flight_service] = lambda: svc
    yield svc
    app.dependency_overrides.clear()

@pytest.fixture
def mock_route_svc():
    svc = MagicMock()
    app.dependency_overrides[get_route_service] = lambda: svc
    yield svc
    app.dependency_overrides.clear()

@pytest.fixture
def mock_aircraft_svc():
    svc = MagicMock()
    app.dependency_overrides[get_aircraft_service] = lambda: svc
    yield svc
    app.dependency_overrides.clear()

# Helper for AircraftBase responses
def mock_aircraft_base_data(aircraft_id=None):
    return {
        "manufacturer": "Boeing",
        "aircraft_model": "737-800",
        "current_distance": 100.0,
        "maintenance_interval": 5000.0,
        "aircraft_status": "AVAILABLE",
        "aircraft_location": "JFK"
    }

# --- FLIGHT ENDPOINTS (POST/PATCH) ---

def test_schedule_flight(mock_flight_svc):
    flight_id = uuid4()
    mock_flight_svc.schedule_flight.return_value = {
        "flight_id": flight_id,
        "route_id": uuid4(),
        "flight_status": "SCHEDULED",
        "aircraft_id": uuid4(),
        "departure_time": datetime.now(),
        "arrival_time": datetime.now()
    }
    payload = {
        "route_id": str(uuid4()),
        "aircraft_id": str(uuid4()),
        "departure_time": "2026-02-17T10:00:00",
        "arrival_time": "2026-02-17T12:00:00"
    }
    response = client.post("/flight/schedule/", json=payload)
    assert response.status_code == 200
    assert response.json()["flight_id"] == str(flight_id)

def test_schedule_flight_crew(mock_flight_svc):
    target_flight_id = uuid4()
    mock_flight_svc.schedule_employees.return_value = [
        {"flight_id": target_flight_id, "employee_id": str(uuid4()), "name": "Jane Doe", "position": "PILOT"}
    ]
    payload = {
        "flight_id": str(uuid4()),
        "employee_ids": [str(uuid4()), str(uuid4())]
    }
    response = client.post("/flight/crew", json=payload)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_launch_flight(mock_flight_svc):
    flight_id = uuid4()
    mock_flight_svc.launch_flight.return_value = {
        "flight_id": flight_id,
        "route_id": uuid4(),
        "flight_status": "IN-FLIGHT",
        "aircraft_id": uuid4()
    }
    response = client.patch("/flight/launch/", json={"flight_id": str(flight_id)})
    assert response.status_code == 200
    assert response.json()["flight_status"] == "IN-FLIGHT"

def test_land_flight(mock_flight_svc):
    # This endpoint returns AircraftBase
    mock_flight_svc.confirm_flight_landed.return_value = mock_aircraft_base_data()
    response = client.patch("/flight/land/", json={"flight_id": str(uuid4())})
    assert response.status_code == 200
    assert response.json()["aircraft_location"] == "JFK"

# --- ROUTE ENDPOINTS (POST/DELETE) ---

def test_create_route(mock_route_svc):
    route_id = uuid4()
    mock_route_svc.route_create.return_value = {
        "route_id": route_id,
        "origin_airport_code": "LAX",
        "destination_airport_code": "SFO"
    }
    payload = {"origin_airport_code": "LAX", "destination_airport_code": "SFO"}
    response = client.post("/route/", json=payload)
    assert response.status_code == 200
    assert response.json()["route_id"] == str(route_id)

def test_delete_route_success(mock_route_svc):
    mock_route_svc.route_delete.return_value = {"message": "Route deleted"}
    payload = {
        "route_id": str(uuid4()),
        "authorization_code": "authorized"
    }
    response = client.request("DELETE", "/route", json=payload)
    assert response.status_code == 200

def test_delete_route_unauthorized(mock_route_svc):
    payload = {
        "route_id": str(uuid4()),
        "authorization_code": "wrong-code"
    }
    response = client.request("DELETE", "/route", json=payload)
    assert response.status_code == 400
    assert "Permission denied" in response.json()["detail"]

# --- AIRCRAFT ENDPOINTS (PATCH) ---

def test_fix_aircraft(mock_aircraft_svc):
    mock_aircraft_svc.repair_aircraft.return_value = mock_aircraft_base_data()
    payload = {"aircraft_id": str(uuid4())}
    response = client.patch("/aircraft/fix/", json=payload)
    assert response.status_code == 200
    assert response.json()["aircraft_status"] == "AVAILABLE"

def test_schedule_repair_aircraft(mock_aircraft_svc):
    data = mock_aircraft_base_data()
    data["aircraft_status"] = "MAINTENANCE"
    mock_aircraft_svc.schedule_repair_aircraft.return_value = data
    
    payload = {"aircraft_id": str(uuid4())}
    response = client.patch("/aircraft/schedule_repair/", json=payload)
    assert response.status_code == 200
    assert response.json()["aircraft_status"] == "MAINTENANCE"