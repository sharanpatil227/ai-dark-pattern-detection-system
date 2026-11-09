import { RISK_BG_COLORS } from '../../utils/constants';
import { capitalize } from '../../utils/formatters';

/**
 * Color-coded badge displaying risk level.
 * @param {{ level: 'low'|'medium'|'high'|'critical', className?: string }} props
 */
export default function RiskBadge({ level, className = '' }) {
  const normalizedLevel = (level || 'low').toLowerCase();
  const colorClass = RISK_BG_COLORS[normalizedLevel] || RISK_BG_COLORS.low;

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${colorClass} ${className}`}
    >
      {capitalize(normalizedLevel)}
    </span>
  );
}
