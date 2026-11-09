import { Link } from 'react-router-dom';
import { ExternalLink, ArrowRight } from 'lucide-react';
import RiskBadge from '../common/RiskBadge';
import { formatDate } from '../../utils/formatters';

export default function RecentScans({ reports = [] }) {
  return (
    <div className="bg-white rounded-xl shadow-xs border border-slate-200/80 overflow-hidden">
      <div className="p-5 border-b border-slate-100 flex items-center justify-between">
        <div>
          <h3 className="text-base font-semibold text-slate-800">Recent Scans</h3>
          <p className="text-xs text-slate-500">Latest website safety assessments</p>
        </div>
        <Link
          to="/reports"
          className="text-xs font-medium text-indigo-600 hover:text-indigo-700 flex items-center gap-1"
        >
          View all reports <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>

      {reports.length === 0 ? (
        <div className="p-8 text-center text-sm text-slate-400">
          No websites scanned yet. Head over to the{' '}
          <Link to="/scan" className="text-indigo-600 hover:underline">
            Scan
          </Link>{' '}
          page or use the Chrome Extension to run your first analysis.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-600">
            <thead className="bg-slate-50/75 text-xs uppercase font-medium text-slate-500 border-b border-slate-200/60">
              <tr>
                <th className="px-5 py-3.5">Scanned URL</th>
                <th className="px-5 py-3.5">Risk Score</th>
                <th className="px-5 py-3.5">Level</th>
                <th className="px-5 py-3.5">Patterns</th>
                <th className="px-5 py-3.5">Date</th>
                <th className="px-5 py-3.5 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {reports.slice(0, 5).map((r) => (
                <tr key={r.scan_id} className="hover:bg-slate-50/60 transition-colors">
                  <td className="px-5 py-3.5 max-w-xs truncate font-medium text-slate-800">
                    <a
                      href={r.url}
                      target="_blank"
                      rel="noreferrer"
                      className="hover:text-indigo-600 inline-flex items-center gap-1.5"
                    >
                      {r.url}
                      <ExternalLink className="w-3 h-3 text-slate-400 shrink-0" />
                    </a>
                  </td>
                  <td className="px-5 py-3.5 font-semibold text-slate-700">
                    {r.risk_score}/100
                  </td>
                  <td className="px-5 py-3.5">
                    <RiskBadge level={r.risk_level} />
                  </td>
                  <td className="px-5 py-3.5">
                    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-700">
                      {r.total_patterns}
                    </span>
                  </td>
                  <td className="px-5 py-3.5 text-xs text-slate-400 whitespace-nowrap">
                    {formatDate(r.scanned_at)}
                  </td>
                  <td className="px-5 py-3.5 text-right">
                    <Link
                      to={`/reports/${r.scan_id}`}
                      className="text-xs font-semibold text-indigo-600 hover:text-indigo-800"
                    >
                      Report &rarr;
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

