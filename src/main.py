from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from src.services.flight_generator_service import generate_flights


app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "success", "message": "FastAPI server is live!"}

@app.post("/seed/flights")
def seed_flights():

    route_ids = [
        uuid.UUID("11111111-1111-1111-1111-111111111111"),
        uuid.UUID("22222222-2222-2222-2222-222222222222"),
        uuid.UUID("33333333-3333-3333-3333-333333333333")
        ]
    aircraft_ids = [ "AC0001", "AC0002", "AC0003", "AC0004", "AC0005", "AC0006", "AC0007", "AC0008", "AC0009"]

    flights = generate_flights(route_ids, aircraft_ids)

    return flights

print("fuhhh")