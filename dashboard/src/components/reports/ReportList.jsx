import { Link } from 'react-router-dom';
import { ExternalLink, Search } from 'lucide-react';
import RiskBadge from '../common/RiskBadge';
import { formatDate } from '../../utils/formatters';

export default function ReportList({
  reports = [],
  searchQuery,
  onSearchChange,
  page,
  totalPages,
  onPageChange,
}) {
  return (
    <div className="bg-white rounded-xl shadow-xs border border-slate-200/80 overflow-hidden">
      {/* Search Header */}
      <div className="p-4 border-b border-slate-200/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="relative max-w-sm w-full">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search by URL domain..."
            className="w-full pl-9 pr-3 py-1.5 text-xs rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        <span className="text-xs text-slate-500 font-medium">
          Showing page {page} of {Math.max(1, totalPages)}
        </span>
      </div>

      {reports.length === 0 ? (
        <div className="p-12 text-center text-sm text-slate-400">
          No matching scan reports found.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-600">
            <thead className="bg-slate-50/75 text-xs uppercase font-medium text-slate-500 border-b border-slate-200/60">
              <tr>
                <th className="px-5 py-3.5">Target Website</th>
                <th className="px-5 py-3.5">Risk Score</th>
                <th className="px-5 py-3.5">Severity</th>
                <th className="px-5 py-3.5">Patterns</th>
                <th className="px-5 py-3.5">Scanned Date</th>
                <th className="px-5 py-3.5 text-right">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {reports.map((r) => (
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
                  <td className="px-5 py-3.5 font-bold text-slate-700">
                    {r.risk_score} / 100
                  </td>
                  <td className="px-5 py-3.5">
                    <RiskBadge level={r.risk_level} />
                  </td>
                  <td className="px-5 py-3.5">
                    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-700">
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
                      View Report &rarr;
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination controls */}
      {totalPages > 1 && (
        <div className="p-4 border-t border-slate-100 flex items-center justify-between">
          <button
            onClick={() => onPageChange(page - 1)}
            disabled={page <= 1}
            className="px-3 py-1 text-xs rounded border border-slate-200 disabled:opacity-40 cursor-pointer hover:bg-slate-50"
          >
            Previous
          </button>
          <span className="text-xs text-slate-600">
            Page {page} of {totalPages}
          </span>
          <button
            onClick={() => onPageChange(page + 1)}
            disabled={page >= totalPages}
            className="px-3 py-1 text-xs rounded border border-slate-200 disabled:opacity-40 cursor-pointer hover:bg-slate-50"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}

