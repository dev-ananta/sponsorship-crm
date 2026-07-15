import type { DashboardStats } from "../types/api";

type Props = { stats: DashboardStats };

const labels: Array<[keyof DashboardStats, string]> = [
  ["organizations_imported", "Organizations"],
  ["drafts_pending_review", "Pending Drafts"],
  ["approved_drafts", "Approved"],
  ["sent_emails", "Sent"],
  ["replies", "Replies"],
  ["declined_organizations", "Declined"],
];

export function KpiCards({ stats }: Props): JSX.Element {
  return (
    <section className="kpi-grid">
      {labels.map(([key, label]) => (
        <article key={key} className="card">
          <h3>{label}</h3>
          <p>{stats[key]}</p>
        </article>
      ))}
    </section>
  );
}
