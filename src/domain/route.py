import uuid
from dataclasses import dataclass
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from src.base import Base
from enum import Enum

class Route(Base):
    __tablename__ = "route"
    
    route_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    destination_airport_code = Column(String, ForeignKey("airport.airport_id"))
    origin_airport_code = Column(String, ForeignKey("airport.airport_id"))