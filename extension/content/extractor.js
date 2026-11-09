/**
 * DarkGuard - DOM Element Extraction Module
 * 
 * Extracts page elements for dark pattern analysis.
 * 
 * PRIVACY RULES:
 * - NEVER extracts password field values
 * - NEVER extracts credit card field values
 * - NEVER extracts email input values
 * - NEVER extracts authentication tokens
 * - Text extraction is limited to prevent sending entire page HTML
 */

// ============================================================
// Sensitive field types that must never have values extracted
// ============================================================
const SENSITIVE_INPUT_TYPES = [
  'password', 'email', 'tel', 'credit-card', 'cc-number',
  'cc-exp', 'cc-csc', 'cc-name', 'cc-type'
];

// ============================================================
// extractPageText - Visible body text (no scripts/styles)
// ============================================================
function extractPageText() {
  try {
    // Clone the body so we can remove unwanted elements without affecting the page
    const clone = document.body.cloneNode(true);

    // Remove script, style, noscript, svg, and hidden elements
    const removeSelectors = 'script, style, noscript, svg, template, [hidden], [aria-hidden="true"]';
    clone.querySelectorAll(removeSelectors).forEach(el => el.remove());

    // Get text content and normalize whitespace
    let text = clone.innerText || clone.textContent || '';
    text = text.replace(/\s+/g, ' ').trim();

    // Limit to first 50,000 characters to avoid excessive data
    return text.substring(0, 50000);
  } catch (error) {
    console.error('[DarkGuard] Error extracting page text:', error);
    return '';
  }
}

// ============================================================
// extractButtons - All interactive button-like elements
// ============================================================
function extractButtons() {
  const buttons = [];
  const selector = [
    'button',
    'input[type="submit"]',
    'input[type="button"]',
    '[role="button"]',
    'a.btn', 'a.button',
    'a[class*="btn-"]',
    'a[class*="button-"]',
    'div[role="button"]',
    'span[role="button"]'
  ].join(', ');

  try {
    document.querySelectorAll(selector).forEach(el => {
      const rect = el.getBoundingClientRect();
      const computedStyle = window.getComputedStyle(el);

      buttons.push({
        text: (el.innerText || el.value || el.getAttribute('aria-label') || '').trim().substring(0, 200),
        type: el.tagName.toLowerCase(),
        visible: rect.width > 0 && rect.height > 0,
        width: Math.round(rect.width),
        height: Math.round(rect.height),
        fontSize: computedStyle.fontSize,
        backgroundColor: computedStyle.backgroundColor,
        color: computedStyle.color,
        fontWeight: computedStyle.fontWeight,
        classes: typeof el.className === 'string' ? el.className : '',
        ariaLabel: el.getAttribute('aria-label') || '',
        href: el.href || '',
        disabled: el.disabled || el.getAttribute('aria-disabled') === 'true'
      });
    });
  } catch (error) {
    console.error('[DarkGuard] Error extracting buttons:', error);
  }

  return buttons.slice(0, 200);
}

// ============================================================
// extractLinks - Anchor elements with visible text
// ============================================================
function extractLinks() {
  const links = [];

  try {
    document.querySelectorAll('a').forEach(el => {
      const rect = el.getBoundingClientRect();
      const computedStyle = window.getComputedStyle(el);
      const text = (el.innerText || '').trim();

      if (text.length === 0) return;

      links.push({
        text: text.substring(0, 200),
        href: el.href || '',
        visible: rect.width > 0 && rect.height > 0,
        fontSize: computedStyle.fontSize,
        color: computedStyle.color,
        textDecoration: computedStyle.textDecoration,
        classes: typeof el.className === 'string' ? el.className : '',
        rel: el.getAttribute('rel') || '',
        target: el.target || ''
      });
    });
  } catch (error) {
    console.error('[DarkGuard] Error extracting links:', error);
  }

  return links.slice(0, 500);
}

