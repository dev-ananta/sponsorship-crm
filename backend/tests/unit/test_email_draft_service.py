import pytest

from app.models.crm import EmailTemplate, Organization
from app.services.email_draft import DraftGenerationService


@pytest.fixture
def organization() -> Organization:
    return Organization(
        id=1,
        name="Robotics Club",
        website="https://robotics.example.org",
        mission="Support student robotics education.",
    )


@pytest.fixture
def template() -> EmailTemplate:
    return EmailTemplate(
        id=1,
        name="standard",
        subject_blueprint="Support {{organization}}",
        body_blueprint="Mission: {{mission}} | Event: {{event}} | Request: {{request}}",
    )


def test_render_factual_draft_uses_only_context(
    organization: Organization, template: EmailTemplate
) -> None:
    service = DraftGenerationService()

    result = service.render_factual_draft(
        organization,
        template,
        {
            "sender_name": "Avery",
            "event": "Robotics Expo",
            "request": "$500 for parts",
        },
    )

    assert result["subject"] == "Support Robotics Club"
    assert "Mission: Support student robotics education." in result["body"]
    assert "Event: Robotics Expo" in result["body"]


def test_render_factual_draft_requires_context(
    organization: Organization, template: EmailTemplate
) -> None:
    service = DraftGenerationService()

    with pytest.raises(KeyError):
        service.render_factual_draft(
            organization,
            template,
            {
                "sender_name": "Avery",
                "event": "Robotics Expo",
            },
        )
