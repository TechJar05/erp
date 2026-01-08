from sqlalchemy.orm import Session
from app.models import ContextSession, MetricMetadata
from app.analytics.metric_registry import METRIC_EXECUTORS

class DashboardService:

    @staticmethod
    def load_dashboard(db: Session, context_session_id):
        session = db.query(ContextSession).filter(
            ContextSession.id == context_session_id
        ).first()

        context = session.data_context
        metadata_map = {
            m.metric_name: m
            for m in db.query(MetricMetadata)
            .filter(MetricMetadata.metric_name.in_(context.allowed_metrics))
            .all()
        }

        response = {
            "context": context.name,
            "kpis": [],
            "charts": [],
            "tables": []
        }

        for metric in context.allowed_metrics:
            executor = METRIC_EXECUTORS.get(metric)
            meta = metadata_map.get(metric)

            if not executor or not meta:
                continue

            data = executor.run_metric(
                db=db,
                context_session_id=context_session_id,
                metric_name=metric
            )

            # KPI
            if meta.widget_type == "KPI":
                value = list(data[0].values())[0] if data else 0
                response["kpis"].append({
                    "metric": metric,
                    "title": meta.title,
                    "value": value,
                    "unit": meta.unit
                })

            # Chart
            elif meta.widget_type in ("BAR", "PIE", "LINE"):
                response["charts"].append({
                    "metric": metric,
                    "title": meta.title,
                    "chart_type": meta.chart_type,
                    "unit": meta.unit,
                    "data": data
                })

            # Table
            elif meta.widget_type == "TABLE":
                response["tables"].append({
                    "metric": metric,
                    "title": meta.title,
                    "data": data
                })

        return response
