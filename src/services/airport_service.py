from repositories.airport_repository import AirportRepository
from src.domain.airline import Airline

class AirportService:
    def __init__(self, airline_repository: AirportRepository):
        self.airline_repository = airline_repository
    
    def get_airline_records(self) -> list[Airline]:
        return self.airline_repository.get_airline_records()
    