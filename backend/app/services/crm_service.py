from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ConflictError, NotFoundError
from app.models.crm import DraftStatus
from app.repositories.crm_repos import (
    AuditLogRepository,
    EmailDraftRepository,
    EmailTemplateRepository,
    OrganizationRepository,
)
from app.schemas.crm import (
    DraftReviewAction,
    EmailDraftCreate,
    EmailTemplateCreate,
    OrganizationCreate,
    OrganizationUpdate,
)
from app.services.crawler import ComplianceScraper
from app.services.email_draft import DraftGenerationService


class CRMService:
    def __init__(self, session: AsyncSession) -> None:
        self.org_repo = OrganizationRepository(session)
        self.template_repo = EmailTemplateRepository(session)
        self.draft_repo = EmailDraftRepository(session)
        self.audit_repo = AuditLogRepository(session)
        self.scraper = ComplianceScraper()
        self.draft_generator = DraftGenerationService()

    async def discover_organizations(self, urls: list[str]) -> Sequence:
        discovered = []
        for url in urls:
            existing = await self.org_repo.get_by_website(url)
            if existing:
                discovered.append(existing)
                continue

            profile = await self.scraper.extract_profile(url)
            organization = await self.org_repo.create(profile)
            await self.audit_repo.log(
                "profile_created",
                {"organization_id": organization.id, "source": url},
            )
            discovered.append(organization)

        return discovered

    async def list_organizations(self) -> Sequence:
        return await self.org_repo.list(limit=500)

    async def create_organization(self, payload: OrganizationCreate):
        existing = await self.org_repo.get_by_website(str(payload.website))
        if existing:
            raise ConflictError("Organization with this website already exists")

        org = await self.org_repo.create(payload.model_dump(mode="json"))
        await self.audit_repo.log("profile_created", {"organization_id": org.id})
        return org

    async def update_organization(
        self, organization_id: int, payload: OrganizationUpdate
    ):
        org = await self.org_repo.get(organization_id)
        if org is None:
            raise NotFoundError("Organization not found")

        updated = await self.org_repo.update(
            org,
            payload.model_dump(mode="json", exclude_unset=True),
        )
        await self.audit_repo.log(
            "profile_updated", {"organization_id": organization_id}
        )
        return updated

    async def create_template(self, payload: EmailTemplateCreate):
        existing = await self.template_repo.get_by_name(payload.name)
        if existing:
            raise ConflictError("Email template name already exists")

        template = await self.template_repo.create(payload.model_dump())
        await self.audit_repo.log("template_created", {"template_id": template.id})
        return template

    async def list_templates(self) -> Sequence:
        return await self.template_repo.list(limit=100)

    async def create_draft(self, payload: EmailDraftCreate):
        organization = await self.org_repo.get(payload.organization_id)
        if organization is None:
            raise NotFoundError("Organization not found")

        template = await self.template_repo.get(payload.template_id)
        if template is None:
            raise NotFoundError("Template not found")

        rendered = self.draft_generator.render_factual_draft(
            organization,
            template,
            payload.model_dump(),
        )

        draft = await self.draft_repo.create(
            {
                "organization_id": organization.id,
                "subject": rendered["subject"],
                "body": rendered["body"],
                "status": DraftStatus.pending,
            }
        )
        await self.audit_repo.log(
            "draft_created",
            {"draft_id": draft.id, "organization_id": organization.id},
        )
        return draft

    async def review_draft(self, draft_id: int, payload: DraftReviewAction):
        draft = await self.draft_repo.get(draft_id)
        if draft is None:
            raise NotFoundError("Draft not found")

        if payload.status not in {
            DraftStatus.pending,
            DraftStatus.approved,
            DraftStatus.rejected,
            DraftStatus.declined,
            DraftStatus.sent,
        }:
            raise ConflictError("Invalid draft status")

        updated = await self.draft_repo.update(
            draft,
            {
                "subject": payload.subject or draft.subject,
                "body": payload.body or draft.body,
                "status": payload.status,
            },
        )
        await self.audit_repo.log(
            "draft_reviewed",
            {"draft_id": draft_id, "status": payload.status.value},
        )
        return updated

    async def list_drafts(self, status: DraftStatus | None = None):
        if status is not None:
            return await self.draft_repo.list_by_status(status)
        return await self.draft_repo.list(limit=500)

    async def dashboard(self) -> dict[str, int]:
        return await self.draft_repo.dashboard_metrics()

    async def list_audit_logs(self):
        return await self.audit_repo.list(limit=1_000)
