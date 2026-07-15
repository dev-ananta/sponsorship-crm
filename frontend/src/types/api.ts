export type Organization = {
  id: number;
  name: string;
  website: string;
  mission?: string | null;
  description?: string | null;
  industry?: string | null;
  location?: string | null;
  public_email?: string | null;
  public_contact?: string | null;
  notes?: string | null;
  created_at: string;
  updated_at: string;
};

export type EmailTemplate = {
  id: number;
  name: string;
  subject_blueprint: string;
  body_blueprint: string;
  created_at: string;
};

export type Draft = {
  id: number;
  organization_id: number;
  subject: string;
  body: string;
  status: "pending" | "approved" | "rejected" | "sent" | "declined";
  created_at: string;
  updated_at: string;
};

export type DashboardStats = {
  organizations_imported: number;
  drafts_pending_review: number;
  approved_drafts: number;
  sent_emails: number;
  replies: number;
  declined_organizations: number;
};

export type AuditLog = {
  id: number;
  action: string;
  details: string;
  created_at: string;
};
