import random
from datetime import datetime, timedelta, timezone
from uuid import UUID

from src.domain.flight import Flight, FlightStatus

def generate_flights(
    route_ids: list[UUID],
    aircraft_ids: list[UUID],
    flights_per_route: int = 3,
    start_time: datetime | None = None,
    max_days_ahead: int = 14,
    ) -> list[Flight]:

    flights: list[Flight] = []

    base = start_time or datetime.now(timezone.utc)
    statuses = [
        FlightStatus.SCHEDULED,
        FlightStatus.BOARDING,
        FlightStatus.DEPARTED,
        FlightStatus.EN_ROUTE,
        FlightStatus.ARRIVED,
        FlightStatus.COMPLETED,
        FlightStatus.CANCELED,
    ]
    weights = [60, 10, 8, 8, 6, 20, 2]

    for route_id in route_ids:
        for _ in range(flights_per_route):
            # random aircraft
            aircraft_id = random.choice(aircraft_ids) # not sure yet if its model or aircraft if itself

            # random departure
            minutes_ahead = random.randint(0, max_days_ahead * 24 * 60) # within next max_days_ahead
            dept_time = base + timedelta(minutes=minutes_ahead)

            # random flight duration
            duration_minutes = random.randint(60, 360)
            arrival_time = dept_time + timedelta(minutes=duration_minutes)

            flight_status = random.choices(statuses, weights=weights, k=1)[0]

            flights.append(
                Flight(
                    route_id=route_id,
                    aircraft_id=aircraft_id,
                    dept_time=dept_time,
                    arrival_time=arrival_time,
                    flight_status=flight_status,
                )
            )



    return flights

