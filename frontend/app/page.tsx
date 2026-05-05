"use client";

import { useMemo, useState } from "react";
import { Loader2, SendHorizonal, TriangleAlert } from "lucide-react";
import { sendChatMessage } from "@/lib/api";

type ChatRole = "user" | "assistant";

type ChatMessage = {
  id: string;
  role: ChatRole;
  content: string;
};

function extractAssistantText(data: Record<string, unknown>) {
  const candidates = [
    data.response,
    data.answer,
    data.message,
    data.content,
    data.text,
  ];

  for (const candidate of candidates) {
    if (typeof candidate === "string" && candidate.trim()) {
      return candidate;
    }
  }

  return JSON.stringify(data, null, 2);
}

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "Central Brain online. Ask anything about project docs, team status, or uploaded knowledge.",
    },
  ]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canSend = useMemo(
    () => input.trim().length > 0 && !isSending,
    [input, isSending],
  );

  const onSend = async () => {
    const text = input.trim();
    if (!text || isSending) {
      return;
    }

    setError(null);
    setIsSending(true);
    setInput("");

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: text,
    };

    setMessages((prev) => [...prev, userMessage]);

    try {
      const result = await sendChatMessage(text);
      const assistantText = extractAssistantText(result);
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: assistantText,
        },
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected error.");
    } finally {
      setIsSending(false);
    }
  };

  const onSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    await onSend();
  };

  return (
    <section className="mx-auto flex h-[calc(100vh-3rem)] w-full max-w-5xl flex-col">
      <header className="mb-4">
        <h1 className="text-2xl font-semibold tracking-tight text-zinc-100">Chat Interface</h1>
        <p className="subtle-text mt-1 text-sm">RAG-powered assistant for team context and docs.</p>
      </header>

      <div className="panel flex flex-1 flex-col overflow-hidden">
        <div className="flex-1 space-y-4 overflow-y-auto p-4 sm:p-6">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`max-w-[92%] rounded-2xl px-4 py-3 text-sm leading-relaxed sm:max-w-[80%] ${
                message.role === "user"
                  ? "ml-auto bg-sky-500/20 text-sky-100"
                  : "bg-zinc-800/80 text-zinc-100"
              }`}
            >
              {message.content}
            </div>
          ))}
        </div>

        <div className="border-t border-zinc-800 p-3 sm:p-4">
          {error ? (
            <div className="mb-3 flex items-start gap-2 rounded-xl border border-rose-400/40 bg-rose-500/10 p-3 text-sm text-rose-200">
              <TriangleAlert className="mt-0.5 h-4 w-4 shrink-0" />
              <span>{error}</span>
            </div>
          ) : null}

          <form onSubmit={onSubmit} className="flex items-center gap-2">
            <input
              className="field"
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Ask Central Brain..."
              aria-label="Chat message"
            />
            <button
              type="submit"
              disabled={!canSend}
              className="inline-flex h-11 w-11 items-center justify-center rounded-xl bg-sky-500 text-zinc-950 transition hover:bg-sky-400 disabled:cursor-not-allowed disabled:opacity-50"
              aria-label="Send"
            >
              {isSending ? <Loader2 className="h-4 w-4 animate-spin" /> : <SendHorizonal className="h-4 w-4" />}
            </button>
          </form>
        </div>
      </div>
    </section>
  );
}
