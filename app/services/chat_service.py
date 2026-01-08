from sqlalchemy.orm import Session
from app.models import ContextSession, DataContext
from app.chat.metric_resolver import resolve_metric
from app.services.inventory_analytics_service import InventoryAnalyticsService
from app.services.sales_analytics_service import SalesAnalyticsService
from app.chat.ai_intent_resolver import ai_resolve_intent


class ChatService:

    @staticmethod
    def handle_message(
        db: Session,
        context_session_id,
        message: str
    ):
        session = (
            db.query(ContextSession)
            .filter(ContextSession.id == context_session_id)
            .first()
        )

        if not session:
            return {"error": "Invalid session"}

        context = (
            db.query(DataContext)
            .filter(DataContext.id == session.data_context_id)
            .first()
        )

        # derive domain from primary_table
        if context.primary_table == "inventory_balance":
            domain = "inventory"
        elif context.primary_table == "sales_order":
            domain = "sales"
        else:
            return {"error": "Unsupported context"}

        metric = resolve_metric(domain, message)

        if not metric:
            return {
                "message": "I can help with these metrics:",
                "allowed_metrics": context.allowed_metrics
            }

        if context.name.lower().startswith("inventory"):
            data = InventoryAnalyticsService.run_metric(
                db, context_session_id, metric
            )
        elif context.name.lower().startswith("sales"):
            data = SalesAnalyticsService.run_metric(
                db, context_session_id, metric
            )
        else:
            return {"error": "Context not supported yet"}

        return {
            "metric": metric,
            "data": data
        }
