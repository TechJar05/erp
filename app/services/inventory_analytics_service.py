from sqlalchemy.orm import Session
from app.models import ContextSession, DataContext
from app.analytics.metrics import INVENTORY_METRICS
from sqlalchemy import text

class InventoryAnalyticsService:

    @staticmethod
    def run_metric(
        db: Session,
        context_session_id,
        metric_name: str
    ):
        session = (
            db.query(ContextSession)
            .filter(ContextSession.id == context_session_id)
            .first()
        )

        if not session:
            raise ValueError("Invalid context session")

        context = (
            db.query(DataContext)
            .filter(DataContext.id == session.data_context_id)
            .first()
        )

        if not context:
            raise ValueError("Invalid data context")

        if metric_name not in context.allowed_metrics:
            raise PermissionError("Metric not allowed in this context")

        if metric_name not in INVENTORY_METRICS:
            raise ValueError("Metric not implemented")

        sql = INVENTORY_METRICS[metric_name]["sql"]
        result = db.execute(text(sql)).mappings().all()
        return result
