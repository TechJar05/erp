from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.context_guard import require_context_session
from app.services.advanced_chat_service import AdvancedChatService
from app.schemas.chat import ChatRequest

router = APIRouter(prefix="/chat", tags=["Chat"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("")
def chat(
    payload: ChatRequest,
    context_session = Depends(require_context_session),
    db: Session = Depends(get_db)
):
    """
    AI-powered chat endpoint with advanced features:
    
    - Natural language understanding
    - Predefined metric execution
    - Custom SQL generation for complex queries
    - Intelligent response formatting
    - Safety validation
    """
    response = AdvancedChatService.handle_message(
        db=db,
        context_session_id=context_session.id,
        message=payload.message
    )

    if response.get("type") == "error" and "Invalid session" in response.get("message", ""):
        raise HTTPException(status_code=400, detail=response.get("message"))

    return response