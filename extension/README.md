# DarkGuard - AI Dark Pattern Detection Chrome Extension (Manifest V3)

A lightweight, privacy-preserving Chrome Extension built with Manifest V3 to audit active web pages for deceptive and manipulative UI patterns.

## Features
- **One-Click Audit**: Extract visible DOM elements, buttons, links, timers, and text without collecting sensitive form data.
- **Privacy by Design**: Passwords, payment card details, and email values are strictly excluded before sending payloads to the detection backend.
- **Instant Risk Meter**: Animated risk gauge displaying 0-100 risk score and risk level (Low, Medium, High, Critical).
- **Categorized Breakdown**: Detailed evidence, explanations, confidence scores, and recommendations.
- **Dashboard Integration**: Direct one-click link to comprehensive audit report in the DarkGuard web portal.

## How to Install in Chrome / Edge / Brave

1. Open your browser and navigate to `chrome://extensions/` (or `edge://extensions/`).
2. Toggle on **Developer mode** in the top-right corner.
3. Click the **Load unpacked** button.
4. Select the `c:\dark pattern prj\extension` folder.
5. The **DarkGuard** shield icon will appear in your browser extension toolbar!

## Permissions
- `activeTab`: Used solely when the user clicks the extension popup to inspect DOM element styles and text on the current tab.
- `storage`: Caches recent scan results locally in the browser.
- `host_permissions` (`http://localhost:8000/*`): Allows communication with the local DarkGuard detection backend.

