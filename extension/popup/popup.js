/**
 * DarkGuard - Popup Controller
 * Manages UI interactions, scans active tab, and displays risk analysis.
 */

document.addEventListener('DOMContentLoaded', async () => {
  // DOM Elements
  const siteDomainEl = document.getElementById('siteDomain');
  const scanBtn = document.getElementById('scanBtn');
  const scanBtnIcon = document.getElementById('scanBtnIcon');
  const scanBtnText = document.getElementById('scanBtnText');
  const statusDot = document.getElementById('statusDot');
  const statusText = document.getElementById('statusText');
  const emptyState = document.getElementById('emptyState');
  const scanningState = document.getElementById('scanningState');
  const errorState = document.getElementById('errorState');
  const errorMessage = document.getElementById('errorMessage');
  const retryBtn = document.getElementById('retryBtn');
  const resultsEl = document.getElementById('results');
  const riskScoreValue = document.getElementById('riskScoreValue');
  const riskStatusBadge = document.getElementById('riskStatusBadge');
  const riskPatternsCount = document.getElementById('riskPatternsCount');
  const gaugeFill = document.getElementById('gaugeFill');
  const patternsCountBadge = document.getElementById('patternsCountBadge');
  const patternsList = document.getElementById('patternsList');
  const noPatterns = document.getElementById('noPatterns');
  const recommendationsSection = document.getElementById('recommendationsSection');
  const recommendationsList = document.getElementById('recommendationsList');
  const reportBtn = document.getElementById('reportBtn');

  let activeTab = null;
  let activeUrl = '';

  // 1. Initialize Active Tab and Health Check
  try {
    activeTab = await DarkGuardAPI.getActiveTab();
    if (activeTab && activeTab.url) {
      activeUrl = activeTab.url;
      try {
        const parsed = new URL(activeUrl);
        siteDomainEl.textContent = parsed.hostname || activeUrl;
      } catch (e) {
        siteDomainEl.textContent = activeUrl;
      }
      scanBtn.disabled = false;
    }
  } catch (err) {
    siteDomainEl.textContent = 'Active tab unavailable';
  }

  // Check Backend Status
  checkBackendHealth();

  // Check if current page has cached scan results
  if (activeUrl) {
    checkCachedScan(activeUrl);
  }

  // Event Listeners
  scanBtn.addEventListener('click', () => performScan());
  if (retryBtn) {
    retryBtn.addEventListener('click', () => performScan());
  }

  async function checkBackendHealth() {
    try {
      const res = await DarkGuardAPI.checkApiStatus();
      const isOnline = res && (res.reachable === true || res.success === true || res.data?.status === 'online' || res.status === 'healthy');
      if (isOnline) {
        statusDot.className = 'status-dot connected';
        statusText.textContent = 'Backend Online';
      } else {
        statusDot.className = 'status-dot disconnected';
        statusText.textContent = 'Backend Offline';
      }
    } catch {
      statusDot.className = 'status-dot disconnected';
      statusText.textContent = 'Backend Offline';
    }
  }

  async function checkCachedScan(url) {
    try {
      const cached = await DarkGuardAPI.getCachedScan(url);
      if (cached) {
        renderResults(cached);
      }
    } catch (e) {
      // Ignore cache lookup error
    }
  }

  async function performScan() {
    if (!activeTab || !activeTab.id) return;

    // Set UI to scanning
    showState('scanning');
    scanBtn.disabled = true;

    try {
      // 1. Extract DOM & content from tab
      const pageData = await DarkGuardAPI.extractPageData(activeTab.id);
      if (!pageData.url) {
        pageData.url = activeUrl || pageData.meta?.url || 'https://unknown-website.com';
      }

      // 2. Transmit to backend detection API
      const result = await DarkGuardAPI.scanPage(pageData);

      // 3. Render analysis
      renderResults(result);
    } catch (err) {
      console.error('Scan error:', err);
      showError(err.message || 'Failed to inspect page elements.');
    } finally {
      scanBtn.disabled = false;
    }
  }

  function renderResults(result) {
    showState('results');

    const score = Math.max(0, Math.min(100, result.risk_score || 0));
    const level = (result.risk_level || 'Low').toUpperCase();

    // Risk Gauge animation
    riskScoreValue.textContent = score;
    const circumference = 326.73; // 2 * PI * 52
    const offset = circumference - (score / 100) * circumference;
    gaugeFill.style.strokeDashoffset = offset;

    // Gauge color by risk
    let gaugeColor = '#22C55E';
    if (score > 25 && score <= 50) gaugeColor = '#EAB308';
    else if (score > 50 && score <= 75) gaugeColor = '#F97316';
    else if (score > 75) gaugeColor = '#EF4444';
    gaugeFill.style.stroke = gaugeColor;

    // Status Badge
    riskStatusBadge.textContent = `${level} RISK`;
    riskStatusBadge.className = `risk-status-badge risk-${level.toLowerCase()}`;
    riskPatternsCount.textContent = `${result.total_patterns || 0} patterns detected`;

    // Render Patterns
    const patterns = result.patterns || [];
    patternsCountBadge.textContent = patterns.length;
    patternsList.innerHTML = '';

    if (patterns.length === 0) {
      noPatterns.classList.remove('hidden');
    } else {
      noPatterns.classList.add('hidden');
      patterns.forEach((p) => {
        const card = createPatternCard(p);
        patternsList.appendChild(card);
      });
    }

    // Render Recommendations
    const recommendations = result.recommendations || [];
    recommendationsList.innerHTML = '';
    if (recommendations.length > 0) {
      recommendationsSection.classList.remove('hidden');
      recommendations.forEach((rec) => {
        const li = document.createElement('li');
        li.className = 'recommendation-item';
        li.textContent = rec;
        recommendationsList.appendChild(li);
      });
    } else {
      recommendationsSection.classList.add('hidden');
    }

    // Full Report button
    if (result.scan_id) {
      reportBtn.classList.remove('hidden');
      reportBtn.href = `http://localhost:5173/reports/${result.scan_id}`;
    }
  }

  function createPatternCard(p) {
    const card = document.createElement('div');
    card.className = 'pattern-card';

    const sev = (p.severity || 'Medium').toLowerCase();
    const confPercent = Math.round((p.confidence || 0) * 100);

    card.innerHTML = `
      <div class="pattern-header">
        <span class="pattern-category">${escapeHtml(p.category)}</span>
        <span class="pattern-severity severity-${sev}">${escapeHtml(p.severity)}</span>
      </div>
      <div class="pattern-confidence">
        <div class="confidence-bar">
          <div class="confidence-fill" style="width: ${confPercent}%"></div>
        </div>
        <span class="confidence-text">${confPercent}% confidence</span>
      </div>
      <div class="pattern-evidence">
        <span class="evidence-label">Evidence:</span>
        <div class="evidence-text">"${escapeHtml(p.evidence)}"</div>
      </div>
      <div class="pattern-explanation">${escapeHtml(p.explanation)}</div>
      <div class="pattern-recommendation">
        <strong>Tip:</strong> ${escapeHtml(p.recommendation)}
      </div>
    `;
    return card;
  }

  function showState(state) {
    emptyState.classList.add('hidden');
    scanningState.classList.add('hidden');
    errorState.classList.add('hidden');
    resultsEl.classList.add('hidden');

    if (state === 'empty') emptyState.classList.remove('hidden');
    else if (state === 'scanning') scanningState.classList.remove('hidden');
    else if (state === 'error') errorState.classList.remove('hidden');
    else if (state === 'results') resultsEl.classList.remove('hidden');
  }

  function showError(msg) {
    showState('error');
    errorMessage.textContent = msg;
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
});

