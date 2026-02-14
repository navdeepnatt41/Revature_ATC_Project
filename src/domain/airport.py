from dataclasses import dataclass
from sqlalchemy import Column, String
from src.base import Base

@dataclass
class Airport(Base):
  __tablename__ = 'airport'

  airport_code = Column(String, primary_key= True)
  airport_name = Column(String)
  airport_country = Column(String)
  airport_city = Column(String)
  airport_address = Column(String)
  longitude = Column(String)
  latitude = Column(String)
