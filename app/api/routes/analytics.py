from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.context_guard import require_context_session
from app.services.inventory_analytics_service import InventoryAnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/inventory")
def inventory_analytics(
    metric: str,
    context_session=Depends(require_context_session),
    db: Session = Depends(get_db)
):
    try:
        return InventoryAnalyticsService.run_metric(
            db=db,
            context_session_id=context_session.id,
            metric_name=metric
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
