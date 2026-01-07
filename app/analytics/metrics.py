INVENTORY_METRICS = {
    "total_stock": {
        "description": "Total stock across all warehouses",
        "sql": """
            SELECT SUM(quantity_on_hand) AS total_stock
            FROM inventory_balance;
        """
    },
    "stock_by_warehouse": {
        "description": "Stock grouped by warehouse",
        "sql": """
            SELECT warehouse_id, SUM(quantity_on_hand) AS total_stock
            FROM inventory_balance
            GROUP BY warehouse_id;
        """
    },
    "below_reorder_level": {
        "description": "Items below reorder level",
        "sql": """
            SELECT i.sku, i.name, b.quantity_on_hand, i.reorder_level
            FROM inventory_balance b
            JOIN item i ON i.id = b.item_id
            WHERE b.quantity_on_hand < i.reorder_level;
        """
    }
}