// ============================================================
// extractCheckboxes - Checkbox inputs with labels
// ============================================================
function extractCheckboxes() {
  const checkboxes = [];

  try {
    document.querySelectorAll('input[type="checkbox"]').forEach(el => {
      let label = '';

      // Strategy 1: Find label via 'for' attribute matching checkbox id
      if (el.id) {
        const labelEl = document.querySelector(`label[for="${CSS.escape(el.id)}"]`);
        if (labelEl) label = labelEl.innerText.trim();
      }

      // Strategy 2: Find parent <label> element
      if (!label) {
        const parent = el.closest('label');
        if (parent) label = parent.innerText.trim();
      }

      // Strategy 3: Check adjacent sibling text
      if (!label) {
        const next = el.nextSibling;
        if (next && next.textContent) {
          label = next.textContent.trim();
        }
      }

      // Strategy 4: Check next element sibling
      if (!label && el.nextElementSibling) {
        label = el.nextElementSibling.innerText ? el.nextElementSibling.innerText.trim() : '';
      }

      // Strategy 5: aria-label
      if (!label) {
        label = el.getAttribute('aria-label') || '';
      }

      const rect = el.getBoundingClientRect();

      checkboxes.push({
        checked: el.checked,
        label: label.substring(0, 300),
        name: el.name || '',
        id: el.id || '',
        required: el.required,
        visible: rect.width > 0 && rect.height > 0,
        disabled: el.disabled
      });
    });
  } catch (error) {
    console.error('[DarkGuard] Error extracting checkboxes:', error);
  }

  return checkboxes.slice(0, 100);
}

// ============================================================
// extractForms - Form elements with their inputs
// ============================================================
function extractForms() {
  const forms = [];

  try {
    document.querySelectorAll('form').forEach(form => {
      const inputs = Array.from(
        form.querySelectorAll('input, select, textarea')
      ).map(input => {
        const inputType = input.type || input.tagName.toLowerCase();

        // Respect privacy: never extract sensitive field values
        let value = '';
        if (!SENSITIVE_INPUT_TYPES.includes(inputType) &&
            !input.name.toLowerCase().includes('password') &&
            !input.name.toLowerCase().includes('token') &&
            !input.name.toLowerCase().includes('csrf') &&
            !input.autocomplete?.includes('cc-')) {
          value = (input.value || '').substring(0, 100);
        }

        return {
          type: inputType,
          name: input.name || '',
          placeholder: input.placeholder || '',
          value: value,
          required: input.required,
          ariaLabel: input.getAttribute('aria-label') || '',
          autocomplete: input.autocomplete || ''
        };
      }).slice(0, 50);

      forms.push({
        action: form.action || '',
        method: (form.method || 'get').toUpperCase(),
        id: form.id || '',
        name: form.name || '',
        inputs: inputs,
        inputCount: form.querySelectorAll('input, select, textarea').length
      });
    });
  } catch (error) {
    console.error('[DarkGuard] Error extracting forms:', error);
  }

  return forms.slice(0, 50);
}

// ============================================================
// extractTimers - Countdown / urgency elements
// ============================================================
function extractTimers() {
  const timers = [];
  const timerSelectors = [
    '[class*="countdown"]',
    '[class*="timer"]',
    '[class*="clock"]',
    '[id*="countdown"]',
    '[id*="timer"]',
    '[data-countdown]',
    '[class*="urgency"]',
    '[class*="hurry"]',
    '[class*="limited"]',
    '[class*="expir"]',
    '[class*="remaining"]',
    '[class*="deadline"]',
    '[class*="offer-end"]',
    '[class*="time-left"]',
    '[data-timer]',
    '[data-expires]'
  ];

  try {
    document.querySelectorAll(timerSelectors.join(',')).forEach(el => {
      const rect = el.getBoundingClientRect();
      const text = (el.innerText || '').trim();

      if (text.length === 0) return;

      timers.push({
        text: text.substring(0, 300),
        classes: typeof el.className === 'string' ? el.className : '',
        id: el.id || '',
        tagName: el.tagName.toLowerCase(),
        visible: rect.width > 0 && rect.height > 0,
        dataAttributes: extractDataAttributes(el)
      });
    });
  } catch (error) {
    console.error('[DarkGuard] Error extracting timers:', error);
  }

  return timers.slice(0, 50);
}

