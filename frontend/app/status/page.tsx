"use client";

import { useState } from "react";
import { Loader2, TriangleAlert } from "lucide-react";
import { submitStatusUpdate } from "@/lib/api";

type StatusItem = {
  id: string;
  teammate: string;
  summary: string;
  risk: string;
};

const mockSummaries: StatusItem[] = [
  {
    id: "1",
    teammate: "Avery (Backend)",
    summary: "Integrated vector search and validated chunk retrieval latency under 300ms.",
    risk: "Need final API contract for status metadata.",
  },
  {
    id: "2",
    teammate: "Noel (Frontend)",
    summary: "Built chat and file upload workflows; mobile responsiveness in progress.",
    risk: "Pending final iconography pass.",
  },
  {
    id: "3",
    teammate: "Sam (Data)",
    summary: "Prepared seed knowledge docs and tested OCR pipeline for PDFs.",
    risk: "OCR quality drops on low contrast scans.",
  },
];

export default function StatusPage() {
  const [update, setUpdate] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmed = update.trim();

    if (!trimmed || isSubmitting) {
      return;
    }

    setError(null);
    setSuccess(null);
    setIsSubmitting(true);

    try {
      await submitStatusUpdate(trimmed);
      setSuccess("Status update submitted to backend.");
      setUpdate("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to submit update.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section className="mx-auto w-full max-w-5xl space-y-6">
      <header>
        <h1 className="text-2xl font-semibold tracking-tight text-zinc-100">Status Synthesis</h1>
        <p className="subtle-text mt-1 text-sm">Submit daily updates and review team-wide summaries.</p>
      </header>

      <div className="panel p-4 sm:p-6">
        <form onSubmit={handleSubmit} className="space-y-3">
          <label className="block text-sm font-medium text-zinc-300">Daily Update</label>
          <textarea
            className="field min-h-28 resize-y"
            value={update}
            onChange={(event) => setUpdate(event.target.value)}
            placeholder="Shipped X, blocked by Y, next focus is Z..."
          />
          <button
            type="submit"
            disabled={isSubmitting || !update.trim()}
            className="inline-flex items-center gap-2 rounded-xl bg-emerald-400 px-4 py-2 text-sm font-medium text-zinc-950 transition hover:bg-emerald-300 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isSubmitting ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
            Submit Update
          </button>
        </form>

        {error ? (
          <div className="mt-4 flex items-start gap-2 rounded-xl border border-rose-400/40 bg-rose-500/10 p-3 text-sm text-rose-200">
            <TriangleAlert className="mt-0.5 h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
        ) : null}

        {success ? (
          <div className="mt-4 rounded-xl border border-emerald-400/40 bg-emerald-500/10 p-3 text-sm text-emerald-200">
            {success}
          </div>
        ) : null}
      </div>

      <div className="panel p-4 sm:p-6">
        <h2 className="text-lg font-semibold text-zinc-100">Team Snapshot</h2>
        <div className="mt-4 space-y-3">
          {mockSummaries.map((item) => (
            <article key={item.id} className="rounded-xl border border-zinc-800 bg-zinc-900 p-4">
              <p className="text-sm font-medium text-zinc-200">{item.teammate}</p>
              <p className="mt-2 text-sm text-zinc-300">{item.summary}</p>
              <p className="mt-2 text-xs text-amber-300">Risk: {item.risk}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
