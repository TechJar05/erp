from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import SessionLocal
from app.models import ContextSession

# TEMP until auth is wired
DUMMY_USER_ID = UUID("22222222-2222-2222-2222-222222222222")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_context_session(
    context_session_id: UUID,
    db: Session = Depends(get_db)
) -> ContextSession:
    session = (
        db.query(ContextSession)
        .filter(
            ContextSession.id == context_session_id,
            ContextSession.user_id == DUMMY_USER_ID
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=403,
            detail="Invalid or unauthorized context session"
        )

    return session
