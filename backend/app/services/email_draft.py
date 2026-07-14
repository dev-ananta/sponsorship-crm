from jinja2 import Template
from app.models.crm import Organization, EmailTemplate


class DraftGenerationService:
    @staticmethod
    def render_factual_draft(organization: Organization, template: EmailTemplate, variables: dict) -> dict:
        """Renders an outreach blueprint strictly injecting found organizational telemetry."""
        
        context = {
            "organization": organization.name,
            "website": organization.website,
            "mission": organization.mission or "your corporate initiatives",
            "sender_name": variables.get("sender_name", "Our Team"),
            "event": variables.get("event", "our seasonal activities"),
            "request": variables.get("request", "sponsorship collaboration")
        }

        subject_template = Template(template.subject_blueprint)
        body_template = Template(template.body_blueprint)

        return {
            "subject": subject_template.render(context),
            "body": body_template.render(context)
        }
