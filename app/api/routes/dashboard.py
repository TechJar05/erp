from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.context_guard import require_context_session
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("")
def get_dashboard(
    context_session = Depends(require_context_session),
    db: Session = Depends(get_db)
):
    data = DashboardService.load_dashboard(db, context_session.id)
    return jsonable_encoder(data)
