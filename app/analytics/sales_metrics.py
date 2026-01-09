SALES_METRICS = {

    # 🔹 KPI: Total Sales Orders
    "total_sales_orders": {
        "description": "Total number of sales orders",
        "sql": """
            SELECT COUNT(*)::INT AS total_sales_orders
            FROM sales_order;
        """
    },

    # 🔹 KPI: Open Sales Orders
    "open_sales_orders": {
        "description": "Sales orders that are strictly open",
        "sql": """
            SELECT COUNT(*)::INT AS open_sales_orders
            FROM sales_order
            WHERE TRIM(UPPER(status)) = 'OPEN';
        """
    },

    # 🔹 KPI: Partial Sales Orders
    "partial_sales_orders": {
        "description": "Sales orders partially fulfilled",
        "sql": """
            SELECT COUNT(*)::INT AS partial_sales_orders
            FROM sales_order
            WHERE TRIM(UPPER(status)) = 'PARTIAL';
        """
    },

    # 🔹 KPI: Shipped Sales Orders
    "shipped_sales_orders": {
        "description": "Sales orders fully shipped",
        "sql": """
            SELECT COUNT(*)::INT AS shipped_sales_orders
            FROM sales_order
            WHERE TRIM(UPPER(status)) = 'SHIPPED';
        """
    },

    # 🔹 CHART: Sales by Customer
    "sales_by_customer": {
        "description": "Sales orders grouped by customer",
        "sql": """
            SELECT
                c.name AS customer,
                COUNT(so.id)::INT AS total_orders
            FROM sales_order so
            JOIN customer c ON c.id = so.customer_id
            GROUP BY c.name
            ORDER BY total_orders DESC;
        """
    }

}
