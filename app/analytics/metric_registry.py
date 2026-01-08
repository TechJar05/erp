from app.services.inventory_analytics_service import InventoryAnalyticsService
from app.services.sales_analytics_service import SalesAnalyticsService
from app.analytics.production_planning import (
    TotalProductionPlansExecutor,
    TodayPlannedQtyExecutor,
    TotalPlannedQtyExecutor,
    AvgDailyPlannedQtyExecutor,
    ProductionTrendExecutor,
    PlannedByItemExecutor,
    PlannedByTypeExecutor
)


# Metric → Executor mapping
METRIC_EXECUTORS = {
    # Inventory metrics
    "total_stock": InventoryAnalyticsService,
    "below_reorder_level": InventoryAnalyticsService,
    "stock_by_warehouse": InventoryAnalyticsService,

    # Sales metrics
   "total_sales_orders": SalesAnalyticsService,
    "open_sales_orders": SalesAnalyticsService,
    "partial_sales_orders": SalesAnalyticsService,
    "shipped_sales_orders": SalesAnalyticsService,
    "sales_by_customer": SalesAnalyticsService,
    
    # 🔹 KPIs
    "total_production_plans": TotalProductionPlansExecutor(),
    "today_planned_qty": TodayPlannedQtyExecutor(),
    "total_planned_qty": TotalPlannedQtyExecutor(),
    "avg_daily_planned_qty": AvgDailyPlannedQtyExecutor(),

    # 🔹 Charts
    "production_plan_trend": ProductionTrendExecutor(),
    "planned_by_item": PlannedByItemExecutor(),
    "planned_by_type": PlannedByTypeExecutor(),
}
