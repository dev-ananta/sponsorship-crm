import { useEffect, useState } from "react";

import { DiscoveryForm } from "./components/DiscoveryForm";
import { DraftReviewQueue } from "./components/DraftReviewQueue";
import { KpiCards } from "./components/KpiCards";
import { TemplateManager } from "./components/TemplateManager";
import { api } from "./lib/api";
import type { AuditLog, DashboardStats, Draft, EmailTemplate, Organization } from "./types/api";

const defaultStats: DashboardStats = {
  organizations_imported: 0,
  drafts_pending_review: 0,
  approved_drafts: 0,
  sent_emails: 0,
  replies: 0,
  declined_organizations: 0,
};

export default function App(): JSX.Element {
  const [stats, setStats] = useState<DashboardStats>(defaultStats);
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [templates, setTemplates] = useState<EmailTemplate[]>([]);
  const [drafts, setDrafts] = useState<Draft[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    try {
      const [dashboard, orgs, savedTemplates, reviewDrafts, logs] = await Promise.all([
        api.dashboard(),
        api.organizations(),
        api.templates(),
        api.drafts(),
        api.auditLogs(),
      ]);
      setStats(dashboard);
      setOrganizations(orgs);
      setTemplates(savedTemplates);
      setDrafts(reviewDrafts);
      setAuditLogs(logs.slice(0, 10));
      setError(null);
    } catch (fetchError) {
      setError(fetchError instanceof Error ? fetchError.message : "Failed loading data");
    }
  };

  useEffect(() => {
    void load();
  }, []);

  return (
    <main className="layout">
      <h1>Sponsorship CRM</h1>
      <p>Public-data-first sponsorship workflow for teams, clubs, and nonprofits.</p>
      {error ? <p className="error">{error}</p> : null}
      <KpiCards stats={stats} />
      <DiscoveryForm
        onSubmit={async (urls) => {
          await api.discover(urls);
          await load();
        }}
      />
      <TemplateManager
        templates={templates}
        onCreate={async (payload) => {
          await api.createTemplate(payload);
          await load();
        }}
      />
      <DraftReviewQueue
        drafts={drafts}
        onUpdate={async (id, status) => {
          await api.reviewDraft(id, { status });
          await load();
        }}
      />

      <section className="card">
        <h3>Organizations ({organizations.length})</h3>
        <ul>
          {organizations.map((org) => (
            <li key={org.id}>
              <a href={org.website} rel="noreferrer" target="_blank">
                {org.name}
              </a>
              {org.public_email ? ` • ${org.public_email}` : ""}
            </li>
          ))}
        </ul>
      </section>

      <section className="card">
        <h3>Recent Audit Logs</h3>
        <ul>
          {auditLogs.map((entry) => (
            <li key={entry.id}>
              {entry.action} — {entry.created_at}
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}
