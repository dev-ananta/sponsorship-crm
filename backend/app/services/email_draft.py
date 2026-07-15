from jinja2 import Environment, StrictUndefined

from app.core.errors import AppError
from app.models.crm import EmailTemplate, Organization


class DraftGenerationService:
    def render_factual_draft(
        self,
        organization: Organization,
        template: EmailTemplate,
        variables: dict[str, str],
    ) -> dict[str, str]:
        context = {
            "organization": organization.name,
            "website": organization.website,
            "mission": organization.mission,
            "sender_name": variables["sender_name"],
            "event": variables["event"],
            "request": variables["request"],
        }

        for key in ("organization", "website", "sender_name", "event", "request"):
            if not context.get(key):
                raise AppError(f"Missing required draft field: {key}")

        subject = Environment(undefined=StrictUndefined).from_string(
            template.subject_blueprint
        )
        body = Environment(undefined=StrictUndefined).from_string(
            template.body_blueprint
        )

        return {"subject": subject.render(context), "body": body.render(context)}
