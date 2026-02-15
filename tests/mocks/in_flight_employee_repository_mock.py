from typing import Optional
from uuid import UUID
from src.domain.in_flight_employee import InFlightEmployee, InFlightStatus


class MockInFlightEmployeeRepository:
    def create(self, employee: InFlightEmployee) -> InFlightEmployee:
        return employee
    
    def get(self, employee_id: UUID) -> Optional[InFlightEmployee]: #returning one employee
        return InFlightEmployee(employee_id = employee_id, first_name = 'test', last_name = 'test', position = 'CAPTAIN', employee_status = 'AVAILABLE', supervisor = None, employee_location = 'JFK')
    
    def find_by_first_and_last(self, first: str, last: str) -> Optional[list[InFlightEmployee]]:
        return [InFlightEmployee(employee_id = 'aaaaaaa1-aaaa-aaaa-aaaa-aaaaaaaaaaa1', first_name = first, last_name = last, position = 'CAPTAIN', employee_status = 'AVAILABLE', supervisor = None, employee_location = 'JFK')]
    
    def find_by_first(self, first: str) -> list[InFlightEmployee]:
        first = first.strip()
        return [InFlightEmployee(employee_id = 'aaaaaaa1-aaaa-aaaa-aaaa-aaaaaaaaaaa1', first_name = first, last_name = 'test', position = 'CAPTAIN', employee_status = 'AVAILABLE', supervisor = None, employee_location = 'JFK')]
    

    def list_all(self) -> list[InFlightEmployee]:
        return [
            InFlightEmployee(employee_id = 'aaaaaaa1-aaaa-aaaa-aaaa-aaaaaaaaaaa1', first_name = 'test', last_name = 'test2', position = 'CAPTAIN', employee_status = 'AVAILABLE', supervisor = None, employee_location = 'JFK'),
            InFlightEmployee(employee_id = 'aaaaaaa2-aaaa-aaaa-aaaa-aaaaaaaaaaa2', first_name = 'test2', last_name = 'test2', position = 'CAPTAIN', employee_status = 'AVAILABLE', supervisor = None, employee_location = 'JFK')
        ]
    

    def update_status_location(self, employee: InFlightEmployee, status: InFlightStatus, location: str) -> InFlightEmployee:
        employee.employee_status = status
        employee.employee_location = 
        return existing

    def delete(self, employee_id: UUID) -> None:
        employee = self.session.get(InFlightEmployee, employee_id)
        if employee is None:
            raise ValueError("Employee not found")
        self.session.delete(employee)
        self.session.commit()