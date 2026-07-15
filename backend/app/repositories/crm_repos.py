import json

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.crm import AuditLog, DraftStatus, EmailDraft, EmailTemplate, Organization
from app.repositories.base import BaseRepository


class OrganizationRepository(BaseRepository[Organization]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Organization, session)

    async def get_by_website(self, website: str) -> Organization | None:
        result = await self.session.execute(
            select(Organization).where(Organization.website == website)
        )
        return result.scalar_one_or_none()


class EmailTemplateRepository(BaseRepository[EmailTemplate]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(EmailTemplate, session)

    async def get_by_name(self, name: str) -> EmailTemplate | None:
        result = await self.session.execute(
            select(EmailTemplate).where(EmailTemplate.name == name)
        )
        return result.scalar_one_or_none()


class EmailDraftRepository(BaseRepository[EmailDraft]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(EmailDraft, session)

    async def list_by_status(self, status: DraftStatus) -> list[EmailDraft]:
        result = await self.session.execute(
            select(EmailDraft).where(EmailDraft.status == status)
        )
        return list(result.scalars().all())

    async def dashboard_metrics(self) -> dict[str, int]:
        total_orgs = await self.session.scalar(select(func.count(Organization.id)))

        async def count_drafts(status: DraftStatus) -> int:
            value = await self.session.scalar(
                select(func.count(EmailDraft.id)).where(EmailDraft.status == status)
            )
            return value or 0

        return {
            "organizations_imported": total_orgs or 0,
            "drafts_pending_review": await count_drafts(DraftStatus.pending),
            "approved_drafts": await count_drafts(DraftStatus.approved),
            "sent_emails": await count_drafts(DraftStatus.sent),
            "replies": 0,
            "declined_organizations": await count_drafts(DraftStatus.declined),
        }


class AuditLogRepository(BaseRepository[AuditLog]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(AuditLog, session)

    async def log(self, action: str, details: dict | str) -> AuditLog:
        payload = json.dumps(details) if isinstance(details, dict) else details
        return await self.create({"action": action, "details": payload})
