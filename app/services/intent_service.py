from app.services.ai_service import AIService
from typing import Dict, Any, List
from app.models import DataContext

class IntentService:
    def __init__(self):
        self.ai = AIService()
    
    def analyze_query(
        self,
        user_message: str,
        context: DataContext
    ) -> Dict[str, Any]:
        """
        Analyze user query and determine intent, metric, and action
        
        Returns:
            {
                "intent": "get_metric" | "get_data" | "unknown" | "greeting",
                "metric_name": str or None,
                "domain": "inventory" | "sales" | "production" | None,
                "confidence": float,
                "needs_clarification": bool,
                "clarification_question": str or None,
                "friendly_response": str
            }
        """
        
        system_prompt = f"""You are an intelligent ERP analytics assistant.

Available Context: {context.name}
Context Type: {context.context_type}
Primary Table: {context.primary_table}
Available Metrics: {', '.join(context.allowed_metrics)}

Your job is to analyze user queries and determine:
1. Intent (what does the user want?)
2. Which metric to use (if applicable)
3. Domain (inventory, sales, production)
4. Confidence level
5. Whether clarification is needed

Respond ONLY with valid JSON in this exact format:
{{
    "intent": "get_metric|get_data|unknown|greeting|help",
    "metric_name": "exact_metric_name_from_allowed_list or null",
    "domain": "inventory|sales|production or null",
    "confidence": 0.0-1.0,
    "needs_clarification": true|false,
    "clarification_question": "question to ask user or null",
    "friendly_response": "brief explanation of what you understood"
}}

Intent Types:
- get_metric: User wants a specific metric (e.g., "show total stock")
- get_data: User wants raw data (e.g., "list all warehouses")
- unknown: Cannot determine what user wants
- greeting: User is greeting (hi, hello, etc.)
- help: User wants to know what you can do

Examples:
User: "Show me low stock items" 
→ {{"intent": "get_metric", "metric_name": "below_reorder_level", "domain": "inventory", "confidence": 0.95, "needs_clarification": false, "clarification_question": null, "friendly_response": "I'll show you items below their reorder level"}}

User: "What can you do?"
→ {{"intent": "help", "metric_name": null, "domain": null, "confidence": 1.0, "needs_clarification": false, "clarification_question": null, "friendly_response": "I can help you with inventory and sales analytics"}}

User: "Show me something"
→ {{"intent": "unknown", "metric_name": null, "domain": null, "confidence": 0.2, "needs_clarification": true, "clarification_question": "What specific information would you like to see? I can show you stock levels, sales orders, or warehouse data.", "friendly_response": "I'm not sure what you'd like to see"}}
"""

        messages = [
            {"role": "user", "content": user_message}
        ]
        
        try:
            response = self.ai.chat(
                messages=messages,
                system_prompt=system_prompt,
                json_mode=True
            )
            
            return self.ai.parse_json_response(response)
            
        except Exception as e:
            # Fallback response on error
            return {
                "intent": "unknown",
                "metric_name": None,
                "domain": None,
                "confidence": 0.0,
                "needs_clarification": True,
                "clarification_question": "I'm having trouble understanding. Could you rephrase your question?",
                "friendly_response": f"Error: {str(e)}"
            }
    
    def get_help_response(self, context: DataContext) -> str:
        """
        Generate helpful response about available capabilities
        """
        system_prompt = f"""You are a friendly ERP assistant.
        
The user is in the "{context.name}" context.
Available metrics: {', '.join(context.allowed_metrics)}

Generate a brief, friendly message explaining what you can help with.
Be conversational and welcoming. Mention 2-3 example questions they could ask.

Keep it under 100 words."""

        messages = [
            {"role": "user", "content": "What can you help me with?"}
        ]
        
        return self.ai.chat(messages, system_prompt=system_prompt)