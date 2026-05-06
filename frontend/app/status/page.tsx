// app/status/page.tsx
"use client";
import { Activity, CheckCircle, AlertCircle, Clock } from 'lucide-react';

export default function StatusPage() {
  const teamStatus = [
    { name: 'Backend API', status: 'operational', lastCheck: '2 min ago' },
    { name: 'Vector Database', status: 'operational', lastCheck: '5 min ago' },
    { name: 'LLM Service', status: 'operational', lastCheck: '1 min ago' },
    { name: 'File Storage', status: 'operational', lastCheck: '3 min ago' },
  ];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'operational':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'warning':
        return <AlertCircle className="w-5 h-5 text-yellow-500" />;
      default:
        return <Clock className="w-5 h-5 text-zinc-500" />;
    }
  };

  return (
    <div className="h-full w-full bg-zinc-900 p-8">
      <div className="max-w-4xl">
        <h1 className="text-4xl font-bold text-white mb-2">Team Status</h1>
        <p className="text-zinc-400 mb-8">Real-time system health monitoring</p>

        <div className="grid gap-4">
          {teamStatus.map((item) => (
            <div
              key={item.name}
              className="bg-zinc-800 border border-white/10 rounded-lg p-4 flex items-center justify-between hover:border-white/20 transition"
            >
              <div className="flex items-center gap-4">
                <Activity className="w-5 h-5 text-zinc-400" />
                <div>
                  <h3 className="text-white font-medium">{item.name}</h3>
                  <p className="text-zinc-500 text-sm">{item.lastCheck}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {getStatusIcon(item.status)}
                <span className="text-green-500 font-medium text-sm">{item.status}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
