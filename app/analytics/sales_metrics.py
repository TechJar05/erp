SALES_METRICS = {
    "total_sales_orders": {
        "description": "Total number of sales orders",
        "sql": """
            SELECT COUNT(*) AS total_sales_orders
            FROM sales_order;
        """
    },
    "open_sales_orders": {
        "description": "Sales orders not yet shipped",
        "sql": """
            SELECT COUNT(*) AS open_sales_orders
            FROM sales_order
            WHERE status IN ('OPEN', 'PARTIAL');
        """
    },
    "sales_by_customer": {
        "description": "Sales orders grouped by customer",
        "sql": """
            SELECT c.name AS customer, COUNT(so.id) AS total_orders
            FROM sales_order so
            JOIN customer c ON c.id = so.customer_id
            GROUP BY c.name;
        """
    }
}
