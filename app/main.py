from fastapi import FastAPI
from app.api.router import api_router
from starlette.middleware.cors import CORSMiddleware

app = FastAPI(title="ERP Analytics Platform")

# Allow CORS from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
