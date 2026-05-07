// app/knowledge/page.tsx
"use client";
import { useEffect, useState } from 'react';
import { UploadCloud, FileText, CheckCircle, X } from 'lucide-react';
import { deleteUploadedFile, getUploadedFiles, uploadDocument } from '../../library/api';

type UploadedFileItem = {
  file_name: string;
  r2_path: string;
  size: number;
  uploaded_at: string;
};

export default function KnowledgePage() {
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFileItem[]>([]);
  const [loadingFiles, setLoadingFiles] = useState(true);
  const [deletingPath, setDeletingPath] = useState<string | null>(null);

  const loadUploadedFiles = async () => {
    setLoadingFiles(true);
    try {
      const response = await getUploadedFiles();
      const responseFiles = response.files ?? [];

      // Deduplicate by r2_path, keeping the most recently uploaded entry when duplicates exist.
      const map = new Map<string, UploadedFileItem>();
      for (const f of responseFiles) {
        const existing = map.get(f.r2_path);
        if (!existing) {
          map.set(f.r2_path, f);
        } else {
          const existingDate = new Date(existing.uploaded_at).getTime();
          const newDate = new Date(f.uploaded_at).getTime();
          if (newDate > existingDate) map.set(f.r2_path, f);
        }
      }

      setUploadedFiles(Array.from(map.values()));
    } catch (fetchError) {
      setError(fetchError instanceof Error ? fetchError.message : 'Failed to load uploaded files.');
    } finally {
      setLoadingFiles(false);
    }
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(event.target.files ?? []);

    if (selectedFiles.length === 0) {
      return;
    }

    setFiles((previousFiles) => {
      const nextFiles = [...previousFiles, ...selectedFiles];
      const uniqueFiles = new Map(
        nextFiles.map((file) => [`${file.name}-${file.size}-${file.lastModified}`, file])
      );
      return Array.from(uniqueFiles.values());
    });
    setDone(false);
    setError(null);
    event.target.value = '';
  };

  const handleUpload = async () => {
    if (files.length === 0) return;

    setUploading(true);
    setDone(false);
    setError(null);

    try {
      await uploadDocument(files);

      setDone(true);
      setFiles([]);
      await loadUploadedFiles();
    } catch (error) {
      const message = error instanceof Error ? error.message : 'One or more uploads failed.';
      setError(message);
    } finally {
      setUploading(false);
    }
  };

  useEffect(() => {
    loadUploadedFiles();
  }, []);

  const handleDeleteFile = async (r2Path: string) => {
    setDeletingPath(r2Path);
    setError(null);

    try {
      await deleteUploadedFile(r2Path);
      await loadUploadedFiles();
    } catch (deleteError) {
      setError(deleteError instanceof Error ? deleteError.message : 'Failed to delete file.');
    } finally {
      setDeletingPath(null);
    }
  };

  return (
    <div className="min-h-full w-full bg-zinc-900 px-6 py-8 lg:px-10">
      <div className="mx-auto flex w-full max-w-5xl flex-col gap-8">
        <div className="text-center">
          <h1 className="mb-2 text-3xl font-bold text-white">Feed the Brain</h1>
          <p className="text-zinc-400">Upload documentation, API specs, or PR notes to build the context.</p>
        </div>

        <div className="group relative w-full rounded-3xl border-2 border-dashed border-zinc-700 bg-zinc-900/50 p-10 text-center transition hover:border-indigo-500">
          <input 
            type="file" 
            multiple
            onChange={handleFileChange}
            className="absolute inset-0 h-full w-full cursor-pointer opacity-0"
          />
          <div className="pointer-events-none flex flex-col items-center gap-4">
            {done ? (
              <CheckCircle className="h-16 w-16 text-green-500" />
            ) : (
              <UploadCloud className="h-16 w-16 text-zinc-500 transition group-hover:text-indigo-400" />
            )}

            <h3 className="text-xl font-medium text-white">
              {files.length > 0
                ? `${files.length} file${files.length === 1 ? '' : 's'} selected`
                : done
                  ? 'Vectorized and Saved!'
                  : 'Drag & Drop files here'}
            </h3>
            <p className="text-sm text-zinc-500">
              {files.length > 0 ? 'Ready to upload' : 'Supports PDF and TXT'}
            </p>
          </div>
        </div>

        <div className="rounded-2xl border border-white/10 bg-zinc-800/50 p-4 text-left">
          <p className="mb-3 flex items-center gap-2 text-sm font-medium text-zinc-300">
            <FileText className="h-4 w-4" />
            Selected files
          </p>
          {files.length > 0 ? (
            <div className="max-h-40 space-y-2 overflow-y-auto pr-1">
              {files.map((file) => (
                <div key={`${file.name}-${file.size}-${file.lastModified}`} className="flex items-center justify-between rounded-xl bg-zinc-900 px-3 py-2 text-sm text-zinc-200">
                  <span className="truncate">{file.name}</span>
                  <span className="ml-3 shrink-0 text-zinc-500">{Math.max(1, Math.round(file.size / 1024))} KB</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="rounded-xl border border-dashed border-zinc-700 px-4 py-6 text-sm text-zinc-500">
              No files selected yet.
            </div>
          )}

          {files.length > 0 && (
            <button 
              onClick={handleUpload}
              disabled={uploading}
              className="mx-auto mt-4 flex items-center justify-center gap-2 rounded-full bg-white px-8 py-3 font-bold text-black transition hover:bg-indigo-400 hover:text-white disabled:opacity-50"
            >
              {uploading
                ? `Uploading ${files.length} file${files.length === 1 ? '' : 's'}...`
                : `Upload ${files.length} file${files.length === 1 ? '' : 's'} to Pinecone`}
            </button>
          )}

          {error && (
            <p className="mt-3 max-w-xl text-sm text-red-400">{error}</p>
          )}
        </div>

        <div className="rounded-3xl border border-white/10 bg-zinc-900/70 p-6 text-left">
          <div className="mb-4 flex items-center justify-between gap-4">
            <div>
              <h2 className="text-xl font-semibold text-white">Already Uploaded</h2>
              <p className="text-sm text-zinc-400">Files currently stored in R2 and indexed by the backend.</p>
            </div>
            <div className="text-sm text-zinc-500">
              {loadingFiles ? 'Refreshing list...' : `${uploadedFiles.length} file${uploadedFiles.length === 1 ? '' : 's'}`}
            </div>
          </div>

          <div className="space-y-3 max-h-96 overflow-y-auto pr-1">
            {loadingFiles ? (
              <div className="space-y-3 rounded-2xl border border-dashed border-zinc-700 px-4 py-6">
                <div className="h-4 w-1/3 animate-pulse rounded bg-zinc-700/70" />
                <div className="h-10 animate-pulse rounded-xl bg-zinc-800/80" />
                <div className="h-10 animate-pulse rounded-xl bg-zinc-800/80" />
                <div className="h-10 animate-pulse rounded-xl bg-zinc-800/80" />
                <p className="pt-2 text-sm text-zinc-500">Updating uploaded files...</p>
              </div>
            ) : uploadedFiles.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-zinc-700 px-4 py-6 text-sm text-zinc-500">
                No uploaded files found yet.
              </div>
            ) : null}

            {uploadedFiles.map((file) => (
              <div key={file.r2_path} className="flex flex-col gap-2 rounded-2xl border border-white/10 bg-zinc-950 px-4 py-4 sm:flex-row sm:items-center sm:justify-between">
                <div className="min-w-0 pr-8">
                  <p className="truncate text-sm font-medium text-zinc-100">{file.file_name}</p>
                  <p className="truncate text-xs text-zinc-500">{file.r2_path}</p>
                </div>
                <div className="flex items-center gap-3 text-xs text-zinc-400">
                  <span>{Math.max(1, Math.round(file.size / 1024))} KB</span>
                  <span>{new Date(file.uploaded_at).toLocaleString()}</span>
                  <button
                    type="button"
                    onClick={() => handleDeleteFile(file.r2_path)}
                    disabled={deletingPath === file.r2_path}
                    className="inline-flex h-8 w-8 items-center justify-center rounded-full border border-white/10 text-zinc-400 transition hover:border-red-400 hover:text-red-300 disabled:cursor-not-allowed disabled:opacity-50"
                    aria-label={`Delete ${file.file_name}`}
                    title={`Delete ${file.file_name}`}
                  >
                    {deletingPath === file.r2_path ? (
                      <span className="text-[10px]">...</span>
                    ) : (
                      <X className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}