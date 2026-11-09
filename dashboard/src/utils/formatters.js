/**
 * Format a date string to a human-readable format.
 * @param {string|Date} dateStr - ISO date string or Date object
 * @param {object} opts - Intl.DateTimeFormat options
 * @returns {string} Formatted date string
 */
export function formatDate(dateStr, opts = {}) {
  if (!dateStr) return '—';
  const date = new Date(dateStr);
  if (isNaN(date.getTime())) return '—';
  const defaults = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    ...opts,
  };
  return date.toLocaleDateString('en-US', defaults);
}

/**
 * Format a date string to a short format (no time).
 * @param {string|Date} dateStr
 * @returns {string}
 */
export function formatShortDate(dateStr) {
  return formatDate(dateStr, { hour: undefined, minute: undefined });
}

/**
 * Format a date to relative time ("2 hours ago").
 * @param {string|Date} dateStr
 * @returns {string}
 */
export function formatRelativeTime(dateStr) {
  if (!dateStr) return '—';
  const date = new Date(dateStr);
  if (isNaN(date.getTime())) return '—';
  const now = new Date();
  const diffMs = now - date;
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHr = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHr / 24);

  if (diffSec < 60) return 'Just now';
  if (diffMin < 60) return `${diffMin}m ago`;
  if (diffHr < 24) return `${diffHr}h ago`;
  if (diffDay < 7) return `${diffDay}d ago`;
  return formatShortDate(dateStr);
}

/**
 * Format a risk score (0-100) with color context.
 * @param {number} score
 * @returns {string}
 */
export function formatScore(score) {
  if (score == null || isNaN(score)) return '—';
  return Math.round(score).toString();
}

/**
 * Get risk level from a numeric score.
 * @param {number} score - 0 to 100
 * @returns {'low'|'medium'|'high'|'critical'}
 */
export function getRiskLevel(score) {
  if (score == null || isNaN(score)) return 'low';
  if (score < 30) return 'low';
  if (score < 60) return 'medium';
  if (score < 80) return 'high';
  return 'critical';
}

/**
 * Capitalize the first letter of a string.
 * @param {string} str
 * @returns {string}
 */
export function capitalize(str) {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Truncate a URL for display.
 * @param {string} url
 * @param {number} maxLen
 * @returns {string}
 */
export function truncateUrl(url, maxLen = 50) {
  if (!url) return '—';
  try {
    const u = new URL(url);
    const display = u.hostname + u.pathname;
    if (display.length <= maxLen) return display;
    return display.substring(0, maxLen - 3) + '...';
  } catch {
    if (url.length <= maxLen) return url;
    return url.substring(0, maxLen - 3) + '...';
  }
}

/**
 * Format a number with commas.
 * @param {number} num
 * @returns {string}
 */
export function formatNumber(num) {
  if (num == null || isNaN(num)) return '0';
  return num.toLocaleString('en-US');
}

/**
 * Format a percentage.
 * @param {number} value
 * @param {number} decimals
 * @returns {string}
 */
export function formatPercentage(value, decimals = 1) {
  if (value == null || isNaN(value)) return '0%';
  return `${value.toFixed(decimals)}%`;
}
