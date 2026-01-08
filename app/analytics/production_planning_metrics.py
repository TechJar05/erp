PRODUCTION_PLANNING_METRICS = {
    "kpis": {
        "total_plans": """
            SELECT COUNT(*) AS value
            FROM production_plan;
        """,
        "today_planned_qty": """
            SELECT COALESCE(SUM(planned_qty), 0) AS value
            FROM production_plan
            WHERE planned_date = CURRENT_DATE;
        """,
        "total_planned_qty": """
            SELECT COALESCE(SUM(planned_qty), 0) AS value
            FROM production_plan;
        """,
        "avg_daily_qty": """
            SELECT COALESCE(AVG(daily_qty), 0) AS value
            FROM (
                SELECT planned_date, SUM(planned_qty) AS daily_qty
                FROM production_plan
                GROUP BY planned_date
            ) t;
        """
    },
    "charts": {
        "trend": """
            SELECT
                planned_date AS date,
                SUM(planned_qty) AS qty
            FROM production_plan
            GROUP BY planned_date
            ORDER BY planned_date;
        """,
        "by_item": """
            SELECT
                i.sku,
                SUM(p.planned_qty) AS qty
            FROM production_plan p
            JOIN item i ON i.id = p.item_id
            GROUP BY i.sku
            ORDER BY qty DESC;
        """,
        "by_type": """
            SELECT
                i.item_type,
                SUM(p.planned_qty) AS qty
            FROM production_plan p
            JOIN item i ON i.id = p.item_id
            GROUP BY i.item_type;
        """
    }
}
