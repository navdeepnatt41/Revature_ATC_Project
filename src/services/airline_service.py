from src.repositories.airline_repository import AirlineRepository
from src.domain.airline import Airline

class AirlineService:
    def __init__(self, airline_repository: AirlineRepository):
        self.airline_repository = airline_repository
    
    def get_airline_records(self) -> list[Airline]:
        return self.airline_repository.get_airline_records()
    