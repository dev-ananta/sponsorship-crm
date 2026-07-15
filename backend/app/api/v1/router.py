from fastapi import APIRouter

from app.api.v1.endpoints import (
    audit,
    dashboard,
    discovery,
    drafts,
    import_export,
    organizations,
    templates,
)

api_router = APIRouter()
api_router.include_router(discovery.router)
api_router.include_router(organizations.router)
api_router.include_router(templates.router)
api_router.include_router(drafts.router)
api_router.include_router(dashboard.router)
api_router.include_router(audit.router)
api_router.include_router(import_export.router)
