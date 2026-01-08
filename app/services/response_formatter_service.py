from app.services.ai_service import AIService
from typing import List, Dict, Any

class ResponseFormatterService:
    def __init__(self):
        self.ai = AIService()
    
    def format_metric_response(
        self,
        metric_name: str,
        data: List[Dict[str, Any]],
        user_query: str
    ) -> Dict[str, Any]:
        """
        Convert raw metric data into conversational response with actual data details
        """
        
        # Handle empty data
        if not data:
            return {
                "summary": f"No data found for {metric_name}. Everything looks good!",
                "data": [],
                "insights": [],
                "suggestions": ["Try asking about other metrics"],
                "formatted_data": None
            }
        
        # Format data into human-readable structure
        formatted_data = self._create_formatted_display(data, metric_name)
        
        # Generate AI summary with actual data
        ai_summary = self._generate_ai_summary(data, metric_name, user_query)
        
        return {
            "summary": ai_summary["summary"],
            "data": data,  # Keep raw data
            "formatted_data": formatted_data,  # Add formatted display
            "insights": ai_summary["insights"],
            "suggestions": ai_summary["suggestions"]
        }
    
    def _create_formatted_display(self, data: List[Dict[str, Any]], metric_name: str) -> Dict[str, Any]:
        """
        Create structured, human-readable data display
        """
        if not data:
            return None
        
        # Detect data structure
        first_row = data[0]
        columns = list(first_row.keys())
        
        # Create table-like structure
        formatted = {
            "type": "table",
            "columns": columns,
            "rows": []
        }
        
        for row in data:
            formatted_row = {}
            for col, val in row.items():
                # Format numeric values
                if isinstance(val, (int, float)):
                    if val == int(val):
                        formatted_row[col] = int(val)
                    else:
                        formatted_row[col] = round(float(val), 2)
                else:
                    formatted_row[col] = str(val) if val else ""
            
            formatted["rows"].append(formatted_row)
        
        return formatted
    
    def _generate_ai_summary(
        self,
        data: List[Dict[str, Any]],
        metric_name: str,
        user_query: str
    ) -> Dict[str, Any]:
        """
        Generate AI summary that includes specific data points
        """
        
        # Limit data for AI to prevent token overflow
        sample_data = data[:20]
        
        # Create readable data string
        data_str = self._format_data_for_ai(sample_data)
        
        system_prompt = f"""You are a helpful ERP analytics assistant.

User asked: "{user_query}"
Metric: {metric_name}
Data returned: {len(data)} record(s)

IMPORTANT INSTRUCTIONS:
1. In your summary, MENTION SPECIFIC ITEMS/NUMBERS from the data
2. Reference actual SKUs, names, quantities, warehouse names, or other specific values
3. Be specific and concrete, not vague
4. If showing multiple items, list at least 2-3 examples with their actual values
5. Keep insights actionable and data-driven
6. Use actual numbers from the data

Bad example: "You have items below reorder level"
Good example: "Steel Rod (RM-001) is at 150 units, well below its reorder level of 500. Plastic Granules (RM-002) is also low at 50 units."

Bad example: "Stock levels vary across warehouses"
Good example: "Mumbai - Finished Goods has 1,450 units, while Delhi - Raw Materials has only 350 units."

Respond ONLY with valid JSON:
{{
    "summary": "2-3 sentences with SPECIFIC data points and numbers",
    "insights": ["insight with specific numbers", "another actionable insight"],
    "suggestions": ["specific action based on data"]
}}
"""

        messages = [
            {"role": "user", "content": f"Here's the data:\n{data_str}\n\nProvide a summary that mentions specific items, names, and numbers from the data."}
        ]
        
        try:
            response = self.ai.chat(
                messages=messages,
                system_prompt=system_prompt,
                json_mode=True
            )
            
            return self.ai.parse_json_response(response)
            
        except Exception as e:
            # Fallback to manual formatting
            return self._create_manual_summary(data, metric_name)
    
    def _create_manual_summary(self, data: List[Dict[str, Any]], metric_name: str) -> Dict[str, Any]:
        """
        Create manual summary when AI fails
        """
        count = len(data)
        
        # Get first few items for examples
        examples = []
        for i, row in enumerate(data[:3]):
            item_desc = ", ".join([f"{k}: {v}" for k, v in row.items()])
            examples.append(item_desc)
        
        summary = f"Found {count} records. Examples: {'; '.join(examples)}"
        
        return {
            "summary": summary,
            "insights": [f"Total of {count} records found"],
            "suggestions": ["Review the detailed data below"]
        }
    
    def _format_data_for_ai(self, data: List[Dict[str, Any]], max_rows: int = 20) -> str:
        """Format data in a readable way for AI"""
        if not data:
            return "No data"
        
        # Limit rows to avoid token limits
        sample_data = data[:max_rows]
        
        # Create readable string with clear structure
        result = []
        for i, row in enumerate(sample_data, 1):
            row_str = ", ".join([f"{k}={v}" for k, v in row.items()])
            result.append(f"Record {i}: {row_str}")
        
        if len(data) > max_rows:
            result.append(f"... and {len(data) - max_rows} more records")
        
        return "\n".join(result)
    
    def format_error_response(self, error_message: str, user_query: str) -> Dict[str, Any]:
        """
        Format error messages in a friendly way
        """
        system_prompt = """You are a helpful assistant. 
        
The user encountered an error. Rephrase the technical error into a friendly, 
non-technical message that helps them understand what went wrong and what to do next.

Keep it under 50 words. Be encouraging.

Respond with ONLY the friendly message text, no JSON."""

        messages = [
            {
                "role": "user", 
                "content": f"User asked: '{user_query}'\nError: {error_message}"
            }
        ]
        
        try:
            friendly_message = self.ai.chat(messages, system_prompt=system_prompt)
            return {
                "summary": friendly_message,
                "data": [],
                "insights": [],
                "suggestions": ["Try asking about available metrics"]
            }
        except:
            return {
                "summary": "Something went wrong. Please try rephrasing your question.",
                "data": [],
                "insights": [],
                "suggestions": ["Ask 'What can you do?'"]
            }