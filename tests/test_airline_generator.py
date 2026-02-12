from src.services.airline_generator import generate_airlines

def test_generate_airline():
    airlines = generate_airlines()
    print(airlines)
    for airline in airlines:
        print(f"{airline.airline_designator} : {airline.name}")
    assert airlines is not None
