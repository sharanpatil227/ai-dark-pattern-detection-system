/**
 * DarkGuard - API Communication Helper
 * 
 * Utility module for communicating with the DarkGuard backend API.
 * Used by the popup to send messages through the background service worker.
 */

const DarkGuardAPI = (() => {
  'use strict';

  /**
   * Send a message to the background service worker and wait for a response.
   * @param {Object} message - The message to send
   * @returns {Promise<Object>} The response from the service worker
   */
  function sendMessage(message) {
    return new Promise((resolve, reject) => {
      chrome.runtime.sendMessage(message, (response) => {
        if (chrome.runtime.lastError) {
          reject(new Error(chrome.runtime.lastError.message));
          return;
        }
        if (!response) {
          reject(new Error('No response received from background worker'));
          return;
        }
        resolve(response);
      });
    });
  }

  /**
   * Send a message to the content script in the specified tab.
   * @param {number} tabId - The tab ID to send the message to
   * @param {Object} message - The message to send
   * @returns {Promise<Object>} The response from the content script
   */
  function sendTabMessage(tabId, message) {
    return new Promise((resolve, reject) => {
      chrome.tabs.sendMessage(tabId, message, (response) => {
        if (chrome.runtime.lastError) {
          reject(new Error(chrome.runtime.lastError.message));
          return;
        }
        if (!response) {
          reject(new Error('No response from content script. The page may need to be refreshed.'));
          return;
        }
        resolve(response);
      });
    });
  }

  /**
   * Get the currently active tab.
   * @returns {Promise<chrome.tabs.Tab>} The active tab
   */
  async function getActiveTab() {
    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tabs || tabs.length === 0) {
      throw new Error('No active tab found');
    }
    return tabs[0];
  }

  /**
   * Extract page data from the active tab's content script.
   * @param {number} tabId - The tab ID
   * @returns {Promise<Object>} Extracted page data
   */
  async function extractPageData(tabId) {
    const response = await sendTabMessage(tabId, { action: 'extractPageData' });
    if (!response.success) {
      throw new Error(response.error || 'Failed to extract page data');
    }
    return response.data;
  }

  /**
   * Scan a page by sending extracted data to the backend API via background worker.
   * @param {Object} pageData - The extracted page data
   * @returns {Promise<Object>} Scan results
   */
  async function scanPage(pageData) {
    const response = await sendMessage({ action: 'scanPage', data: pageData });
    if (!response.success) {
      throw new Error(response.error || 'Scan failed');
    }
    return response.data;
  }

  /**
   * Check if the backend API is reachable.
   * @returns {Promise<Object>} API status information
   */
  async function checkApiStatus() {
    const response = await sendMessage({ action: 'checkApiStatus' });
    return response;
  }

  /**
   * Get scan history.
   * @returns {Promise<Array>} Array of scan history entries
   */
  async function getScanHistory() {
    const response = await sendMessage({ action: 'getScanHistory' });
    if (!response.success) {
      throw new Error(response.error || 'Failed to get scan history');
    }
    return response.data;
  }

  /**
   * Clear all scan history.
   * @returns {Promise<void>}
   */
  async function clearScanHistory() {
    const response = await sendMessage({ action: 'clearScanHistory' });
    if (!response.success) {
      throw new Error(response.error || 'Failed to clear scan history');
    }
  }

  /**
   * Get a cached scan result for a specific domain.
   * @param {string} domain - The domain to look up
   * @returns {Promise<Object|null>} Cached result or null
   */
  async function getCachedResult(domain) {
    return new Promise((resolve) => {
      chrome.storage.local.get(`domain_${domain}`, (result) => {
        const cached = result[`domain_${domain}`];
        if (cached && cached.timestamp) {
          // Cache is valid for 1 hour
          const ONE_HOUR = 60 * 60 * 1000;
          if (Date.now() - cached.timestamp < ONE_HOUR) {
            resolve(cached);
            return;
          }
        }
        resolve(null);
      });
    });
  }

  /**
   * Check if the content script is loaded in a tab.
   * @param {number} tabId - The tab ID to check
   * @returns {Promise<boolean>}
   */
  async function isContentScriptLoaded(tabId) {
    try {
      const response = await sendTabMessage(tabId, { action: 'ping' });
      return response && response.success;
    } catch (e) {
      return false;
    }
  }

  // Public API
  return {
    sendMessage,
    sendTabMessage,
    getActiveTab,
    extractPageData,
    scanPage,
    checkApiStatus,
    getScanHistory,
    clearScanHistory,
    getCachedResult,
    isContentScriptLoaded
  };
})();
