import { FormEvent, useState } from "react";

type Props = {
  onSubmit: (urls: string[]) => Promise<void>;
};

export function DiscoveryForm({ onSubmit }: Props): JSX.Element {
  const [input, setInput] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const urls = input
      .split("\n")
      .map((line) => line.trim())
      .filter(Boolean);

    if (urls.length === 0) {
      return;
    }

    setSubmitting(true);
    try {
      await onSubmit(urls);
      setInput("");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form className="card" onSubmit={submit}>
      <h3>Organization Discovery</h3>
      <label htmlFor="urls">One URL per line</label>
      <textarea
        id="urls"
        rows={4}
        value={input}
        onChange={(event) => setInput(event.target.value)}
        placeholder="https://example.org"
      />
      <button disabled={submitting} type="submit">
        {submitting ? "Importing..." : "Discover Organizations"}
      </button>
    </form>
  );
}
