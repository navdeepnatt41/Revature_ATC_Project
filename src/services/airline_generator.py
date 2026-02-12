import json
from src.domain.airline import Airline


def generate_airlines() -> list[Airline]:
    with open("registry.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        return [
            Airline(airline_designator=code, name=name)
            for code, name in data["airlines"].items()
        ]


if __name__ == "main":
    breakpoint()
