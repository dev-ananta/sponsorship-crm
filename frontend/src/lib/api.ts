import type { AuditLog, DashboardStats, Draft, EmailTemplate, Organization } from "../types/api";

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000/api/v1";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    ...init,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(body.detail ?? "Request failed");
  }

  return response.json() as Promise<T>;
}

export const api = {
  dashboard: () => request<DashboardStats>("/dashboard"),
  organizations: () => request<Organization[]>("/organizations"),
  templates: () => request<EmailTemplate[]>("/templates"),
  drafts: () => request<Draft[]>("/drafts"),
  auditLogs: () => request<AuditLog[]>("/audit-logs"),
  discover: (urls: string[]) => request<Organization[]>("/discovery", {
    method: "POST",
    body: JSON.stringify({ urls }),
  }),
  createTemplate: (payload: {
    name: string;
    subject_blueprint: string;
    body_blueprint: string;
  }) => request<EmailTemplate>("/templates", {
    method: "POST",
    body: JSON.stringify(payload),
  }),
  reviewDraft: (id: number, payload: { subject?: string; body?: string; status: string }) =>
    request<Draft>(`/drafts/${id}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),
};
