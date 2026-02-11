import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from src.base import Base

class Route(Base):
    __tablename__ = "route"
    
    route_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    destination_airport_code = Column(String, ForeignKey("airport.airport_code"))
    origin_airport_code = Column(String, ForeignKey("airport.airport_code"))