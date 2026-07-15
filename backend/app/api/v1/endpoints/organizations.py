from fastapi import APIRouter, Depends

from app.api.deps import get_crm_service
from app.schemas.crm import OrganizationCreate, OrganizationResponse, OrganizationUpdate
from app.services.crm_service import CRMService

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("", response_model=list[OrganizationResponse])
async def list_organizations(
    service: CRMService = Depends(get_crm_service),
) -> list[OrganizationResponse]:
    return list(await service.list_organizations())


@router.post("", response_model=OrganizationResponse)
async def create_organization(
    payload: OrganizationCreate,
    service: CRMService = Depends(get_crm_service),
) -> OrganizationResponse:
    return await service.create_organization(payload)


@router.patch("/{organization_id}", response_model=OrganizationResponse)
async def update_organization(
    organization_id: int,
    payload: OrganizationUpdate,
    service: CRMService = Depends(get_crm_service),
) -> OrganizationResponse:
    return await service.update_organization(organization_id, payload)
