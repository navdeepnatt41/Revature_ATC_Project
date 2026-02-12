from sqlalchemy.orm import Session
from src.domain.airline import Airline

class AirportRepository():
    def __init__(self, session: Session):
        self.session = session
    
    def get_airline_records(self) -> list[Airline]:
        return self.session.query(Airline).all()