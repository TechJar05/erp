from app.services.ai_service import AIService
from app.models import DataContext
from typing import Dict, Any
import sqlalchemy
from sqlalchemy import text

class SQLGeneratorService:
    def __init__(self):
        self.ai = AIService()
    
    def can_generate_sql(self, user_query: str, context: DataContext) -> bool:
        """
        Determine if we should generate custom SQL for this query
        """
        # Keywords that suggest custom queries
        custom_keywords = [
            "top", "bottom", "highest", "lowest", "most", "least",
            "compare", "comparison", "between", "range",
            "average", "avg", "sum", "total", "count",
            "group", "grouped", "categorize",
            "sort", "order", "rank",
            "more than", "less than", "greater", "fewer",
            "first", "last", "recent"
        ]
        
        query_lower = user_query.lower()
        return any(keyword in query_lower for keyword in custom_keywords)
    
    def generate_sql(
        self,
        user_query: str,
        context: DataContext
    ) -> Dict[str, Any]:
        """
        Generate safe SQL query based on user's natural language request
        """
        
        system_prompt = f"""You are an expert SQL generator for an ERP inventory system.

Context Information:
- Context Name: {context.name}
- Primary Table: {context.primary_table}
- Allowed Tables: {', '.join(context.allowed_tables)}
- Allowed Columns (JSON): {context.allowed_columns}

Database Schema Details:
- inventory_balance table: id, item_id (FK to item), warehouse_id (FK to warehouse), quantity_on_hand
- item table: id, sku, name, item_type, uom, reorder_level, safety_stock
- warehouse table: id, plant_id (FK to plant), name, type
- plant table: id, organization_id, name, location

STRICT RULES:
1. ONLY use tables from allowed_tables list
2. ONLY select columns from allowed_columns
3. NEVER use UPDATE, DELETE, INSERT, DROP, ALTER, TRUNCATE
4. Use proper JOINs: inventory_balance.item_id = item.id, inventory_balance.warehouse_id = warehouse.id
5. Always use table aliases (b for balance, i for item, w for warehouse)
6. Include LIMIT clause for safety (default LIMIT 100)
7. Use aggregate functions when appropriate (SUM, COUNT, AVG, MAX, MIN)

Common Query Patterns:
- "top N items" → ORDER BY quantity_on_hand DESC LIMIT N
- "items between X and Y" → WHERE quantity_on_hand BETWEEN X AND Y
- "average stock" → SELECT AVG(quantity_on_hand)
- "compare warehouses" → GROUP BY warehouse_id
- "items with more than X" → WHERE quantity_on_hand > X

Respond ONLY with valid JSON:
{{
    "sql": "SELECT ... FROM ... WHERE ... ORDER BY ... LIMIT ...",
    "explanation": "Brief explanation",
    "is_safe": true,
    "estimated_complexity": "simple|medium|complex",
    "tables_used": ["table1", "table2"]
}}

Examples:

User: "Show me top 5 items by stock quantity"
{{
    "sql": "SELECT i.sku, i.name, SUM(b.quantity_on_hand) as total_stock FROM inventory_balance b JOIN item i ON i.id = b.item_id GROUP BY i.id, i.sku, i.name ORDER BY total_stock DESC LIMIT 5",
    "explanation": "Returns the 5 items with highest total stock across all warehouses",
    "is_safe": true,
    "estimated_complexity": "medium",
    "tables_used": ["inventory_balance", "item"]
}}

User: "Show me items with stock between 100 and 500"
{{
    "sql": "SELECT i.sku, i.name, b.quantity_on_hand FROM inventory_balance b JOIN item i ON i.id = b.item_id WHERE b.quantity_on_hand BETWEEN 100 AND 500 ORDER BY b.quantity_on_hand DESC LIMIT 100",
    "explanation": "Returns items with stock levels between 100 and 500 units",
    "is_safe": true,
    "estimated_complexity": "simple",
    "tables_used": ["inventory_balance", "item"]
}}

User: "What's the average stock quantity?"
{{
    "sql": "SELECT AVG(quantity_on_hand) as average_stock FROM inventory_balance",
    "explanation": "Calculates the average stock quantity across all items and warehouses",
    "is_safe": true,
    "estimated_complexity": "simple",
    "tables_used": ["inventory_balance"]
}}

User: "Compare stock levels across warehouses"
{{
    "sql": "SELECT w.name as warehouse, SUM(b.quantity_on_hand) as total_stock FROM inventory_balance b JOIN warehouse w ON w.id = b.warehouse_id GROUP BY w.id, w.name ORDER BY total_stock DESC",
    "explanation": "Compares total stock levels across different warehouses",
    "is_safe": true,
    "estimated_complexity": "medium",
    "tables_used": ["inventory_balance", "warehouse"]
}}

If unsafe or not possible, set is_safe to false.
"""

        messages = [
            {"role": "user", "content": f"Generate SQL for: {user_query}"}
        ]
        
        try:
            response = self.ai.chat(
                messages=messages,
                system_prompt=system_prompt,
                json_mode=True
            )
            
            result = self.ai.parse_json_response(response)
            
            # Additional safety check
            if not self._validate_sql_safety(result.get("sql", "")):
                result["is_safe"] = False
                result["explanation"] = "Query contains potentially unsafe operations"
            
            return result
            
        except Exception as e:
            return {
                "sql": None,
                "explanation": f"Failed to generate SQL: {str(e)}",
                "is_safe": False,
                "estimated_complexity": "unknown",
                "tables_used": []
            }
    
    def _validate_sql_safety(self, sql: str) -> bool:
        """
        Validate that SQL is safe to execute (read-only)
        """
        if not sql:
            return False
        
        sql_upper = sql.upper()
        
        # Forbidden keywords
        forbidden = [
            "UPDATE", "DELETE", "INSERT", "DROP", "ALTER",
            "TRUNCATE", "EXEC", "EXECUTE", "CREATE", "GRANT",
            "REVOKE", "COMMIT", "ROLLBACK", "SAVEPOINT"
        ]
        
        for keyword in forbidden:
            if keyword in sql_upper:
                return False
        
        # Must start with SELECT
        if not sql_upper.strip().startswith("SELECT"):
            return False
        
        return True
    
    def execute_generated_sql(
        self,
        db,
        sql: str,
        context: DataContext
    ) -> list:
        """
        Execute the generated SQL safely
        """
        # Final safety check
        if not self._validate_sql_safety(sql):
            raise ValueError("SQL query failed safety validation")
        
        try:
            result = db.execute(text(sql)).mappings().all()
            return result
        except Exception as e:
            raise ValueError(f"SQL execution failed: {str(e)}")