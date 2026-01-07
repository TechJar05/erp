from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.context_guard import require_context_session
from app.services.automation_service import AutomationService

router = APIRouter(prefix="/automation", tags=["Automation"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/evaluate")
def evaluate_automation(
    context_session = Depends(require_context_session),
    db: Session = Depends(get_db)
):
    return AutomationService.evaluate(db, context_session.id)
