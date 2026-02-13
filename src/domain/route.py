import uuid
from math import radians, cos, sin, asin, sqrt
from sqlalchemy import Column, String, ForeignKey, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.base import Base


class Route(Base):
    __tablename__ = "route"
    
    route_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    destination_airport_code = Column(String, ForeignKey("airport.airport_code"))
    origin_airport_code = Column(String, ForeignKey("airport.airport_code"))
    
    # Relationships to load airport objects
    origin_airport = relationship("Airport", foreign_keys=[origin_airport_code], primaryjoin="Route.origin_airport_code==Airport.airport_code")
    destination_airport = relationship("Airport", foreign_keys=[destination_airport_code], primaryjoin="Route.destination_airport_code==Airport.airport_code")

   