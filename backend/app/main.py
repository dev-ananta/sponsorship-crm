from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.endpoints import router as api_v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize unified logger configurations
    setup_logging()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    lifespan=lifespan
)

# Apply dynamic Cross-Origin Resource Sharing protections
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register endpoints mapping
app.include_router(api_v1_router, prefix=settings.API_V1_STR)

@app.get("/healthz", status_code=200)
async def health_check():
    return {"status": "healthy", "environment": settings.ENVIRONMENT}
