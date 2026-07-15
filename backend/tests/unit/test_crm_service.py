import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ConflictError, NotFoundError
from app.models.crm import DraftStatus
from app.schemas.crm import (
    DraftReviewAction,
    EmailDraftCreate,
    EmailTemplateCreate,
    OrganizationCreate,
    OrganizationUpdate,
)
from app.services.crm_service import CRMService


@pytest.mark.asyncio
async def test_crm_service_create_and_list_entities(session: AsyncSession) -> None:
    service = CRMService(session)

    org = await service.create_organization(
        OrganizationCreate(name="Team One", website="https://team1.org")
    )
    template = await service.create_template(
        EmailTemplateCreate(
            name="primary",
            subject_blueprint="Hello {{organization}}",
            body_blueprint="Mission {{mission}} Event {{event}} Request {{request}}",
        )
    )

    draft = await service.create_draft(
        EmailDraftCreate(
            organization_id=org.id,
            template_id=template.id,
            sender_name="Casey",
            event="Build Season",
            request="$200",
        )
    )

    assert draft.status == DraftStatus.pending
    assert len(await service.list_organizations()) == 1
    assert len(await service.list_templates()) == 1
    assert len(await service.list_drafts()) == 1


@pytest.mark.asyncio
async def test_crm_service_review_and_dashboard(session: AsyncSession) -> None:
    service = CRMService(session)
    org = await service.create_organization(
        OrganizationCreate(name="Team Two", website="https://team2.org")
    )
    template = await service.create_template(
        EmailTemplateCreate(
            name="reviewable",
            subject_blueprint="Hello {{organization}}",
            body_blueprint="Event {{event}} Request {{request}}",
        )
    )
    draft = await service.create_draft(
        EmailDraftCreate(
            organization_id=org.id,
            template_id=template.id,
            sender_name="Casey",
            event="Competition",
            request="$100",
        )
    )

    reviewed = await service.review_draft(
        draft.id,
        DraftReviewAction(status=DraftStatus.approved, subject="Approved", body="Body"),
    )

    assert reviewed.status == DraftStatus.approved
    assert len(await service.list_drafts(DraftStatus.approved)) == 1

    dashboard = await service.dashboard()
    assert dashboard["approved_drafts"] == 1


@pytest.mark.asyncio
async def test_crm_service_conflict_and_not_found_paths(session: AsyncSession) -> None:
    service = CRMService(session)

    await service.create_organization(
        OrganizationCreate(name="Team Three", website="https://team3.org")
    )

    with pytest.raises(ConflictError):
        await service.create_organization(
            OrganizationCreate(name="Team Three Again", website="https://team3.org")
        )

    with pytest.raises(NotFoundError):
        await service.update_organization(999, payload=OrganizationUpdate())

    with pytest.raises(NotFoundError):
        await service.review_draft(999, DraftReviewAction(status=DraftStatus.approved))


@pytest.mark.asyncio
async def test_crm_service_discovery_and_update(
    session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = CRMService(session)

    async def fake_extract(url: str) -> dict[str, str | None]:
        return {
            "name": "Found Org",
            "website": url,
            "mission": "Mission",
            "description": "Description",
            "industry": "Education",
            "location": "NYC",
            "public_email": "x@example.org",
            "public_contact": "Contact",
            "notes": "Public",
        }

    monkeypatch.setattr(service.scraper, "extract_profile", fake_extract)

    found = await service.discover_organizations(["https://found.org"])
    assert len(found) == 1
    assert found[0].name == "Found Org"

    updated = await service.update_organization(
        found[0].id,
        OrganizationUpdate(notes="Reviewed"),
    )
    assert updated.notes == "Reviewed"
