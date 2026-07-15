from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.core.logging import setup_logging
from app.db.init_db import create_tables
from app.db.session import engine
from app.services.scheduler import SchedulerService

scheduler = SchedulerService(timezone=settings.scheduler_timezone)


@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_logging()
    await create_tables(engine)
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(title=settings.project_name, version="1.0.0", lifespan=lifespan)
register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/healthz", status_code=200)
async def health_check() -> dict[str, str]:
    return {"status": "healthy", "environment": settings.environment}
