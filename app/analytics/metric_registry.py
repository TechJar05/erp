from app.services.inventory_analytics_service import InventoryAnalyticsService
from app.services.sales_analytics_service import SalesAnalyticsService

# Metric → Executor mapping
METRIC_EXECUTORS = {
    # Inventory metrics
    "total_stock": InventoryAnalyticsService,
    "below_reorder_level": InventoryAnalyticsService,
    "stock_by_warehouse": InventoryAnalyticsService,

    # Sales metrics
    "total_sales_orders": SalesAnalyticsService,
    "open_sales_orders": SalesAnalyticsService,
    "sales_by_customer": SalesAnalyticsService,
}
