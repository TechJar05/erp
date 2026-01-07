from fastapi import APIRouter
from app.api.routes import data_context, context_session
from app.api.routes import analytics


api_router = APIRouter()
api_router.include_router(data_context.router)
api_router.include_router(context_session.router)
api_router.include_router(analytics.router)
