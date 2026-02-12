from src.db.deps import get_db
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends
from services.airport_service import AirportService
from repositories.airport_repository import AirportRepository

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "success", "message": "FastAPI server is live!"}

@app.get("/airlines")
def airlines_all(sesh: Session = Depends(get_db)):
    repo = AirportRepository(sesh)
    srv = AirportService(repo)
    return srv.get_airline_records()