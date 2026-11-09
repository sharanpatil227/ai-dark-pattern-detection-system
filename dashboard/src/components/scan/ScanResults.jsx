import { Link } from 'react-router-dom';
import { ExternalLink, CheckCircle2, AlertOctagon, Share2 } from 'lucide-react';
import ScoreGauge from '../common/ScoreGauge';
import RiskBadge from '../common/RiskBadge';
import PatternCard from '../reports/PatternCard';

export default function ScanResults({ result }) {
  if (!result) return null;

  return (
    <div className="space-y-6 mt-6">
      {/* Top summary banner */}
      <div className="bg-white rounded-xl shadow-xs border border-slate-200/80 p-6">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6 pb-6 border-b border-slate-100">
          <div className="flex items-center gap-5">
            <ScoreGauge score={result.risk_score} size={110} strokeWidth={9} />
            <div>
              <div className="flex items-center gap-2 mb-1">
                <RiskBadge level={result.risk_level} />
                <span className="text-xs text-slate-400">
                  {result.total_patterns} patterns flagged
                </span>
              </div>
              <h2 className="text-xl font-bold text-slate-800 break-all">
                {result.url}
              </h2>
              <p className="text-xs text-slate-500 mt-1">
                Scan ID: <code className="font-mono text-slate-600">{result.scan_id}</code>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 w-full md:w-auto">
            <Link
              to={`/reports/${result.scan_id}`}
              className="flex-1 md:flex-none text-center px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold shadow-xs transition-colors"
            >
              Permanent Report &rarr;
            </Link>
          </div>
        </div>

        {/* Global Recommendations */}
        {result.recommendations && result.recommendations.length > 0 && (
          <div className="pt-4">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
              Key Consumer Takeaways
            </h4>
            <ul className="space-y-1.5">
              {result.recommendations.map((rec, idx) => (
                <li
                  key={idx}
                  className="text-xs text-slate-700 flex items-start gap-2 bg-slate-50 p-2 rounded-md"
                >
                  <span className="text-indigo-600 font-bold">•</span>
                  <span>{rec}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Detected Patterns List */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-base font-bold text-slate-800">
            Detected Manipulative Patterns ({result.patterns?.length || 0})
          </h3>
        </div>

        {(!result.patterns || result.patterns.length === 0) ? (
          <div className="bg-white rounded-xl border border-slate-200/80 p-8 text-center">
            <CheckCircle2 className="w-10 h-10 text-green-500 mx-auto mb-2" />
            <h4 className="text-sm font-semibold text-slate-800">
              No Deceptive Patterns Detected!
            </h4>
            <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
              The analyzed elements adhere to transparent UI guidelines. No artificial urgency, confirm shaming, or pre-selected add-ons were identified.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {result.patterns.map((p, idx) => (
              <PatternCard key={idx} pattern={p} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

