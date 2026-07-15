from fastapi import APIRouter, Depends

from app.api.deps import get_crm_service
from app.schemas.crm import EmailTemplateCreate, EmailTemplateResponse
from app.services.crm_service import CRMService

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("", response_model=list[EmailTemplateResponse])
async def list_templates(
    service: CRMService = Depends(get_crm_service),
) -> list[EmailTemplateResponse]:
    return list(await service.list_templates())


@router.post("", response_model=EmailTemplateResponse)
async def create_template(
    payload: EmailTemplateCreate,
    service: CRMService = Depends(get_crm_service),
) -> EmailTemplateResponse:
    return await service.create_template(payload)
