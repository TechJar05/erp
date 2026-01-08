from sqlalchemy.orm import Session
from app.models import ContextSession, DataContext
from app.services.intent_service import IntentService
from app.services.response_formatter_service import ResponseFormatterService
from app.services.inventory_analytics_service import InventoryAnalyticsService
from app.services.sales_analytics_service import SalesAnalyticsService
from typing import Dict, Any

class ChatService:

    @staticmethod
    def handle_message(
        db: Session,
        context_session_id,
        message: str
    ) -> Dict[str, Any]:
        """
        Handle incoming chat message with AI-powered intent detection and response formatting
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
        formatter = ResponseFormatterService()
        
        # Analyze intent
        intent_result = intent_service.analyze_query(message, context)
        
        # Handle different intents
        if intent_result["intent"] == "greeting":
            return {
                "type": "greeting",
                "message": intent_result["friendly_response"],
                "suggestions": [
                    "What can you help me with?",
                    f"Show me {context.allowed_metrics[0]}" if context.allowed_metrics else "Help"
                ]
            }
        
        if intent_result["intent"] == "help":
            help_message = intent_service.get_help_response(context)
            return {
                "type": "help",
                "message": help_message,
                "available_metrics": context.allowed_metrics,
                "suggestions": [f"Show me {m}" for m in context.allowed_metrics[:3]]
            }
        
        if intent_result["needs_clarification"]:
            return {
                "type": "clarification",
                "message": intent_result["clarification_question"],
                "understood": intent_result["friendly_response"],
                "suggestions": [f"Show me {m}" for m in context.allowed_metrics[:3]]
            }
        
        if intent_result["intent"] == "get_metric" and intent_result["metric_name"]:
            # Execute the metric
            metric_name = intent_result["metric_name"]
            
            try:
                # Determine which service to use
                if intent_result["domain"] == "inventory" or context.primary_table == "inventory_balance":
                    raw_data = InventoryAnalyticsService.run_metric(
                        db, context_session_id, metric_name
                    )
                elif intent_result["domain"] == "sales" or context.primary_table == "sales_order":
                    raw_data = SalesAnalyticsService.run_metric(
                        db, context_session_id, metric_name
                    )
                else:
                    return {
                        "type": "error",
                        "message": "I'm not sure which system to query for that information.",
                        "suggestions": ["Ask 'What can you do?'"]
                    }
                
                # Format the response using AI
                formatted_response = formatter.format_metric_response(
                    metric_name=metric_name,
                    data=raw_data,
                    user_query=message
                )
                
                return {
                    "type": "success",
                    "metric": metric_name,
                    "domain": intent_result["domain"],
                    "summary": formatted_response["summary"],
                    "insights": formatted_response["insights"],
                    "suggestions": formatted_response["suggestions"],
                    "data": formatted_response["data"],
                    "confidence": intent_result["confidence"]
                }
                
            except PermissionError as e:
                error_response = formatter.format_error_response(str(e), message)
                return {
                    "type": "error",
                    "message": error_response["summary"],
                    "suggestions": error_response["suggestions"]
                }
            except ValueError as e:
                error_response = formatter.format_error_response(str(e), message)
                return {
                    "type": "error",
                    "message": error_response["summary"],
                    "suggestions": error_response["suggestions"]
                }
            except Exception as e:
                error_response = formatter.format_error_response(str(e), message)
                return {
                    "type": "error",
                    "message": error_response["summary"],
                    "suggestions": ["Try rephrasing your question", "Ask 'What can you do?'"]
                }
        
        # Unknown intent fallback
        return {
            "type": "unknown",
            "message": "I'm not sure how to help with that. Could you rephrase your question?",
            "suggestions": [f"Show me {m}" for m in context.allowed_metrics[:3]],
            "available_metrics": context.allowed_metrics
        }