from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.context_guard import require_context_session
from app.core.database import SessionLocal
from app.services.dashboard_service import DashboardService
from app.services.dashboard_ai_service import DashboardAIService

router = APIRouter(
    prefix="/dashboard/insights",
    tags=["Dashboard AI"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("")
def get_dashboard_insights(
    context_session = Depends(require_context_session),
    db: Session = Depends(get_db)   # ✅ FIXED
):
    dashboard = DashboardService.load_dashboard(db, context_session.id)

    return DashboardAIService.generate_insights(
        context_name=dashboard["context"],
        dashboard=dashboard
    )
