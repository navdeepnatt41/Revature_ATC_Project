from src.domain import Airport

def generate_airports():
    airports: list[Airport] = []
    # We want to read from a file called "registry.json"
    with open("registry.json", "r") as f:
        data = f.read()
        import json
        data = json.loads(data)
        airports_data = data["airports"]
        
        # We want to iterate over the data and create Airport objects
        for a in airports_data:
            airport = Airport(
                airport_code = a,
                airport_name = airports_data[a]["airport_name"],
                airport_country = airports_data[a]["airport_country"],
                airport_city = airports_data[a]["airport_city"],
                airport_address = airports_data[a]["airport_address"]
            )
            airports.append(airport)
    
    return airports