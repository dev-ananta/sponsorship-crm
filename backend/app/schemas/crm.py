from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, HttpUrl

from app.models.crm import DraftStatus


class OrganizationBase(BaseModel):
    name: str
    website: HttpUrl
    mission: str | None = None
    description: str | None = None
    industry: str | None = None
    location: str | None = None
    public_email: EmailStr | None = None
    public_contact: str | None = None
    notes: str | None = None


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: str | None = None
    mission: str | None = None
    description: str | None = None
    industry: str | None = None
    location: str | None = None
    public_email: EmailStr | None = None
    public_contact: str | None = None
    notes: str | None = None


class OrganizationResponse(OrganizationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class DiscoveryRequest(BaseModel):
    urls: list[HttpUrl]


class EmailTemplateBase(BaseModel):
    name: str
    subject_blueprint: str
    body_blueprint: str


class EmailTemplateCreate(EmailTemplateBase):
    pass


class EmailTemplateResponse(EmailTemplateBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class EmailDraftCreate(BaseModel):
    organization_id: int
    template_id: int
    sender_name: str
    event: str
    request: str


class EmailDraftUpdate(BaseModel):
    subject: str | None = None
    body: str | None = None
    status: DraftStatus | None = None


class EmailDraftResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
    subject: str
    body: str
    status: DraftStatus
    created_at: datetime
    updated_at: datetime


class DashboardStats(BaseModel):
    organizations_imported: int
    drafts_pending_review: int
    approved_drafts: int
    sent_emails: int
    replies: int
    declined_organizations: int


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    action: str
    details: str
    created_at: datetime


class ImportSummary(BaseModel):
    imported: int
    skipped: int


class DraftReviewAction(BaseModel):
    subject: str | None = None
    body: str | None = None
    status: DraftStatus
