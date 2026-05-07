// components/Sidebar.tsx
"use client";
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Brain, MessageSquare, Activity, Database, ShieldCheck } from 'lucide-react';

export default function Sidebar() {
  const pathname = usePathname();
  
  const navItems = [
    { name: 'Chat', href: '/', icon: MessageSquare },
    { name: 'Team Status', href: '/status', icon: Activity },
    { name: 'Knowledge Base', href: '/knowledge', icon: Database },
    { name: 'Context Verification', href: '/verify', icon: ShieldCheck },
  ];

  return (
    <div className="w-64 bg-zinc-950 border-r border-white/10 h-screen flex flex-col p-4 text-zinc-300">
      <div className="flex items-center gap-3 mb-10 px-2 mt-4">
        <div className="p-2 bg-gradient-to-tr from-indigo-500 to-purple-600 rounded-lg">
          <Brain className="w-6 h-6 text-white" />
        </div>
        <h1 className="text-xl font-bold text-white tracking-wide">COBE</h1>
      </div>
      
      <nav className="flex flex-col gap-2">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link key={item.name} href={item.href}>
              <div className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${
                isActive ? 'bg-white/10 text-white' : 'hover:bg-white/5 hover:text-white'
              }`}>
                <Icon className="w-5 h-5" />
                <span className="font-medium">{item.name}</span>
              </div>
            </Link>
          );
        })}
      </nav>
    </div>
  );
}