import random
from uuid import UUID

from domain.flight_crew import FlightCrew


def generate_flight_crew(
    flight_ids: list[UUID], employee_ids: list[UUID], crew_per_flight: int = 8
) -> list[FlightCrew]:
    assignments: list[FlightCrew] = []
    # cant build anything if inputs are empty or crew size is invalid
    if not flight_ids or not employee_ids or crew_per_flight <= 0:
        return assignments

    for flight_id in flight_ids:
        # choosing a crew for this flight
        if crew_per_flight <= len(employee_ids):
            # sample without duplicates when there are enough employees.
            selected_ids = random.sample(employee_ids, crew_per_flight)
        else:
            # allow repeats when crew size is larger than available employees.
            selected_ids = [random.choice(employee_ids) for _ in range(crew_per_flight)]

        for employee_id in selected_ids:
            # creating assignments (flight_id + employee_id).
            assignments.append(
                FlightCrew(
                    flight_id=flight_id,
                    employee_id=employee_id,
                )
            )

    return assignments