// ============================================================
// extractMeta - Page metadata
// ============================================================
function extractMeta() {
  try {
    return {
      title: document.title || '',
      description: document.querySelector('meta[name="description"]')?.content || '',
      url: window.location.href,
      domain: window.location.hostname,
      path: window.location.pathname,
      protocol: window.location.protocol,
      language: document.documentElement.lang || '',
      charset: document.characterSet || '',
      viewport: document.querySelector('meta[name="viewport"]')?.content || ''
    };
  } catch (error) {
    console.error('[DarkGuard] Error extracting meta:', error);
    return {
      title: '',
      description: '',
      url: window.location.href,
      domain: window.location.hostname,
      path: '',
      protocol: '',
      language: '',
      charset: '',
      viewport: ''
    };
  }
}

// ============================================================
// extractPopups - Modal and popup overlays
// ============================================================
function extractPopups() {
  const popups = [];
  const popupSelectors = [
    '[class*="modal"]',
    '[class*="popup"]',
    '[class*="overlay"]',
    '[class*="dialog"]',
    '[role="dialog"]',
    '[role="alertdialog"]',
    '[class*="lightbox"]',
    '[class*="interstitial"]'
  ];

  try {
    document.querySelectorAll(popupSelectors.join(',')).forEach(el => {
      const rect = el.getBoundingClientRect();
      const computedStyle = window.getComputedStyle(el);

      // Only include elements that are currently visible
      if (computedStyle.display === 'none' || computedStyle.visibility === 'hidden') return;
      if (rect.width === 0 && rect.height === 0) return;

      const text = (el.innerText || '').trim();
      if (text.length === 0) return;

      popups.push({
        text: text.substring(0, 500),
        classes: typeof el.className === 'string' ? el.className : '',
        id: el.id || '',
        tagName: el.tagName.toLowerCase(),
        visible: true,
        width: Math.round(rect.width),
        height: Math.round(rect.height),
        zIndex: computedStyle.zIndex,
        position: computedStyle.position
      });
    });
  } catch (error) {
    console.error('[DarkGuard] Error extracting popups:', error);
  }

  return popups.slice(0, 20);
}

// ============================================================
// Helper: Extract data-* attributes from an element
// ============================================================
function extractDataAttributes(el) {
  const data = {};
  try {
    if (el.dataset) {
      for (const [key, value] of Object.entries(el.dataset)) {
        // Limit to prevent huge data blobs
        data[key] = (value || '').substring(0, 100);
      }
    }
  } catch (e) {
    // Silently ignore
  }
  return data;
}

// ============================================================
// Main extraction function - aggregates all extractors
// ============================================================
function extractAllPageData() {
  const startTime = performance.now();

  const data = {
    url: window.location.href,
    page_text: extractPageText(),
    buttons: extractButtons(),
    links: extractLinks(),
    checkboxes: extractCheckboxes(),
    forms: extractForms(),
    timers: extractTimers(),
    popups: extractPopups(),
    meta: extractMeta(),
    extraction_time_ms: 0
  };

  data.extraction_time_ms = Math.round(performance.now() - startTime);

  console.log(`[DarkGuard] Extraction complete in ${data.extraction_time_ms}ms:`, {
    textLength: data.page_text.length,
    buttons: data.buttons.length,
    links: data.links.length,
    checkboxes: data.checkboxes.length,
    forms: data.forms.length,
    timers: data.timers.length,
    popups: data.popups.length
  });

  return data;
}
