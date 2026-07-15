from fastapi import APIRouter, Depends

from app.api.deps import get_crm_service
from app.schemas.crm import AuditLogResponse
from app.services.crm_service import CRMService

router = APIRouter(prefix="/audit-logs", tags=["audit"])


@router.get("", response_model=list[AuditLogResponse])
async def get_audit_logs(
    service: CRMService = Depends(get_crm_service),
) -> list[AuditLogResponse]:
    return list(await service.list_audit_logs())
