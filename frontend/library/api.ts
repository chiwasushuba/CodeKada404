// lib/api.ts
const API_URL = '';

export type KnowledgeFile = {
  id: string;
  filename: string;
  r2_path: string;
  ai_context: string;
  is_verified: boolean;
};

export async function sendChatMessage(message: string) {
  const res = await fetch(`${API_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question: message }),
  });
  if (!res.ok) {
    let detail = 'Chat request failed';
    try {
      const errorPayload = await res.json();
      if (typeof errorPayload?.detail === 'string') {
        detail = errorPayload.detail;
      }
    } catch {
      detail = `Chat request failed with status ${res.status}`;
    }
    throw new Error(detail);
  }
  return res.json();
}

export async function submitStatus(text: string) {
  const res = await fetch(`${API_URL}/api/status`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) throw new Error('API Error');
  return res.json();
}

export async function uploadDocument(files: File[]) {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append('files', file);
  });
  
  const res = await fetch(`${API_URL}/api/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    let detail = 'Upload failed';
    try {
      const errorPayload = await res.json();
      if (typeof errorPayload?.detail === 'string') {
        detail = errorPayload.detail;
      }
    } catch {
      detail = `Upload failed with status ${res.status}`;
    }
    throw new Error(detail);
  }
  return res.json();
}

export async function getUploadedFiles() {
  const res = await fetch(`${API_URL}/api/upload/files`, {
    method: 'GET',
  });

  if (!res.ok) {
    let detail = 'Failed to load uploaded files';
    try {
      const errorPayload = await res.json();
      if (typeof errorPayload?.detail === 'string') {
        detail = errorPayload.detail;
      }
    } catch {
      detail = `Failed to load uploaded files with status ${res.status}`;
    }
    throw new Error(detail);
  }

  return res.json();
}

export async function deleteUploadedFile(r2Path: string) {
  const res = await fetch(`/api/upload/files?r2_path=${encodeURIComponent(r2Path)}`, {
    method: 'DELETE',
  });

  if (!res.ok) {
    let detail = 'Failed to delete uploaded file';
    try {
      const errorPayload = await res.json();
      if (typeof errorPayload?.detail === 'string') {
        detail = errorPayload.detail;
      }
    } catch {
      detail = `Failed to delete uploaded file with status ${res.status}`;
    }
    throw new Error(detail);
  }

  return res.json();
}

export async function getKnowledgeFiles(): Promise<{ files: KnowledgeFile[]; total_files: number; status: string }> {
  const res = await fetch(`${API_URL}/api/knowledge`, {
    method: 'GET',
  });

  if (!res.ok) {
    let detail = 'Failed to load knowledge files';
    try {
      const errorPayload = await res.json();
      if (typeof errorPayload?.detail === 'string') {
        detail = errorPayload.detail;
      }
    } catch {
      detail = `Failed to load knowledge files with status ${res.status}`;
    }
    throw new Error(detail);
  }

  return res.json();
}

export async function verifyFileContext(fileId: string): Promise<{ id: string; is_verified: boolean; status: string }> {
  const res = await fetch(`${API_URL}/api/knowledge/${fileId}/verify`, {
    method: 'PATCH',
  });

  if (!res.ok) {
    let detail = 'Failed to verify context';
    try {
      const errorPayload = await res.json();
      if (typeof errorPayload?.detail === 'string') {
        detail = errorPayload.detail;
      }
    } catch {
      detail = `Failed to verify context with status ${res.status}`;
    }
    throw new Error(detail);
  }

  return res.json();
}

export async function updateFileContext(fileId: string, manualContext: string): Promise<{ id: string; ai_context: string; is_verified: boolean; status: string; reembedded_chunks: number }> {
  const res = await fetch(`${API_URL}/api/knowledge/${fileId}/update-context`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ manual_context: manualContext }),
  });

  if (!res.ok) {
    let detail = 'Failed to update context';
    try {
      const errorPayload = await res.json();
      if (typeof errorPayload?.detail === 'string') {
        detail = errorPayload.detail;
      }
    } catch {
      detail = `Failed to update context with status ${res.status}`;
    }
    throw new Error(detail);
  }

  return res.json();
}

export async function deleteKnowledgeFileContext(fileId: string): Promise<{ id: string; r2_path: string; deleted_vectors: number; status: string }> {
  const res = await fetch(`${API_URL}/api/knowledge/${fileId}`, {
    method: 'DELETE',
  });

  if (!res.ok) {
    let detail = 'Failed to delete context';
    try {
      const errorPayload = await res.json();
      if (typeof errorPayload?.detail === 'string') {
        detail = errorPayload.detail;
      }
    } catch {
      detail = `Failed to delete context with status ${res.status}`;
    }
    throw new Error(detail);
  }

  return res.json();
}