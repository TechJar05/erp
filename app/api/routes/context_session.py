from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from uuid import UUID
from app.core.database import SessionLocal
from app.models import ContextSession
from uuid import UUID
router = APIRouter(prefix="/context-sessions", tags=["Context Sessions"])

# TEMP: hardcoded user_id until auth exists

DUMMY_USER_ID = UUID("22222222-2222-2222-2222-222222222222")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/{context_id}/open")
def open_context(context_id: UUID, db: Session = Depends(get_db)):
    session = ContextSession(
        data_context_id=context_id,
        user_id=DUMMY_USER_ID
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("")
def list_sessions(db: Session = Depends(get_db)):
    return (
        db.query(ContextSession)
        .filter(ContextSession.user_id == DUMMY_USER_ID)
        .order_by(ContextSession.last_active_at.desc())
        .all()
    )
