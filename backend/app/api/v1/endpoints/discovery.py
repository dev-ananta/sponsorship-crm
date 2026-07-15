from fastapi import APIRouter, Depends

from app.api.deps import get_crm_service
from app.schemas.crm import DiscoveryRequest, OrganizationResponse
from app.services.crm_service import CRMService

router = APIRouter(prefix="/discovery", tags=["discovery"])


@router.post("", response_model=list[OrganizationResponse])
async def discover_organizations(
    payload: DiscoveryRequest,
    service: CRMService = Depends(get_crm_service),
) -> list[OrganizationResponse]:
    return list(await service.discover_organizations([str(url) for url in payload.urls]))
