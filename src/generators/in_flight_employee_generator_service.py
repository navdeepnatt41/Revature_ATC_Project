import random
from faker import Faker
from domain.in_flight_employee import InFlightEmployee, EmployeePosition

fake = Faker()


def generate_inflight_employee(
    iata_codes: list[str], supervisor_id=None
) -> list[InFlightEmployee]:
    crew_members: list[InFlightEmployee] = []
    for _ in range(10):
        crew_member = InFlightEmployee(
            # pick a valid airline IATA code for this employee.
            IATA_code=random.choice(iata_codes),
            f_name=fake.first_name(),
            l_name=fake.last_name(),
            position=random.choice(list(EmployeePosition)),
            status=random.choice(["Active", "Inactive", "Terminated"]),
            # supervisor_id can be None but set to another employee's UUID when available
            supervised=supervisor_id,
        )
        crew_members.append(crew_member)
    return crew_members
