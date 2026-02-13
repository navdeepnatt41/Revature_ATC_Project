from typing import Optional
from uuid import UUID

from src.domain.in_flight_employee import InFlightEmployee, EmployeePosition, InFlightStatus
from src.repositories.in_flight_employee_repository_protocol import InFlightEmployeeRepositoryProtocol





class InFlightEmployeeService:
    def __init__(self, repo: InFlightEmployeeRepositoryProtocol):
        self.repo = repo

    def create(self, employee: InFlightEmployee) -> InFlightEmployee:
        self._validate_employee(employee, require_id=False)
        return self.repo.create(employee)

    def get(self, employee_id: UUID) -> Optional[InFlightEmployee]:
        return self.repo.get(employee_id)

    def listall(self) -> list[InFlightEmployee]:
        return self.repo.list_all()

    def update_status(self, employee: InFlightEmployee, status: InFlightStatus) -> InFlightEmployee:
        return self.repo.update_status(employee, status)

    def delete(self, employee_id: UUID) -> None:
        self.repo.delete(employee_id)

    def _validate_employee(self, employee: InFlightEmployee, require_id: bool) -> None:
        if require_id and not employee.employee_id.get():
            raise ValueError("employee_id is required for update")
        if not employee.IATA_code:
            raise ValueError("IATA_code is required")
        if not employee.f_name.get() or not employee.l_name.get():
            raise ValueError("first and last name are required")
        if not isinstance(employee.position, EmployeePosition):
            raise ValueError("position must be an EmployeePosition")
        if employee.status not in ALLOWED_STATUSES:
            raise ValueError("status must be one of: Available, Scheduled")
        if employee.employee_id.get() and employee.supervised == employee.employee_id.get():
            raise ValueError("employee cannot supervise themselves")