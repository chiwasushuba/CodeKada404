"use client";

import { useRef, useState } from "react";
import { FileUp, Loader2, TriangleAlert, Upload } from "lucide-react";
import { uploadKnowledgeFile } from "@/lib/api";

const acceptedExtensions = [".pdf", ".txt", ".md"];

export default function KnowledgePage() {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const onFileSelect = (fileList: FileList | null) => {
    const file = fileList?.[0] ?? null;
    setSelectedFile(file);
    setError(null);
    setSuccess(null);
  };

  const onUpload = async () => {
    if (!selectedFile || isUploading) {
      return;
    }

    setError(null);
    setSuccess(null);
    setIsUploading(true);

    try {
      const response = await uploadKnowledgeFile(selectedFile);
      const detail = typeof response.detail === "string" ? response.detail : "File uploaded successfully.";
      setSuccess(detail);
      setSelectedFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <section className="mx-auto w-full max-w-5xl space-y-6">
      <header>
        <h1 className="text-2xl font-semibold tracking-tight text-zinc-100">Knowledge Base Uploads</h1>
        <p className="subtle-text mt-1 text-sm">Ingest PDFs and text files to improve RAG responses.</p>
      </header>

      <div className="panel p-4 sm:p-6">
        <div className="rounded-2xl border border-dashed border-zinc-700 bg-zinc-900/80 p-6 text-center">
          <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-sky-500/15 text-sky-300">
            <FileUp className="h-6 w-6" />
          </div>
          <p className="text-sm text-zinc-200">Drop a file here or select one manually</p>
          <p className="mt-1 text-xs text-zinc-500">Accepted: {acceptedExtensions.join(", ")}</p>

          <input
            ref={fileInputRef}
            type="file"
            className="mt-4 block w-full text-sm text-zinc-300 file:mr-4 file:rounded-lg file:border-0 file:bg-zinc-800 file:px-3 file:py-2 file:text-sm file:font-medium file:text-zinc-200 hover:file:bg-zinc-700"
            accept={acceptedExtensions.join(",")}
            onChange={(event) => onFileSelect(event.target.files)}
          />
        </div>

        {selectedFile ? (
          <div className="mt-4 rounded-xl border border-zinc-700 bg-zinc-900 p-3 text-sm text-zinc-200">
            Selected: {selectedFile.name}
          </div>
        ) : null}

        <button
          onClick={onUpload}
          disabled={!selectedFile || isUploading}
          className="mt-4 inline-flex items-center gap-2 rounded-xl bg-sky-400 px-4 py-2 text-sm font-semibold text-zinc-950 transition hover:bg-sky-300 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isUploading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Upload className="h-4 w-4" />}
          Upload to Knowledge Base
        </button>

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
    </section>
  );
}
