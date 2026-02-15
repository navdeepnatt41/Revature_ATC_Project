from typing import Optional
from src.domain.airport import Airport

class MockAirportRepository:
    def create(self, airport: Airport) -> Airport:
        return airport
    
    def get(self, airport_code: str) -> Optional[Airport]: 
        return Airport(airport_code = airport_code, airport_name = 'test', airport_country = 'test', airport_city = 'test', airport_address = 'test', longitude = '0', latitude = '0')

    def list_all(self) -> list[Airport]:
        return [ Airport(airport_code = 'ts1', airport_name = 'test', airport_country = 'test', airport_city = 'test', airport_address = 'test', longitude = '0', latitude = '0'),
            Airport(airport_code = 'ts2', airport_name = 'test2', airport_country = 'test2', airport_city = 'test2', airport_address = 'test2', longitude = '1', latitude = '1')
        ]

    def update(self, airport: Airport) -> Airport:
        return airport

    def delete(self, airport_code: str) -> None:
        pass