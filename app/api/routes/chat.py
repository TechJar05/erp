from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.context_guard import require_context_session
from app.services.chat_service import ChatService
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
    response = ChatService.handle_message(
        db=db,
        context_session_id=context_session.id,
        message=payload.message
    )

    if "error" in response:
        raise HTTPException(status_code=400, detail=response["error"])

    return response
