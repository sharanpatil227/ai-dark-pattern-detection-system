import {
  AlertTriangle,
  Lightbulb,
  Tag,
  CheckCircle2,
  Clock,
  ShieldAlert,
  HelpCircle,
} from 'lucide-react';
import RiskBadge from '../common/RiskBadge';

const CATEGORY_ICONS = {
  'Confirm Shaming': AlertTriangle,
  'Fake Urgency': Clock,
  'Forced Continuity': ShieldAlert,
  'Hidden Costs': Tag,
  'Sneaking': ShieldAlert,
  'Obstruction': AlertTriangle,
  'Misdirection': AlertTriangle,
};

export default function PatternCard({ pattern }) {
  const Icon = CATEGORY_ICONS[pattern.category] || HelpCircle;
  const confPercent = Math.round((pattern.confidence || 0) * 100);

  const methodBadge = {
    rule: { bg: 'bg-blue-50 text-blue-700 border-blue-200', label: 'Rule Engine' },
    nlp: { bg: 'bg-purple-50 text-purple-700 border-purple-200', label: 'NLP Machine Learning' },
    dom: { bg: 'bg-teal-50 text-teal-700 border-teal-200', label: 'DOM Structure' },
  }[pattern.detection_method] || { bg: 'bg-slate-50 text-slate-700 border-slate-200', label: pattern.detection_method };

  return (
    <div className="bg-white rounded-xl shadow-xs border border-slate-200/80 p-5 hover:border-slate-300 transition-all">
      <div className="flex flex-wrap items-start justify-between gap-2 pb-3 border-b border-slate-100">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center shrink-0">
            <Icon className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-slate-800">
              {pattern.category}
            </h4>
            {pattern.rule_id && (
              <span className="text-[10px] text-slate-400 font-mono">
                ID: {pattern.rule_id}
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span
            className={`text-[10px] font-semibold px-2 py-0.5 rounded-md border ${methodBadge.bg}`}
          >
            {methodBadge.label}
          </span>
          <RiskBadge level={pattern.severity} />
        </div>
      </div>

      {/* Confidence meter */}
      <div className="mt-3 flex items-center gap-2">
        <span className="text-[11px] text-slate-500 font-medium">Confidence:</span>
        <div className="flex-1 max-w-xs h-2 bg-slate-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-indigo-500 rounded-full transition-all"
            style={{ width: `${confPercent}%` }}
          />
        </div>
        <span className="text-[11px] font-semibold text-slate-700">{confPercent}%</span>
      </div>

      {/* Evidence */}
      <div className="mt-3.5 bg-slate-50 rounded-lg p-3 border border-slate-200/70 font-mono text-xs text-slate-700 break-words">
        <span className="text-[10px] uppercase font-sans font-bold text-slate-400 block mb-1">
          Evidence Detected:
        </span>
        &ldquo;{pattern.evidence}&rdquo;
      </div>

      {/* Explanation */}
      <p className="mt-3 text-xs text-slate-600 leading-relaxed">
        {pattern.explanation}
      </p>

      {/* Recommendation */}
      <div className="mt-3 pt-3 border-t border-slate-100 flex items-start gap-2 text-xs text-amber-900 bg-amber-50/50 p-2.5 rounded-lg border border-amber-200/60">
        <Lightbulb className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-amber-800">Recommendation: </span>
          {pattern.recommendation}
        </div>
      </div>
    </div>
  );
}

