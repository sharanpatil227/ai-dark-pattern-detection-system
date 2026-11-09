import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

const COLORS = {
  Low: '#22C55E',
  Medium: '#EAB308',
  High: '#F97316',
  Critical: '#EF4444',
};

export default function RiskDistribution({ distribution = {} }) {
  const data = [
    { name: 'Low', value: distribution?.Low || 0, color: COLORS.Low },
    { name: 'Medium', value: distribution?.Medium || 0, color: COLORS.Medium },
    { name: 'High', value: distribution?.High || 0, color: COLORS.High },
    { name: 'Critical', value: distribution?.Critical || 0, color: COLORS.Critical },
  ].filter((d) => d.value > 0);

  const total = data.reduce((acc, cur) => acc + cur.value, 0);

  return (
    <div className="bg-white rounded-xl shadow-xs border border-slate-200/80 p-5 flex flex-col h-full">
      <h3 className="text-base font-semibold text-slate-800 mb-1">
        Risk Level Breakdown
      </h3>
      <p className="text-xs text-slate-500 mb-4">
        Distribution of analyzed websites by risk severity
      </p>

      {total === 0 ? (
        <div className="flex-1 flex items-center justify-center text-sm text-slate-400 py-12">
          No scan data available yet
        </div>
      ) : (
        <div className="w-full h-64">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={55}
                outerRadius={85}
                paddingAngle={4}
                dataKey="value"
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                formatter={(val, name) => [`${val} sites (${Math.round((val / total) * 100)}%)`, name]}
                contentStyle={{ borderRadius: '8px', border: '1px solid #E2E8F0', fontSize: '12px' }}
              />
              <Legend
                verticalAlign="bottom"
                iconType="circle"
                wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

