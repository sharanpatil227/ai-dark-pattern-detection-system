/**
 * DarkGuard - Content Script
 * 
 * Listens for messages from the popup/background and coordinates
 * data extraction from the current page using extractor.js functions.
 */

(() => {
  'use strict';

  // Prevent double-injection
  if (window.__darkguardContentLoaded) return;
  window.__darkguardContentLoaded = true;

  console.log('[DarkGuard] Content script loaded on:', window.location.href);

  // ============================================================
  // Message listener for extraction requests
  // ============================================================
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'extractPageData') {
      try {
        const data = extractAllPageData();
        sendResponse({ success: true, data: data });
      } catch (error) {
        console.error('[DarkGuard] Extraction error:', error);
        sendResponse({
          success: false,
          error: error.message || 'Unknown extraction error'
        });
      }
      // Return true to keep the message channel open for the synchronous response
      return true;
    }

    if (message.action === 'ping') {
      sendResponse({ success: true, loaded: true });
      return true;
    }

    if (message.action === 'getPageInfo') {
      try {
        sendResponse({
          success: true,
          data: {
            url: window.location.href,
            domain: window.location.hostname,
            title: document.title,
            readyState: document.readyState
          }
        });
      } catch (error) {
        sendResponse({ success: false, error: error.message });
      }
      return true;
    }
  });
})();
