from fastapi import APIRouter
from app.api.routes import (
    data_context,
    context_session,
    analytics,
    chat,
    automation   # 👈 THIS MUST EXIST
)
from app.api.routes import dashboard
api_router = APIRouter()

api_router.include_router(data_context.router)
api_router.include_router(context_session.router)
api_router.include_router(analytics.router)
api_router.include_router(chat.router)
api_router.include_router(automation.router)  # 👈 THIS LINE

api_router.include_router(dashboard.router)