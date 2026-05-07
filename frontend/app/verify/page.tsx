"use client";

import { useEffect, useMemo, useState } from 'react';
import { Check, FileText, Pencil, RefreshCcw, Save, X } from 'lucide-react';
import {
  getKnowledgeFiles,
  KnowledgeFile,
  updateFileContext,
  verifyFileContext,
} from '../../lib/api';

type EditingState = {
  [fileId: string]: {
    open: boolean;
    value: string;
  };
};

export default function VerifyPage() {
  const [files, setFiles] = useState<KnowledgeFile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editing, setEditing] = useState<EditingState>({});
  const [verifyingId, setVerifyingId] = useState<string | null>(null);
  const [savingId, setSavingId] = useState<string | null>(null);

  const loadKnowledgeFiles = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await getKnowledgeFiles();
      setFiles(response.files ?? []);

      setEditing((prev) => {
        const next: EditingState = { ...prev };
        for (const file of response.files ?? []) {
          if (!next[file.id]) {
            next[file.id] = { open: false, value: file.ai_context };
          } else if (!next[file.id].open) {
            next[file.id] = { open: false, value: file.ai_context };
          }
        }
        return next;
      });
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'Failed to load contexts.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadKnowledgeFiles();
  }, []);

  const sortedFiles = useMemo(() => {
    return [...files].sort((a, b) => Number(a.is_verified) - Number(b.is_verified));
  }, [files]);

  const handleVerify = async (fileId: string) => {
    setVerifyingId(fileId);
    setError(null);

    try {
      await verifyFileContext(fileId);
      setFiles((prev) => prev.map((file) => (file.id === fileId ? { ...file, is_verified: true } : file)));
    } catch (verifyError) {
      setError(verifyError instanceof Error ? verifyError.message : 'Failed to verify context.');
    } finally {
      setVerifyingId(null);
    }
  };

  const openEditor = (file: KnowledgeFile) => {
    setEditing((prev) => ({
      ...prev,
      [file.id]: { open: true, value: prev[file.id]?.value ?? file.ai_context },
    }));
  };

  const cancelEditor = (file: KnowledgeFile) => {
    setEditing((prev) => ({
      ...prev,
      [file.id]: { open: false, value: file.ai_context },
    }));
  };

  const onChangeEditor = (fileId: string, value: string) => {
    setEditing((prev) => ({
      ...prev,
      [fileId]: { open: true, value },
    }));
  };

  const handleSaveContext = async (file: KnowledgeFile) => {
    const updatedContext = editing[file.id]?.value?.trim() ?? '';
    if (!updatedContext) {
      setError('Manual context cannot be empty.');
      return;
    }

    setSavingId(file.id);
    setError(null);

    try {
      await updateFileContext(file.id, updatedContext);
      await loadKnowledgeFiles();
      setEditing((prev) => ({
        ...prev,
        [file.id]: { open: false, value: updatedContext },
      }));
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : 'Failed to update context.');
    } finally {
      setSavingId(null);
    }
  };

  return (
    <div className="min-h-full bg-zinc-900 px-6 py-8 text-zinc-100 md:px-10">
      <div className="mx-auto max-w-6xl">
        <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-indigo-300/90">Central Brain</p>
            <h1 className="text-3xl font-bold text-white md:text-4xl">Context Verification</h1>
            <p className="mt-2 text-zinc-400">
              Review generated context, verify trusted summaries, and correct misunderstandings before retrieval.
            </p>
          </div>
          <button
            type="button"
            onClick={() => void loadKnowledgeFiles()}
            className="inline-flex items-center gap-2 rounded-xl border border-indigo-500/40 bg-indigo-500/10 px-4 py-2 text-sm font-semibold text-indigo-200 transition hover:bg-indigo-500/20"
          >
            <RefreshCcw className="h-4 w-4" />
            Refresh
          </button>
        </div>

        {error ? (
          <div className="mb-6 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-200">
            {error}
          </div>
        ) : null}

        {loading ? (
          <div className="rounded-2xl border border-white/10 bg-zinc-950/60 px-6 py-10 text-zinc-400">
            Loading context records...
          </div>
        ) : null}

        {!loading && sortedFiles.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-zinc-700 bg-zinc-950/40 px-6 py-10 text-zinc-400">
            No uploaded files found. Add documents in the Knowledge Base first.
          </div>
        ) : null}

        {!loading ? (
          <div className="grid gap-5">
            {sortedFiles.map((file) => {
              const editState = editing[file.id] ?? { open: false, value: file.ai_context };
              const isSaving = savingId === file.id;
              const isVerifying = verifyingId === file.id;

              return (
                <article
                  key={file.id}
                  className="rounded-2xl border border-white/10 bg-gradient-to-br from-zinc-950 via-zinc-900 to-slate-900/70 p-5 shadow-[0_0_0_1px_rgba(255,255,255,0.02)]"
                >
                  <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                    <div className="min-w-0">
                      <div className="mb-2 inline-flex items-center gap-2 rounded-full border border-indigo-400/30 bg-indigo-400/10 px-3 py-1 text-xs font-semibold text-indigo-200">
                        <FileText className="h-3.5 w-3.5" />
                        Context File
                      </div>
                      <h2 className="truncate text-lg font-semibold text-white">{file.filename}</h2>
                    </div>
                    <span
                      className={`inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs font-semibold ${
                        file.is_verified
                          ? 'border border-emerald-400/30 bg-emerald-500/10 text-emerald-200'
                          : 'border border-amber-400/30 bg-amber-500/10 text-amber-200'
                      }`}
                    >
                      {file.is_verified ? <Check className="h-3.5 w-3.5" /> : <X className="h-3.5 w-3.5" />}
                      {file.is_verified ? 'Verified' : 'Needs Review'}
                    </span>
                  </div>

                  <div className="rounded-xl border border-white/10 bg-zinc-950/70 p-4 text-sm leading-7 text-zinc-200">
                    {file.ai_context || 'No AI context available yet.'}
                  </div>

                  <div className="mt-4 flex flex-wrap items-center gap-3">
                    <button
                      type="button"
                      onClick={() => void handleVerify(file.id)}
                      disabled={file.is_verified || isVerifying || isSaving}
                      className={`inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold transition ${
                        file.is_verified
                          ? 'cursor-default border border-emerald-500/30 bg-emerald-500/15 text-emerald-200'
                          : 'border border-zinc-700 bg-zinc-800 text-zinc-200 hover:border-emerald-400/60 hover:bg-emerald-500/15'
                      } disabled:opacity-60`}
                    >
                      <Check className="h-4 w-4" />
                      {file.is_verified ? 'Context Verified' : isVerifying ? 'Verifying...' : 'Verify Context'}
                    </button>

                    <button
                      type="button"
                      onClick={() => openEditor(file)}
                      disabled={isSaving || isVerifying}
                      className="inline-flex items-center gap-2 rounded-lg border border-zinc-700 bg-zinc-800 px-4 py-2 text-sm font-semibold text-zinc-200 transition hover:border-indigo-400/60 hover:text-indigo-200 disabled:opacity-60"
                    >
                      <Pencil className="h-4 w-4" />
                      Edit Context
                    </button>
                  </div>

                  {editState.open ? (
                    <div className="mt-4 rounded-xl border border-indigo-500/30 bg-zinc-900/80 p-4">
                      <label className="mb-2 block text-xs font-semibold uppercase tracking-[0.15em] text-indigo-200">
                        Manual Context Override
                      </label>
                      <textarea
                        value={editState.value}
                        onChange={(event) => onChangeEditor(file.id, event.target.value)}
                        className="min-h-40 w-full rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-100 outline-none ring-indigo-400/40 transition focus:border-indigo-400 focus:ring"
                        placeholder="Correct the context here..."
                      />

                      <div className="mt-3 flex flex-wrap gap-3">
                        <button
                          type="button"
                          onClick={() => void handleSaveContext(file)}
                          disabled={isSaving}
                          className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-indigo-500 disabled:opacity-60"
                        >
                          <Save className="h-4 w-4" />
                          {isSaving ? 'Saving...' : 'Save & Re-embed'}
                        </button>
                        <button
                          type="button"
                          onClick={() => cancelEditor(file)}
                          disabled={isSaving}
                          className="inline-flex items-center gap-2 rounded-lg border border-zinc-700 bg-zinc-800 px-4 py-2 text-sm font-semibold text-zinc-200 transition hover:border-zinc-500 disabled:opacity-60"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : null}
                </article>
              );
            })}
          </div>
        ) : null}
      </div>
    </div>
  );
}
