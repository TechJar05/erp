from sqlalchemy.orm import Session
from sqlalchemy import text
from app.analytics.production_planning_metrics import PRODUCTION_PLANNING_METRICS

class ProductionPlanningAnalyticsService:

    @staticmethod
    def get_dashboard_data(db: Session):
        kpis = {}
        charts = {}

        # KPI execution
        for key, sql in PRODUCTION_PLANNING_METRICS["kpis"].items():
            result = db.execute(text(sql)).scalar()
            kpis[key] = float(result) if result is not None else 0

        # Chart execution
        for key, sql in PRODUCTION_PLANNING_METRICS["charts"].items():
            result = db.execute(text(sql)).mappings().all()
            charts[key] = result

        return {
            "kpis": kpis,
            "charts": charts
        }
