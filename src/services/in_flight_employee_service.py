from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from src.domain.exceptions import (
    AppErrorException,
    EntityAlreadyExistsException,
    NotFoundException,
    PermissionDeniedException,
)

from src.domain.in_flight_employee import (
    InFlightEmployee,
    InFlightStatus
)

from src.repositories.in_flight_employee_repository_protocol import InFlightEmployeeRepositoryProtocol
from src.repositories.airport_repository_protocol import AirportRepositoryProtocol


class InFlightEmployeeService:
    def __init__(
        self,
        in_flight_employee_repo: InFlightEmployeeRepositoryProtocol,
        airport_repo: AirportRepositoryProtocol 
    ):
        self.in_flight_employee_repo = in_flight_employee_repo
        self.airport_repo = airport_repo

    ALLOWED_STATUSES = {InFlightStatus.AVAILABLE, InFlightStatus.SCHEDULED}

    def update_status(
        self, employee: InFlightEmployee, status: InFlightStatus
    ) -> InFlightEmployee:
        return self.in_flight_employee_repo.update_status_location(
            employee,
            status,
            employee.employee_location,
        )

    def get(self, employee_id: UUID) -> Optional[InFlightEmployee]:
        return self.in_flight_employee_repo.get(employee_id)

    def listall(self) -> list[InFlightEmployee]:
        return self.in_flight_employee_repo.list_all()

    def available_employees_at_airport(self, airport_code: str) -> list[InFlightEmployee]:
        if not self.airport_repo.get(airport_code):
            raise NotFoundException("Airport could not be found")
        return self.in_flight_employee_repo.available_employees_at_airport(airport_code)