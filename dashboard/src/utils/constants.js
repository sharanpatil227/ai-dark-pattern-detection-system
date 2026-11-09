/** Risk level color mappings */
export const RISK_COLORS = {
  low: '#22C55E',
  medium: '#EAB308',
  high: '#F97316',
  critical: '#EF4444',
};

export const RISK_BG_COLORS = {
  low: 'bg-green-100 text-green-800',
  medium: 'bg-yellow-100 text-yellow-800',
  high: 'bg-orange-100 text-orange-800',
  critical: 'bg-red-100 text-red-800',
};

export const RISK_BORDER_COLORS = {
  low: 'border-green-400',
  medium: 'border-yellow-400',
  high: 'border-orange-400',
  critical: 'border-red-400',
};

/** Dark pattern categories */
export const CATEGORIES = {
  urgency: { label: 'Urgency', color: '#EF4444', icon: 'Timer' },
  scarcity: { label: 'Scarcity', color: '#F97316', icon: 'AlertTriangle' },
  misdirection: { label: 'Misdirection', color: '#8B5CF6', icon: 'MousePointerClick' },
  social_proof: { label: 'Social Proof', color: '#3B82F6', icon: 'Users' },
  forced_action: { label: 'Forced Action', color: '#EC4899', icon: 'Lock' },
  obstruction: { label: 'Obstruction', color: '#14B8A6', icon: 'ShieldOff' },
  sneaking: { label: 'Sneaking', color: '#F59E0B', icon: 'EyeOff' },
  confirmshaming: { label: 'Confirm Shaming', color: '#6366F1', icon: 'Frown' },
  disguised_ads: { label: 'Disguised Ads', color: '#10B981', icon: 'Megaphone' },
  trick_wording: { label: 'Trick Wording', color: '#E11D48', icon: 'FileWarning' },
};

/** Category colors for charts */
export const CATEGORY_COLORS = Object.values(CATEGORIES).map((c) => c.color);

/** Detection method labels */
export const DETECTION_METHODS = {
  rule: { label: 'Rule-Based', color: 'bg-blue-100 text-blue-700' },
  nlp: { label: 'NLP/AI', color: 'bg-purple-100 text-purple-700' },
  dom: { label: 'DOM Analysis', color: 'bg-teal-100 text-teal-700' },
};

/** Severity labels */
export const SEVERITY_COLORS = {
  low: 'bg-green-100 text-green-700',
  medium: 'bg-yellow-100 text-yellow-700',
  high: 'bg-orange-100 text-orange-700',
  critical: 'bg-red-100 text-red-700',
};

/** Navigation items */
export const NAV_ITEMS = [
  { path: '/', label: 'Dashboard', icon: 'LayoutDashboard' },
  { path: '/scan', label: 'Scan', icon: 'Search' },
  { path: '/reports', label: 'Reports', icon: 'FileText' },
  { path: '/about', label: 'About', icon: 'Info' },
];
