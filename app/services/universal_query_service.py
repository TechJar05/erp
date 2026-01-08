from app.services.ai_service import AIService
from app.models import DataContext
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect
from typing import Dict, Any, List

class UniversalQueryService:
    """
    Universal query service that can handle ANY question by:
    1. Understanding the database schema dynamically
    2. Generating appropriate SQL for any query
    3. Self-correcting syntax errors
    4. Providing intelligent responses
    """
    
    def __init__(self):
        self.ai = AIService()
    
    def get_schema_info(self, db: Session, context: DataContext) -> str:
        """
        Dynamically extract schema information from the database INCLUDING actual values
        """
        inspector = inspect(db.bind)
        
        schema_info = []
        schema_info.append("DATABASE: PostgreSQL")
        schema_info.append("\nAVAILABLE TABLES AND COLUMNS:\n")
        
        for table_name in context.allowed_tables:
            if table_name in inspector.get_table_names():
                columns = inspector.get_columns(table_name)
                foreign_keys = inspector.get_foreign_keys(table_name)
                
                schema_info.append(f"\nTable: {table_name}")
                schema_info.append("Columns:")
                for col in columns:
                    col_type = str(col['type'])
                    nullable = "NULL" if col['nullable'] else "NOT NULL"
                    schema_info.append(f"  - {col['name']} ({col_type}) {nullable}")
                
                if foreign_keys:
                    schema_info.append("Foreign Keys:")
                    for fk in foreign_keys:
                        schema_info.append(f"  - {fk['constrained_columns']} → {fk['referred_table']}.{fk['referred_columns']}")
                
                # Get sample values for important columns
                sample_values = self._get_sample_values(db, table_name, columns)
                if sample_values:
                    schema_info.append("Sample Values:")
                    for col_name, values in sample_values.items():
                        schema_info.append(f"  - {col_name}: {', '.join(map(str, values))}")
        
        return "\n".join(schema_info)

    def _get_sample_values(self, db: Session, table_name: str, columns: list) -> dict:
        """
        Get sample/distinct values for enum-like columns
        """
        sample_values = {}
        
        # Columns to check for distinct values (status, type, region, etc.)
        text_columns = [col['name'] for col in columns 
                        if 'status' in col['name'].lower() 
                        or 'type' in col['name'].lower()
                        or 'region' in col['name'].lower()]
        
        for col_name in text_columns[:3]:  # Limit to 3 columns
            try:
                query = f"SELECT DISTINCT {col_name} FROM {table_name} WHERE {col_name} IS NOT NULL LIMIT 10"
                result = db.execute(text(query)).fetchall()
                if result:
                    sample_values[col_name] = [row[0] for row in result]
            except:
                pass
        
        return sample_values
    
    def handle_query(
        self,
        db: Session,
        context: DataContext,
        user_query: str,
        max_retries: int = 2
    ) -> Dict[str, Any]:
        """
        Universal query handler with self-healing capabilities
        """
        
        # Get dynamic schema info
        schema_info = self.get_schema_info(db, context)
        
        # Try to generate and execute query
        for attempt in range(max_retries + 1):
            try:
                # Generate SQL
                sql_result = self._generate_sql(user_query, schema_info, context)
                
                if not sql_result["is_safe"]:
                    return {
                        "success": False,
                        "error": "Query is not safe to execute",
                        "explanation": sql_result["explanation"]
                    }
                
                # Execute SQL
                data = self._execute_sql(db, sql_result["sql"])
                
                # Format response
                formatted = self._format_response(data, user_query, sql_result)
                
                return {
                    "success": True,
                    "sql": sql_result["sql"],
                    "explanation": sql_result["explanation"],
                    "data": data,
                    "formatted_data": formatted["formatted_data"],
                    "summary": formatted["summary"],
                    "insights": formatted["insights"],
                    "suggestions": formatted["suggestions"]
                }
                
            except Exception as e:
                error_message = str(e)
                
                if attempt < max_retries:
                    # Try to fix the SQL based on error
                    print(f"⚠️  Attempt {attempt + 1} failed: {error_message}")
                    print(f"🔧 Attempting to self-correct...")
                    
                    sql_result = self._fix_sql_error(
                        user_query,
                        sql_result.get("sql", ""),
                        error_message,
                        schema_info
                    )
                else:
                    # Final attempt failed
                    return {
                        "success": False,
                        "error": error_message,
                        "user_message": self._create_friendly_error(user_query, error_message)
                    }
        
        return {
            "success": False,
            "error": "Could not generate valid query after retries"
        }
    
    def _generate_sql(
        self,
        user_query: str,
        schema_info: str,
        context: DataContext
    ) -> Dict[str, Any]:
        """
        Generate SQL using AI with full schema awareness
        """
        
        system_prompt = f"""You are an expert PostgreSQL query generator.

{schema_info}

CONTEXT:
- User is working in: {context.name}
- Primary focus: {context.primary_table}

CRITICAL - USE ACTUAL VALUES FROM SCHEMA:
When the schema shows "Sample Values" for a column, YOU MUST use those exact values.

Example:
If schema shows: "status: OPEN, PARTIAL, SHIPPED, CANCELLED"
And user asks "pending orders"
Then use: WHERE status IN ('OPEN', 'PARTIAL')
NOT: WHERE status = 'Pending' or 'pending'

COMMON MAPPINGS:
- "pending orders" → status IN ('OPEN', 'PARTIAL')
- "completed orders" → status = 'SHIPPED'
- "cancelled orders" → status = 'CANCELLED'
- "open orders" → status = 'OPEN'

POSTGRESQL SYNTAX RULES (CRITICAL):
- Current date: CURRENT_DATE (not CURDATE())
- Date intervals: INTERVAL '7 days' (not INTERVAL 7 DAY)
- Date arithmetic: CURRENT_DATE - INTERVAL '7 days'
- String concat: col1 || col2 (not CONCAT)
- Case insensitive: ILIKE (not LIKE for case-insensitive)
- Limit: LIMIT N (not TOP N)
- Boolean: true/false (lowercase)

QUERY GENERATION RULES:
1. ONLY SELECT (read-only)
2. Use proper JOINs based on foreign keys shown above
3. Use table aliases for clarity
4. Include LIMIT (default 100) for safety
5. Handle aggregations intelligently (COUNT, SUM, AVG, MAX, MIN)
6. Group by all non-aggregated columns
7. Order results logically
8. ALWAYS use actual column values from Sample Values section

EXAMPLES:

For "pending orders" or "open orders":
SELECT c.name, COUNT(so.id) as order_count
FROM sales_order so
JOIN customer c ON c.id = so.customer_id
WHERE so.status IN ('OPEN', 'PARTIAL')
GROUP BY c.id, c.name
ORDER BY order_count DESC

For "completed orders":
SELECT c.name, COUNT(so.id) as order_count
FROM sales_order so
JOIN customer c ON c.id = so.customer_id
WHERE so.status = 'SHIPPED'
GROUP BY c.id, c.name
ORDER BY order_count DESC

For "orders by region":
SELECT c.region, COUNT(so.id) as order_count
FROM sales_order so
JOIN customer c ON c.id = so.customer_id
GROUP BY c.region
ORDER BY order_count DESC

Respond ONLY with valid JSON:
{{
    "sql": "SELECT ...",
    "explanation": "What this query does",
    "is_safe": true,
    "estimated_rows": "approximate number of rows expected"
}}
"""

        messages = [
            {"role": "user", "content": f"User query: {user_query}\n\nGenerate PostgreSQL SQL for this."}
        ]
        
        try:
            response = self.ai.chat(
                messages=messages,
                system_prompt=system_prompt,
                json_mode=True
            )
            
            result = self.ai.parse_json_response(response)
            
            # Validate safety
            if not self._is_safe_sql(result.get("sql", "")):
                result["is_safe"] = False
            
            return result
            
        except Exception as e:
            return {
                "sql": None,
                "explanation": f"Failed to generate SQL: {str(e)}",
                "is_safe": False
            }
    
    def _fix_sql_error(
        self,
        user_query: str,
        failed_sql: str,
        error_message: str,
        schema_info: str
    ) -> Dict[str, Any]:
        """
        Self-healing: Fix SQL based on error message
        """
        
        system_prompt = f"""You are a PostgreSQL expert fixing a broken query.

{schema_info}

ORIGINAL USER QUERY: {user_query}

FAILED SQL:
{failed_sql}

ERROR MESSAGE:
{error_message}

YOUR TASK:
Analyze the error and generate a CORRECTED version of the SQL that will work.

Common fixes:
- MySQL syntax → PostgreSQL syntax
- Missing JOINs
- Wrong column names
- Aggregation without GROUP BY
- Date function errors

Respond ONLY with valid JSON:
{{
    "sql": "CORRECTED SQL HERE",
    "explanation": "What was wrong and how you fixed it",
    "is_safe": true
}}
"""

        messages = [
            {"role": "user", "content": "Fix the SQL query based on the error above."}
        ]
        
        try:
            response = self.ai.chat(
                messages=messages,
                system_prompt=system_prompt,
                json_mode=True
            )
            
            return self.ai.parse_json_response(response)
            
        except Exception as e:
            return {
                "sql": None,
                "explanation": f"Could not fix: {str(e)}",
                "is_safe": False
            }
    
    def _execute_sql(self, db: Session, sql: str) -> List[Dict]:
        """Execute SQL and return results"""
        if not self._is_safe_sql(sql):
            raise ValueError("Unsafe SQL detected")
        
        result = db.execute(text(sql)).mappings().all()
        return [dict(row) for row in result]
    
    def _is_safe_sql(self, sql: str) -> bool:
        """Validate SQL is read-only"""
        if not sql:
            return False
        
        sql_upper = sql.upper().strip()
        
        # Must start with SELECT
        if not sql_upper.startswith("SELECT"):
            return False
        
        # Block dangerous keywords
        dangerous = ["UPDATE", "DELETE", "INSERT", "DROP", "ALTER", "TRUNCATE", 
                     "CREATE", "GRANT", "REVOKE", "EXEC", "EXECUTE"]
        
        return not any(word in sql_upper for word in dangerous)
    
    def _format_response(
        self,
        data: List[Dict],
        user_query: str,
        sql_result: Dict
    ) -> Dict[str, Any]:
        """Format data into user-friendly response"""
        
        if not data:
            # Create intelligent "no data" message
            no_data_message = self._create_no_data_message(user_query, sql_result)
            
            return {
                "formatted_data": None,
                "summary": no_data_message["summary"],
                "insights": no_data_message["insights"],
                "suggestions": no_data_message["suggestions"]
            }
        
        # Create formatted table
        formatted_data = self._create_table_format(data)
        
        # Generate AI summary
        data_sample = data[:20]  # First 20 rows for AI
        data_str = "\n".join([
            f"Row {i+1}: {', '.join([f'{k}={v}' for k, v in row.items()])}"
            for i, row in enumerate(data_sample)
        ])
        
        system_prompt = f"""You are a helpful data analyst.

User asked: "{user_query}"
Query executed: {sql_result.get('explanation')}
Rows returned: {len(data)}

IMPORTANT: Mention SPECIFIC values from the data in your summary.
Be concrete, not vague.

Respond with JSON:
{{
    "summary": "2-3 sentences with specific numbers and names from data",
    "insights": ["specific insight 1", "specific insight 2"],
    "suggestions": ["actionable suggestion"]
}}
"""

        messages = [
            {"role": "user", "content": f"Data:\n{data_str}\n\nSummarize with specific details."}
        ]
        
        try:
            response = self.ai.chat(messages, system_prompt=system_prompt, json_mode=True)
            ai_response = self.ai.parse_json_response(response)
            
            return {
                "formatted_data": formatted_data,
                "summary": ai_response["summary"],
                "insights": ai_response["insights"],
                "suggestions": ai_response["suggestions"]
            }
        except:
            # Fallback
            return {
                "formatted_data": formatted_data,
                "summary": f"Found {len(data)} records.",
                "insights": ["See data below for details"],
                "suggestions": []
            }
    
    def _create_no_data_message(self, user_query: str, sql_result: Dict) -> Dict[str, Any]:
        """
        Create intelligent message when no data is found
        """
        system_prompt = f"""You are a helpful assistant explaining why no data was found.

User asked: "{user_query}"
Query executed successfully but returned 0 results.

Generate a friendly response that:
1. Acknowledges what they were looking for
2. Explains likely reasons (e.g., wrong status, no matching records, etc.)
3. Suggests alternative questions they could ask

DO NOT mention technical details like SQL, table names, or column names.
Be conversational and helpful.

Respond with JSON:
{{
    "summary": "Friendly explanation of why no data was found",
    "insights": ["possible reason 1", "possible reason 2"],
    "suggestions": ["alternative question 1", "alternative question 2"]
}}
"""

        messages = [
            {"role": "user", "content": "Explain why no data was found."}
        ]
        
        try:
            response = self.ai.chat(messages, system_prompt=system_prompt, json_mode=True)
            return self.ai.parse_json_response(response)
        except:
            return {
                "summary": "I couldn't find any data matching your request.",
                "insights": [
                    "This might be because the specific criteria don't match any records",
                    "The data you're looking for might be stored differently"
                ],
                "suggestions": [
                    "Try asking about related information",
                    "Ask 'What data do you have available?'"
                ]
            }
    
    def _create_table_format(self, data: List[Dict]) -> Dict[str, Any]:
        """Create table format from data"""
        if not data:
            return None
        
        columns = list(data[0].keys())
        
        formatted_rows = []
        for row in data:
            formatted_row = {}
            for col, val in row.items():
                if isinstance(val, (int, float)):
                    formatted_row[col] = int(val) if val == int(val) else round(float(val), 2)
                else:
                    formatted_row[col] = str(val) if val is not None else ""
            formatted_rows.append(formatted_row)
        
        return {
            "type": "table",
            "columns": columns,
            "rows": formatted_rows
        }
    
    def _create_friendly_error(self, user_query: str, error: str) -> str:
        """Create user-friendly error message"""
        system_prompt = """Convert this technical error into a friendly message.
Keep it under 50 words. Be helpful and encouraging.
Respond with just the message, no JSON."""
        
        messages = [
            {"role": "user", "content": f"Query: {user_query}\nError: {error}"}
        ]
        
        try:
            return self.ai.chat(messages, system_prompt=system_prompt)
        except:
            return "I had trouble understanding your question. Could you rephrase it?"