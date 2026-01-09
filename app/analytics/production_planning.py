from sqlalchemy import text

class BaseProductionExecutor:
    def run(self, db, sql):
        return db.execute(text(sql)).mappings().all()


class TotalProductionPlansExecutor(BaseProductionExecutor):
    def run_metric(self, db, context_session_id, metric_name):
        return self.run(db, """
            SELECT COUNT(*) AS value
            FROM production_plan;
        """)


class TodayPlannedQtyExecutor(BaseProductionExecutor):
    def run_metric(self, db, context_session_id, metric_name):
        return self.run(db, """
            SELECT COALESCE(SUM(planned_qty), 0) AS value
            FROM production_plan
            WHERE planned_date = CURRENT_DATE;
        """)


class TotalPlannedQtyExecutor(BaseProductionExecutor):
    def run_metric(self, db, context_session_id, metric_name):
        return self.run(db, """
            SELECT COALESCE(SUM(planned_qty), 0) AS value
            FROM production_plan;
        """)


class AvgDailyPlannedQtyExecutor(BaseProductionExecutor):
    def run_metric(self, db, context_session_id, metric_name):
        return self.run(db, """
            SELECT AVG(daily_qty) AS value
            FROM (
                SELECT planned_date, SUM(planned_qty) AS daily_qty
                FROM production_plan
                GROUP BY planned_date
            ) t;
        """)


class ProductionTrendExecutor(BaseProductionExecutor):
    def run_metric(self, db, context_session_id, metric_name):
        return self.run(db, """
            SELECT planned_date AS date, SUM(planned_qty) AS qty
            FROM production_plan
            GROUP BY planned_date
            ORDER BY planned_date;
        """)


class PlannedByItemExecutor(BaseProductionExecutor):
    def run_metric(self, db, context_session_id, metric_name):
        return self.run(db, """
            SELECT i.sku, SUM(p.planned_qty) AS qty
            FROM production_plan p
            JOIN item i ON i.id = p.item_id
            GROUP BY i.sku
            ORDER BY qty DESC;
        """)


class PlannedByTypeExecutor(BaseProductionExecutor):
    def run_metric(self, db, context_session_id, metric_name):
        return self.run(db, """
            SELECT i.item_type, SUM(p.planned_qty) AS qty
            FROM production_plan p
            JOIN item i ON i.id = p.item_id
            GROUP BY i.item_type;
        """)
