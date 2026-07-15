import { useMemo } from "react";

import type { Draft } from "../types/api";

type Props = {
  drafts: Draft[];
  onUpdate: (draftId: number, status: Draft["status"]) => Promise<void>;
};

const reviewStatuses: Array<Draft["status"]> = ["approved", "rejected", "declined", "sent"];

export function DraftReviewQueue({ drafts, onUpdate }: Props): JSX.Element {
  const pending = useMemo(() => drafts.filter((draft) => draft.status === "pending"), [drafts]);

  return (
    <section className="card">
      <h3>Human Review Queue</h3>
      {pending.length === 0 ? <p>No pending drafts.</p> : null}
      {pending.map((draft) => (
        <article key={draft.id} className="draft-card">
          <h4>{draft.subject}</h4>
          <pre>{draft.body}</pre>
          <div className="button-row">
            {reviewStatuses.map((status) => (
              <button key={status} onClick={() => void onUpdate(draft.id, status)} type="button">
                {status}
              </button>
            ))}
          </div>
        </article>
      ))}
    </section>
  );
}
