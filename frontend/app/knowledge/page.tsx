// app/knowledge/page.tsx
"use client";
import { useEffect, useState } from 'react';
import { UploadCloud, FileText, CheckCircle, X } from 'lucide-react';
import { deleteUploadedFile, getUploadedFiles, uploadDocument } from '@/lib/api';

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
      setUploadedFiles(response.files ?? []);
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
      setUploadedFiles((previousFiles) => previousFiles.filter((file) => file.r2_path !== r2Path));
    } catch (deleteError) {
      setError(deleteError instanceof Error ? deleteError.message : 'Failed to delete file.');
    } finally {
      setDeletingPath(null);
    }
  };

  return (
    <div className="h-full w-full bg-zinc-900 flex flex-col justify-center items-center p-6">
      <div className="text-center mb-10">
        <h1 className="text-3xl font-bold text-white mb-2">Feed the Brain</h1>
        <p className="text-zinc-400">Upload documentation, API specs, or PR notes to build the context.</p>
      </div>

      <div className="w-full max-w-xl bg-zinc-900/50 border-2 border-dashed border-zinc-700 rounded-3xl p-10 text-center hover:border-indigo-500 transition group relative">
        <input 
          type="file" 
          multiple
          onChange={handleFileChange}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />
        <div className="flex flex-col items-center gap-4 pointer-events-none">
          {done ? (
            <CheckCircle className="w-16 h-16 text-green-500" />
          ) : (
            <UploadCloud className="w-16 h-16 text-zinc-500 group-hover:text-indigo-400 transition" />
          )}
          
          <h3 className="text-xl font-medium text-white">
            {files.length > 0
              ? `${files.length} file${files.length === 1 ? '' : 's'} selected`
              : done
                ? 'Vectorized and Saved!'
                : 'Drag & Drop files here'}
          </h3>
          <p className="text-zinc-500 text-sm">
            {files.length > 0 ? 'Ready to upload' : 'Supports PDF and TXT'}
          </p>
        </div>
      </div>

      {files.length > 0 && (
        <div className="mt-6 w-full max-w-xl rounded-2xl border border-white/10 bg-zinc-800/50 p-4 text-left">
          <p className="text-sm font-medium text-zinc-300 mb-3 flex items-center gap-2">
            <FileText className="w-4 h-4" />
            Selected files
          </p>
          <div className="space-y-2 max-h-40 overflow-y-auto pr-1">
            {files.map((file) => (
              <div key={`${file.name}-${file.size}-${file.lastModified}`} className="flex items-center justify-between rounded-xl bg-zinc-900 px-3 py-2 text-sm text-zinc-200">
                <span className="truncate">{file.name}</span>
                <span className="ml-3 shrink-0 text-zinc-500">{Math.max(1, Math.round(file.size / 1024))} KB</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {error && (
        <p className="mt-4 max-w-xl text-sm text-red-400">{error}</p>
      )}

      <div className="mt-10 w-full max-w-4xl rounded-3xl border border-white/10 bg-zinc-900/70 p-6 text-left">
        <div className="flex items-center justify-between gap-4 mb-4">
          <div>
            <h2 className="text-xl font-semibold text-white">Already Uploaded</h2>
            <p className="text-sm text-zinc-400">Files currently stored in R2 and indexed by the backend.</p>
          </div>
          <div className="text-sm text-zinc-500">
            {loadingFiles ? 'Loading...' : `${uploadedFiles.length} file${uploadedFiles.length === 1 ? '' : 's'}`}
          </div>
        </div>

        <div className="space-y-3 max-h-96 overflow-y-auto pr-1">
          {uploadedFiles.length === 0 && !loadingFiles ? (
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

      {files.length > 0 && (
        <button 
          onClick={handleUpload}
          disabled={uploading}
          className="mt-8 bg-white text-black px-8 py-3 rounded-full font-bold hover:bg-indigo-400 hover:text-white transition disabled:opacity-50 flex items-center gap-2"
        >
          {uploading
            ? `Uploading ${files.length} file${files.length === 1 ? '' : 's'}...`
            : `Upload ${files.length} file${files.length === 1 ? '' : 's'} to Pinecone`}
        </button>
      )}
    </div>
  );
}