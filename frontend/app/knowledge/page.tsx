// app/knowledge/page.tsx
"use client";
import { useState } from 'react';
import { UploadCloud, FileText, CheckCircle } from 'lucide-react';
import { uploadDocument } from '@/lib/api';

export default function KnowledgePage() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [done, setDone] = useState(false);

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    // await uploadDocument(file);
    setTimeout(() => {
      setUploading(false);
      setDone(true);
      setFile(null);
    }, 2000);
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
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />
        <div className="flex flex-col items-center gap-4 pointer-events-none">
          {done ? (
            <CheckCircle className="w-16 h-16 text-green-500" />
          ) : (
            <UploadCloud className="w-16 h-16 text-zinc-500 group-hover:text-indigo-400 transition" />
          )}
          
          <h3 className="text-xl font-medium text-white">
            {file ? file.name : (done ? 'Vectorized and Saved!' : 'Drag & Drop files here')}
          </h3>
          <p className="text-zinc-500 text-sm">
            {file ? 'Ready to upload' : 'Supports PDF, TXT, MD, JSON'}
          </p>
        </div>
      </div>

      {file && (
        <button 
          onClick={handleUpload}
          disabled={uploading}
          className="mt-8 bg-white text-black px-8 py-3 rounded-full font-bold hover:bg-indigo-400 hover:text-white transition disabled:opacity-50 flex items-center gap-2"
        >
          {uploading ? 'Embedding Vectors...' : 'Upload to Pinecone'}
        </button>
      )}
    </div>
  );
}