import { Shield, AlertTriangle, Eye, Activity } from 'lucide-react';

export default function StatsCards({ stats }) {
  const cards = [
    {
      title: 'Total Scans',
      value: stats?.total_scans ?? 0,
      icon: Activity,
      color: 'bg-blue-500',
      lightBg: 'bg-blue-50',
      textColor: 'text-blue-600',
      description: 'Websites analyzed',
    },
    {
      title: 'Avg Risk Score',
      value: `${stats?.average_risk_score ?? 0}/100`,
      icon: Shield,
      color: 'bg-indigo-500',
      lightBg: 'bg-indigo-50',
      textColor: 'text-indigo-600',
      description: 'Across all scanned targets',
    },
    {
      title: 'Dark Patterns Found',
      value: stats?.total_patterns_found ?? 0,
      icon: Eye,
      color: 'bg-amber-500',
      lightBg: 'bg-amber-50',
      textColor: 'text-amber-600',
      description: 'Deceptive elements flagged',
    },
    {
      title: 'High/Critical Sites',
      value: stats?.high_risk_count ?? 0,
      icon: AlertTriangle,
      color: 'bg-red-500',
      lightBg: 'bg-red-50',
      textColor: 'text-red-600',
      description: 'Severe consumer risk',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
      {cards.map((c, idx) => {
        const Icon = c.icon;
        return (
          <div
            key={idx}
            className="bg-white rounded-xl shadow-xs border border-slate-200/80 p-5 hover:shadow-md transition-shadow"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
                  {c.title}
                </p>
                <p className="text-2xl font-bold text-slate-800 mt-1">
                  {c.value}
                </p>
              </div>
              <div className={`w-12 h-12 rounded-xl ${c.lightBg} flex items-center justify-center shrink-0`}>
                <Icon className={`w-6 h-6 ${c.textColor}`} />
              </div>
            </div>
            <p className="text-xs text-slate-400 mt-3">{c.description}</p>
          </div>
        );
      })}
    </div>
  );
}

