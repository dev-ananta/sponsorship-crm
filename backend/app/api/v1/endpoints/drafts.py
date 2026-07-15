from fastapi import APIRouter, Depends, Query

from app.api.deps import get_crm_service
from app.models.crm import DraftStatus
from app.schemas.crm import DraftReviewAction, EmailDraftCreate, EmailDraftResponse
from app.services.crm_service import CRMService

router = APIRouter(prefix="/drafts", tags=["drafts"])


@router.get("", response_model=list[EmailDraftResponse])
async def list_drafts(
    status: DraftStatus | None = Query(default=None),
    service: CRMService = Depends(get_crm_service),
) -> list[EmailDraftResponse]:
    return list(await service.list_drafts(status))


@router.post("", response_model=EmailDraftResponse)
async def create_draft(
    payload: EmailDraftCreate,
    service: CRMService = Depends(get_crm_service),
) -> EmailDraftResponse:
    return await service.create_draft(payload)


@router.patch("/{draft_id}", response_model=EmailDraftResponse)
async def review_draft(
    draft_id: int,
    payload: DraftReviewAction,
    service: CRMService = Depends(get_crm_service),
) -> EmailDraftResponse:
    return await service.review_draft(draft_id, payload)
