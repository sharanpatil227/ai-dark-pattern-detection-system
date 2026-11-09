import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';

const PALETTE = ['#6366F1', '#EC4899', '#F59E0B', '#EF4444', '#10B981', '#3B82F6', '#8B5CF6'];

export default function PatternBreakdown({ categories = [] }) {
  const chartData = categories.slice(0, 6).map((item, idx) => ({
    name: item.category,
    count: item.count,
    color: PALETTE[idx % PALETTE.length],
  }));

  return (
    <div className="bg-white rounded-xl shadow-xs border border-slate-200/80 p-5 flex flex-col h-full">
      <h3 className="text-base font-semibold text-slate-800 mb-1">
        Top Deceptive Categories
      </h3>
      <p className="text-xs text-slate-500 mb-4">
        Frequency of dark patterns identified across all scans
      </p>

      {chartData.length === 0 ? (
        <div className="flex-1 flex items-center justify-center text-sm text-slate-400 py-12">
          No pattern categories detected yet
        </div>
      ) : (
        <div className="w-full h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={chartData}
              layout="vertical"
              margin={{ top: 5, right: 20, left: 20, bottom: 5 }}
            >
              <XAxis type="number" tick={{ fontSize: 11, fill: '#64748B' }} />
              <YAxis
                type="category"
                dataKey="name"
                width={110}
                tick={{ fontSize: 11, fill: '#475569' }}
              />
              <Tooltip
                formatter={(val) => [`${val} occurrences`, 'Count']}
                contentStyle={{ borderRadius: '8px', border: '1px solid #E2E8F0', fontSize: '12px' }}
              />
              <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                {chartData.map((entry, index) => (
                  <Cell key={`bar-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

