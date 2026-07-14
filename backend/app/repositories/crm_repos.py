import json
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.crm import Organization, EmailTemplate, EmailDraft, AuditLog, DraftStatus
from app.repositories.base import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    def __init__(self, db: AsyncSession):
        super().__init__(AuditLog, db)

    async def log_action(self, action: str, details: dict | str) -> AuditLog:
        detail_str = json.dumps(details) if isinstance(details, dict) else details
        return await self.create({"action": action, "details": detail_str})


class OrganizationRepository(BaseRepository[Organization]):
    def __init__(self, db: AsyncSession):
        super().__init__(Organization, db)

    async def get_by_url(self, url: str) -> Organization | None:
        result = await self.db.execute(select(self.model).where(self.model.website == url))
        return result.scalars().first()


class EmailTemplateRepository(BaseRepository[EmailTemplate]):
    def __init__(self, db: AsyncSession):
        super().__init__(EmailTemplate, db)


class EmailDraftRepository(BaseRepository[EmailDraft]):
    def __init__(self, db: AsyncSession):
        super().__init__(EmailDraft, db)

    async def get_dashboard_metrics(self) -> dict:
        total_orgs = await self.db.scalar(select(func.count(Organization.id)))
        
        async def count_status(status_val: DraftStatus) -> int:
            return await self.db.scalar(select(func.count(EmailDraft.id)).where(EmailDraft.status == status_val)) or 0

        return {
            "organizations_imported": total_orgs or 0,
            "drafts_pending_review": await count_status(DraftStatus.PENDING),
            "approved_drafts": await count_status(DraftStatus.APPROVED),
            "sent_emails": await count_status(DraftStatus.SENT),
            "replies": 0,  # Hook for inbound integration hooks
            "declined_organizations": await count_status(DraftStatus.DECLINED)
        }
