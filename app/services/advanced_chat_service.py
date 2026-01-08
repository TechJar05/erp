from sqlalchemy.orm import Session
from app.models import ContextSession, DataContext
from app.services.intent_service import IntentService
from app.services.universal_query_service import UniversalQueryService
from typing import Dict, Any

class AdvancedChatService:
    """
    Enhanced chat service using universal query handler
    """
    
    @staticmethod
    def handle_message(
        db: Session,
        context_session_id,
        message: str
    ) -> Dict[str, Any]:
        """
        Universal message handler - works for ANY query
        """
        # Get session and context
        session = (
            db.query(ContextSession)
            .filter(ContextSession.id == context_session_id)
            .first()
        )

        if not session:
            return {"error": "Invalid session"}

        context = (
            db.query(DataContext)
            .filter(DataContext.id == session.data_context_id)
            .first()
        )

        if not context:
            return {"error": "Invalid context"}

        # Initialize services
        intent_service = IntentService()
        universal_service = UniversalQueryService()
        
        # Analyze intent for basic routing
        intent_result = intent_service.analyze_query(message, context)
        
        # Handle greetings
        if intent_result["intent"] == "greeting":
            return {
                "type": "greeting",
                "message": intent_result["friendly_response"],
                "suggestions": [
                    "What can you help me with?",
                    "Show me some insights"
                ]
            }
        
        # Handle help requests
        if intent_result["intent"] == "help":
            help_message = intent_service.get_help_response(context)
            return {
                "type": "help",
                "message": help_message,
                "suggestions": [
                    "Show me recent activity",
                    "What are the key metrics?"
                ]
            }
        
        # Check if query is safe
        if not AdvancedChatService._is_safe_query(message):
            return {
                "type": "error",
                "message": "I cannot execute queries that modify or delete data. I can only retrieve information.",
                "suggestions": ["Try asking for specific information"]
            }
        
        # Use universal query service for EVERYTHING else
        result = universal_service.handle_query(db, context, message)
        
        if result["success"]:
            # USER-FRIENDLY RESPONSE (hide technical details by default)
            response = {
                "type": "success",
                "summary": result["summary"],
                "insights": result["insights"],
                "suggestions": result["suggestions"],
                "data": result["data"],
                "formatted_data": result["formatted_data"]
            }
            
            # ADD TECHNICAL DETAILS ONLY IN DEBUG MODE (optional)
            # Users can request this via "show me the query" or enable debug mode
            # For now, we'll include it but you can remove these lines for production
            response["_debug"] = {
                "query_type": "universal",
                "sql_query": result["sql"],
                "explanation": result["explanation"]
            }
            
            return response
        else:
            return {
                "type": "error",
                "message": result.get("user_message", result.get("error")),
                "suggestions": ["Try rephrasing your question", "Ask for help"]
            }
    
    @staticmethod
    def _is_safe_query(message: str) -> bool:
        """Check if the query is safe"""
        unsafe_keywords = [
            "delete", "drop", "truncate", "remove", "clear",
            "update", "insert", "modify", "change", "alter"
        ]
        
        message_lower = message.lower()
        return not any(keyword in message_lower for keyword in unsafe_keywords)