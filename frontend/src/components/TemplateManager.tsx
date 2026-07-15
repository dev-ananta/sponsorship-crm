import { FormEvent, useState } from "react";

import type { EmailTemplate } from "../types/api";

type Props = {
  templates: EmailTemplate[];
  onCreate: (payload: {
    name: string;
    subject_blueprint: string;
    body_blueprint: string;
  }) => Promise<void>;
};

export function TemplateManager({ templates, onCreate }: Props): JSX.Element {
  const [name, setName] = useState("");
  const [subject, setSubject] = useState("Partnership Opportunity with {{organization}}");
  const [body, setBody] = useState(
    "Hi {{organization}},\n\nI reviewed your public mission statement{{ ': ' + mission if mission else '' }} and would like to ask about sponsoring {{event}}.\n\nOur request: {{request}}\n\nBest,\n{{sender_name}}"
  );

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!name.trim()) {
      return;
    }
    await onCreate({
      name,
      subject_blueprint: subject,
      body_blueprint: body,
    });
    setName("");
  };

  return (
    <section className="card">
      <h3>Email Templates</h3>
      <form onSubmit={submit}>
        <input value={name} placeholder="Template name" onChange={(event) => setName(event.target.value)} />
        <input value={subject} onChange={(event) => setSubject(event.target.value)} />
        <textarea rows={6} value={body} onChange={(event) => setBody(event.target.value)} />
        <button type="submit">Save Template</button>
      </form>
      <ul>
        {templates.map((template) => (
          <li key={template.id}>
            <strong>{template.name}</strong> — {template.subject_blueprint}
          </li>
        ))}
      </ul>
    </section>
  );
}
