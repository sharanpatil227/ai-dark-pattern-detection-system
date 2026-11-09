import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts';

export default function ScanTimeline({ timeline = [] }) {
  const data = timeline.length > 0
    ? timeline.map((item) => ({
        date: item.date.slice(5), // 'MM-DD'
        scans: item.count,
      }))
    : [];

  return (
    <div className="bg-white rounded-xl shadow-xs border border-slate-200/80 p-5 flex flex-col h-full">
      <h3 className="text-base font-semibold text-slate-800 mb-1">
        Scanning Activity
      </h3>
      <p className="text-xs text-slate-500 mb-4">
        Websites audited over the past 30 days
      </p>

      {data.length === 0 ? (
        <div className="flex-1 flex items-center justify-center text-sm text-slate-400 py-12">
          No scanning history recorded
        </div>
      ) : (
        <div className="w-full h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
              <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#64748B' }} />
              <YAxis tick={{ fontSize: 11, fill: '#64748B' }} allowDecimals={false} />
              <Tooltip
                formatter={(val) => [`${val} scans`, 'Audits']}
                contentStyle={{ borderRadius: '8px', border: '1px solid #E2E8F0', fontSize: '12px' }}
              />
              <Line
                type="monotone"
                dataKey="scans"
                stroke="#6366F1"
                strokeWidth={2.5}
                dot={{ r: 3, fill: '#6366F1' }}
                activeDot={{ r: 5 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

