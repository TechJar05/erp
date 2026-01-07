from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models import DataContext

router = APIRouter(prefix="/contexts", tags=["Contexts"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("")
def list_contexts(db: Session = Depends(get_db)):
    return db.query(DataContext).all()
