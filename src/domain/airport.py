from dataclasses import dataclass
from sqlalchemy import Column, String
from src.base import Base

@dataclass
class Airport(Base):
  __tablename__ = 'airport'

  airport_code = Column(String, primary_key= True)
  airport_name = Column(String, nullable= False)
  airport_country = Column(String, nullable= False)
  airport_city = Column(String, nullable= False)
  airport_address = Column(String, nullable= False)
  longitude = Column(String, nullable= False)
  latitude = Column(String, nullable= False)
