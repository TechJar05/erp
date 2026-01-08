SALES_METRICS = {

    "total_sales_orders": {
        "description": "Total number of sales orders",
        "sql": """
            SELECT COUNT(*)::INT AS total_sales_orders
            FROM sales_order;
        """
    },

    "open_sales_orders": {
        "description": "Sales orders that are strictly open (not shipped, not partial)",
        "sql": """
            SELECT COUNT(*)::INT AS open_sales_orders
            FROM sales_order
            WHERE TRIM(UPPER(status)) = 'OPEN';
        """
    },

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
