from sqlalchemy import text

class BaseProductionExec:
    def run(self, db, sql):
        return db.execute(text(sql)).mappings().all()

class TotalProductionOrdersExec(BaseProductionExec):
    def run_metric(self, db, context_session_id, metric_name):
        return self.run(db, "SELECT COUNT(*) AS value FROM production_order")

class InProgressOrdersExec(BaseProductionExec):
    def run_metric(self, db, context_session_id, metric_name):
        return self.run(db, """
            SELECT COUNT(*) AS value
            FROM production_order
            WHERE status = 'IN_PROGRESS'
        """)

class DelayedOrdersExec(BaseProductionExec):
    def run_metric(self, db, context_session_id, metric_name):
        return self.run(db, """
            SELECT COUNT(*) AS value
            FROM production_order
            WHERE status = 'DELAYED'
        """)

class MachineUtilizationExec(BaseProductionExec):
    def run_metric(self, db, context_session_id, metric_name):
        return self.run(db, """
            SELECT m.machine_code, COUNT(po.id) AS orders
            FROM production_order po
            JOIN machine m ON m.id = po.machine_id
            GROUP BY m.machine_code
        """)

class ProductionStatusDistributionExec(BaseProductionExec):
    def run_metric(self, db, context_session_id, metric_name):
        return self.run(db, """
            SELECT status, COUNT(*) AS count
            FROM production_order
            GROUP BY status
        """)
