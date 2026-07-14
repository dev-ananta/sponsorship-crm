from typing import Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.crm import (
    OrganizationResponse, DiscoveryRequest, EmailDraftResponse, 
    EmailDraftCreate, EmailDraftUpdate, DashboardStats, AuditLogResponse
)
from app.repositories.crm_repos import OrganizationRepository, EmailDraftRepository, EmailTemplateRepository, AuditLogRepository
from app.services.crawler import ComplianceScraper
from app.services.email_draft import DraftGenerationService

router = APIRouter()

@router.post("/discovery", response_model=list[OrganizationResponse])
async def discover_organizations(
    payload: DiscoveryRequest, 
    background_tasks: BackgroundTasks, 
    db: AsyncSession = Depends(get_db)
) -> Any:
    org_repo = OrganizationRepository(db)
    audit_repo = AuditLogRepository(db)
    scraper = ComplianceScraper()
    results = []

    for url_obj in payload.urls:
        url_str = str(url_obj)
        existing = await org_repo.get_by_url(url_str)
        if existing:
            results.append(existing)
            continue
        try:
            profile_data = await scraper.extract_profile(url_str)
            new_org = await org_repo.create(profile_data)
            await audit_repo.log_action("PROFILE_CREATION", f"Discovered and mapped system entry for {url_str}")
            results.append(new_org)
        except Exception as e:
            await audit_repo.log_action("DISCOVERY_FAILED", f"Error scraping {url_str}: {str(e)}")
            continue
            
    return results

@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard(db: AsyncSession = Depends(get_db)) -> Any:
    draft_repo = EmailDraftRepository(db)
    return await draft_repo.get_dashboard_metrics()

@router.post("/drafts", response_model=EmailDraftResponse)
async def generate_draft(payload: EmailDraftCreate, db: AsyncSession = Depends(get_db)) -> Any:
    org_repo = OrganizationRepository(db)
    template_repo = EmailTemplateRepository(db)
    draft_repo = EmailDraftRepository(db)
    audit_repo = AuditLogRepository(db)

    org = await org_repo.get(payload.organization_id)
    template = await template_repo.get(payload.template_id)
    if not org or not template:
        raise HTTPException(status_code=404, detail="Required Organization or Template data context mapping missing.")

    rendered = DraftGenerationService.render_factual_draft(org, template, payload.model_dump())
    
    draft = await draft_repo.create({
        "organization_id": org.id,
        "subject": rendered["subject"],
        "body": rendered["body"],
        "status": "pending"
    })
    
    await audit_repo.log_action("DRAFT_GENERATION", f"Created outreach email draft ID {draft.id} for {org.name}")
    return draft

@router.patch("/drafts/{draft_id}", response_model=EmailDraftResponse)
async def patch_draft(draft_id: int, payload: EmailDraftUpdate, db: AsyncSession = Depends(get_db)) -> Any:
    draft_repo = EmailDraftRepository(db)
    audit_repo = AuditLogRepository(db)
    
    draft = await draft_repo.get(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
        
    updated = await draft_repo.update(draft, payload.model_dump(exclude_unset=True))
    await audit_repo.log_action("DRAFT_MODIFICATION", f"Updated status or contents of Draft ID {draft_id} to {payload.status}")
    return updated

@router.get("/audit-logs", response_model=list[AuditLogResponse])
async def get_logs(db: AsyncSession = Depends(get_db)) -> Any:
    audit_repo = AuditLogRepository(db)
    return await audit_repo.get_multi(limit=250)
