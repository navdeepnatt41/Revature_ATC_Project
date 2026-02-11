import json
from src.domain.aircraft import Aircraft
import random

def generate_aircrafts():
    
    aircrafts: list[Aircraft] = []

    with open("registry.json", "r") as f:
        data = f.read()
        data = json.loads(data)
        aircraft_data = data["aircrafts"]
        
        for a in aircraft_data:
            aircraft = Aircraft(
                aircraft_id = a,
                airline_designator = random.choice(data["airlines"]),
                manufacturer = aircraft_data[a]['manufacturer'],
                aircraft_model = aircraft_data[a]['aircraft_model']
            )
            aircrafts.append(aircraft)
    
    return aircrafts