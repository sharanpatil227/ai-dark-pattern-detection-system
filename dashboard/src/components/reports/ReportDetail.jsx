import { Link } from 'react-router-dom';
import { ArrowLeft, Printer, ExternalLink, Calendar } from 'lucide-react';
import ScoreGauge from '../common/ScoreGauge';
import RiskBadge from '../common/RiskBadge';
import PatternCard from './PatternCard';
import { formatDate } from '../../utils/formatters';

export default function ReportDetail({ report }) {
  if (!report) return null;

  return (
    <div className="space-y-6">
      {/* Navigation header */}
      <div className="flex items-center justify-between">
        <Link
          to="/reports"
          className="text-xs font-semibold text-slate-500 hover:text-slate-800 flex items-center gap-1.5"
        >
          <ArrowLeft className="w-3.5 h-3.5" /> Back to all reports
        </Link>
        <button
          onClick={() => window.print()}
          className="px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-medium text-slate-700 hover:bg-slate-50 flex items-center gap-1.5 cursor-pointer"
        >
          <Printer className="w-3.5 h-3.5" /> Print / Export PDF
        </button>
      </div>

      {/* Main card */}
      <div className="bg-white rounded-xl shadow-xs border border-slate-200/80 p-6">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6 pb-6 border-b border-slate-100">
          <div className="flex items-center gap-5">
            <ScoreGauge score={report.risk_score} size={110} strokeWidth={9} />
            <div>
              <div className="flex items-center gap-2 mb-1.5">
                <RiskBadge level={report.risk_level} />
                <span className="text-xs text-slate-400">
                  {report.total_patterns} Deceptive patterns detected
                </span>
              </div>
              <h1 className="text-xl font-bold text-slate-900 break-all flex items-center gap-2">
                {report.url}
                <a
                  href={report.url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-slate-400 hover:text-indigo-600"
                >
                  <ExternalLink className="w-4 h-4" />
                </a>
              </h1>
              <p className="text-xs text-slate-400 mt-1 flex items-center gap-1">
                <Calendar className="w-3.5 h-3.5" />
                Audited on {formatDate(report.scanned_at)} &bull; ID: {report.scan_id}
              </p>
            </div>
          </div>
        </div>

        {/* Global recommendations */}
        {report.recommendations && report.recommendations.length > 0 && (
          <div className="pt-5">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
              Actionable Recommendations
            </h3>
            <div className="space-y-2">
              {report.recommendations.map((rec, idx) => (
                <div
                  key={idx}
                  className="text-xs text-slate-700 bg-slate-50 p-2.5 rounded-lg border border-slate-200/60"
                >
                  {rec}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Patterns breakdown */}
      <div>
        <h3 className="text-base font-bold text-slate-800 mb-4">
          Identified Dark Pattern Instances ({report.patterns?.length || 0})
        </h3>
        {(!report.patterns || report.patterns.length === 0) ? (
          <div className="bg-white rounded-xl border border-slate-200/80 p-8 text-center text-sm text-slate-500">
            No dark patterns were flagged for this website.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {report.patterns.map((p, idx) => (
              <PatternCard key={idx} pattern={p} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

