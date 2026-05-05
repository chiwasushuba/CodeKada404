"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BrainCircuit, Files, LayoutDashboard, MessageSquare } from "lucide-react";

type NavItem = {
  label: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
};

const navItems: NavItem[] = [
  { label: "Chat", href: "/", icon: MessageSquare },
  { label: "Status Dashboard", href: "/status", icon: LayoutDashboard },
  { label: "Knowledge Base", href: "/knowledge", icon: Files },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="sticky top-0 hidden h-screen w-72 shrink-0 border-r border-zinc-800/80 bg-zinc-950/90 p-5 md:block">
      <div className="panel flex h-full flex-col p-4">
        <div className="mb-6 flex items-center gap-3 rounded-xl border border-zinc-800 bg-zinc-900 p-3">
          <div className="rounded-lg bg-sky-500/20 p-2 text-sky-300">
            <BrainCircuit className="h-5 w-5" />
          </div>
          <div>
            <p className="text-sm font-semibold tracking-wide text-zinc-200">Central Brain</p>
            <p className="text-xs text-zinc-500">RAG Console</p>
          </div>
        </div>

        <nav className="space-y-2">
          {navItems.map((item) => {
            const isActive =
              item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
            const Icon = item.icon;

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition ${
                  isActive
                    ? "bg-sky-500/20 text-sky-200"
                    : "text-zinc-300 hover:bg-zinc-800/70 hover:text-zinc-100"
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="mt-auto rounded-xl border border-zinc-800 bg-zinc-900/70 p-3 text-xs text-zinc-400">
          FastAPI backend expected at <span className="text-zinc-200">NEXT_PUBLIC_API_URL</span>
        </div>
      </div>
    </aside>
  );
}
