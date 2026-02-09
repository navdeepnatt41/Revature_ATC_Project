import uuid
from dataclasses import dataclass
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from src.base import Base

from src.base import Base

@dataclass
class Airport(Base):
  __tablename__ = 'airport'

  airport_code = Column(UUID(as_uuid=True), primary_key= True, default=uuid.uuid4)
  airport_name = Column(String, nullable= False)
  airport_country = Column(String, nullable= False)
  airport_city = Column(String, nullable= False)
  airport_address = Column(String, nullable= False)
