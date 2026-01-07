from sqlalchemy.orm import Session
from app.models import AutomationRule, ContextSession, Task
from app.services.inventory_analytics_service import InventoryAnalyticsService
from app.services.sales_analytics_service import SalesAnalyticsService

class AutomationService:

    @staticmethod
    def evaluate(db: Session, context_session_id):
        session = (
            db.query(ContextSession)
            .filter(ContextSession.id == context_session_id)
            .first()
        )

        rules = (
            db.query(AutomationRule)
            .filter(AutomationRule.data_context_id == session.data_context_id)
            .all()
        )

        created_tasks = []

        for rule in rules:
            if rule.metric_name.startswith("below_") or rule.metric_name.startswith("stock"):
                result = InventoryAnalyticsService.run_metric(
                    db, context_session_id, rule.metric_name
                )
            else:
                result = SalesAnalyticsService.run_metric(
                    db, context_session_id, rule.metric_name
                )

            value = len(result) if isinstance(result, list) else list(result[0].values())[0]

            if AutomationService._check_condition(value, rule.condition, rule.threshold):
                task = Task(
                    task_type=rule.task_type,
                    reference_type="METRIC",
                    reference_id=None,
                    reference_name=rule.metric_name,  # ✅ correct
                    priority=rule.priority,
                    status="OPEN"
                )

                db.add(task)
                created_tasks.append(task)

        db.commit()
        return [
            {
                "id": task.id,
                "task_type": task.task_type,
                "reference_type": task.reference_type,
                "reference_name": task.reference_name,
                "priority": task.priority,
                "status": task.status
            }
            for task in created_tasks
        ]

    @staticmethod
    def _check_condition(value, condition, threshold):
        if condition == ">":
            return value > threshold
        if condition == "<":
            return value < threshold
        if condition == "=":
            return value == threshold
        return False
