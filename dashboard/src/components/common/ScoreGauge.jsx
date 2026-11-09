import { RISK_COLORS } from '../../utils/constants';
import { getRiskLevel, formatScore } from '../../utils/formatters';

/**
 * Circular SVG gauge displaying a 0-100 score.
 * Color changes based on risk level.
 * @param {{ score: number, size?: number, strokeWidth?: number, label?: string }} props
 */
export default function ScoreGauge({ score = 0, size = 120, strokeWidth = 10, label = 'Risk Score' }) {
  const safeScore = Math.max(0, Math.min(100, score || 0));
  const riskLevel = getRiskLevel(safeScore);
  const color = RISK_COLORS[riskLevel];

  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (safeScore / 100) * circumference;
  const center = size / 2;

  return (
    <div className="flex flex-col items-center gap-1">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          {/* Background circle */}
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke="#E2E8F0"
            strokeWidth={strokeWidth}
          />
          {/* Progress circle */}
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            className="transition-all duration-700 ease-out"
          />
        </svg>
        {/* Center text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-bold" style={{ color }}>
            {formatScore(safeScore)}
          </span>
        </div>
      </div>
      {label && (
        <span className="text-xs text-slate-500 font-medium">{label}</span>
      )}
    </div>
  );
}
