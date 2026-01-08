from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.context_guard import require_context_session
from app.services.production_planning_analytics_service import (
    ProductionPlanningAnalyticsService
)

router = APIRouter(
    prefix="/analytics/production-planning",
    tags=["Production Planning Analytics"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("")
def production_planning_dashboard(
    context_session = Depends(require_context_session),
    db: Session = Depends(get_db)
):
    return ProductionPlanningAnalyticsService.get_dashboard_data(db)
