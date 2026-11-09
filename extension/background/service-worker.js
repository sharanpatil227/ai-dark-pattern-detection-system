/**
 * DarkGuard - Background Service Worker
 * 
 * Handles API communication with the DarkGuard backend server,
 * manages scan results, and coordinates between popup and content scripts.
 */

const API_BASE = 'http://localhost:8000/api';

// ============================================================
// Message listener for scan requests and other actions
// ============================================================
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  switch (message.action) {
    case 'scanPage':
      handleScanPage(message.data, sendResponse);
      return true; // Async response

    case 'getScanHistory':
      handleGetScanHistory(sendResponse);
      return true;

    case 'clearScanHistory':
      handleClearScanHistory(sendResponse);
      return true;

    case 'checkApiStatus':
      handleCheckApiStatus(sendResponse);
      return true;

    case 'getScanResult':
      handleGetScanResult(message.scanId, sendResponse);
      return true;
  }
});

// ============================================================
// Scan page - sends extracted data to the backend API
// ============================================================
async function handleScanPage(data, sendResponse) {
  try {
    if (!data.url) {
      data.url = data.meta?.url || 'https://unknown-website.com';
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30s timeout

    const response = await fetch(`${API_BASE}/scan`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(data),
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Unknown error');
      throw new Error(`Server error (${response.status}): ${errorText}`);
    }

    const result = await response.json();

    // Store the result in chrome.storage.local
    const storageData = {
      lastScan: result,
      lastScanTimestamp: Date.now()
    };

    // Store by scan_id if available
    if (result.scan_id) {
      storageData[`scan_${result.scan_id}`] = result;
    }

    // Store by domain for quick cache lookup
    if (data.meta && data.meta.domain) {
      storageData[`domain_${data.meta.domain}`] = {
        result: result,
        timestamp: Date.now(),
        url: data.meta.url
      };
    }

    // Update scan history
    const existing = await chrome.storage.local.get('scanHistory');
    const history = existing.scanHistory || [];
    history.unshift({
      scan_id: result.scan_id,
      domain: data.meta?.domain || 'unknown',
      url: data.meta?.url || '',
      timestamp: Date.now(),
      risk_score: result.risk_score || 0,
      patterns_found: result.patterns?.length || 0
    });

    // Keep only last 100 scans in history
    storageData.scanHistory = history.slice(0, 100);

    await chrome.storage.local.set(storageData);

    // Update badge
    updateBadge(result);

    sendResponse({ success: true, data: result });
  } catch (error) {
    console.error('[DarkGuard] Scan error:', error);

    let errorMessage = error.message;
    if (error.name === 'AbortError') {
      errorMessage = 'Request timed out. Please check if the DarkGuard server is running.';
    } else if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
      errorMessage = 'Cannot connect to DarkGuard server. Please ensure the server is running at ' + API_BASE;
    }

    sendResponse({ success: false, error: errorMessage });
  }
}

// ============================================================
// Get scan history
// ============================================================
async function handleGetScanHistory(sendResponse) {
  try {
    const result = await chrome.storage.local.get('scanHistory');
    sendResponse({ success: true, data: result.scanHistory || [] });
  } catch (error) {
    sendResponse({ success: false, error: error.message });
  }
}

// ============================================================
// Clear scan history
// ============================================================
async function handleClearScanHistory(sendResponse) {
  try {
    await chrome.storage.local.clear();
    sendResponse({ success: true });
  } catch (error) {
    sendResponse({ success: false, error: error.message });
  }
}

// ============================================================
// Check API status
// ============================================================
async function handleCheckApiStatus(sendResponse) {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);

    const response = await fetch(`${API_BASE}/health`, {
      method: 'GET',
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (response.ok) {
      const data = await response.json().catch(() => ({}));
      sendResponse({ success: true, data: { status: 'online', ...data } });
    } else {
      sendResponse({ success: false, error: `Server returned ${response.status}` });
    }
  } catch (error) {
    sendResponse({
      success: false,
      error: error.name === 'AbortError'
        ? 'Server not responding'
        : 'Cannot connect to server'
    });
  }
}

// ============================================================
// Get a specific scan result by ID
// ============================================================
async function handleGetScanResult(scanId, sendResponse) {
  try {
    const result = await chrome.storage.local.get(`scan_${scanId}`);
    const scanData = result[`scan_${scanId}`];
    if (scanData) {
      sendResponse({ success: true, data: scanData });
    } else {
      sendResponse({ success: false, error: 'Scan result not found' });
    }
  } catch (error) {
    sendResponse({ success: false, error: error.message });
  }
}

// ============================================================
// Update extension badge based on scan results
// ============================================================
function updateBadge(result) {
  try {
    const patternCount = result.patterns?.length || 0;

    if (patternCount === 0) {
      chrome.action.setBadgeText({ text: '✓' });
      chrome.action.setBadgeBackgroundColor({ color: '#10B981' });
    } else {
      chrome.action.setBadgeText({ text: String(patternCount) });

      const score = result.risk_score || 0;
      if (score >= 70) {
        chrome.action.setBadgeBackgroundColor({ color: '#EF4444' });
      } else if (score >= 40) {
        chrome.action.setBadgeBackgroundColor({ color: '#F59E0B' });
      } else {
        chrome.action.setBadgeBackgroundColor({ color: '#10B981' });
      }
    }
  } catch (error) {
    console.error('[DarkGuard] Badge update error:', error);
  }
}

// ============================================================
// Extension install/update handler
// ============================================================
chrome.runtime.onInstalled.addListener((details) => {
  console.log('[DarkGuard] Extension installed/updated:', details.reason);

  if (details.reason === 'install') {
    // Set default badge
    chrome.action.setBadgeText({ text: '' });
  }
});
