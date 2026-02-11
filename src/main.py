from src.db.deps import get_db
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends
from src.services.airline_service import AirlineService
from src.repositories.airline_repository import AirlineRepository

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "success", "message": "FastAPI server is live!"}

@app.get("/airlines")
def airlines_all(sesh: Session = Depends(get_db)):
    repo = AirlineRepository(sesh)
    srv = AirlineService(repo)
    return srv.get_airline_records()