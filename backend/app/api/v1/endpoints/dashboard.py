from fastapi import APIRouter, Depends

from app.api.deps import get_crm_service
from app.schemas.crm import DashboardStats
from app.services.crm_service import CRMService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardStats)
async def get_dashboard(
    service: CRMService = Depends(get_crm_service),
) -> DashboardStats:
    return DashboardStats(**(await service.dashboard()))
