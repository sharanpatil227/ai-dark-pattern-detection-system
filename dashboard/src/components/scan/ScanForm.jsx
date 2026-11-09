import { useState } from 'react';
import { Search, Globe, FileText, ChevronDown, ChevronUp, Sparkles } from 'lucide-react';

const PRESET_DEMOS = [
  {
    name: 'Flash Sale (Urgency + Shaming)',
    url: 'https://demo-store.com/checkout',
    text: "Only 2 minutes left to complete your order! Flash sale expiring in 00:01:45. Don't miss out on this 70% discount. No thanks, I hate saving money and prefer paying full price.",
    buttons: [
      { text: "YES, CLAIM 70% DISCOUNT NOW", width: 280, height: 50, is_visible: true },
      { text: "No thanks, I prefer paying full price", width: 80, height: 20, is_visible: true }
    ],
    checkboxes: [
      { label: "Add $4.99 shipping protection warranty", is_checked: true, is_visible: true }
    ]
  },
  {
    name: 'Subscription Trap (Forced Continuity)',
    url: 'https://demo-saas.com/free-trial',
    text: "Start your free 7-day trial now! Membership automatically renews at $49.99 per month until cancelled. Continuous billing applies upon trial completion.",
    buttons: [
      { text: "Start Free Trial", width: 200, height: 45, is_visible: true }
    ],
    checkboxes: []
  },
  {
    name: 'Clean & Fair E-Commerce Site',
    url: 'https://fair-store.com/catalog',
    text: "Welcome to our catalog. All pricing is inclusive of statutory taxes. Standard shipping arrives in 3-5 business days. You can cancel your orders anytime from your account settings.",
    buttons: [
      { text: "Add to Cart", width: 140, height: 40, is_visible: true }
    ],
    checkboxes: [
      { label: "Remember my shipping address", is_checked: false, is_visible: true }
    ]
  }
];

export default function ScanForm({ onScan, loading }) {
  const [url, setUrl] = useState('https://flashdeal-example.com/checkout');
  const [pageText, setPageText] = useState(
    "Only 2 minutes left! 4 people are viewing this product right now. No thanks, I don't want to save money. Mandatory handling fee of $12.99 added at checkout. Free 7-day trial automatically renews at $49.99/mo."
  );
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [buttonText, setButtonText] = useState("No, I prefer paying full price");
  const [checkboxLabel, setCheckboxLabel] = useState("Pre-selected VIP warranty package");
  const [isChecked, setIsChecked] = useState(true);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!url.trim()) return;

    const payload = {
      url: url.trim(),
      page_text: pageText.trim(),
      buttons: buttonText.trim()
        ? [
            { text: "Accept All & Continue", width: 280, height: 50, is_visible: true },
            { text: buttonText.trim(), width: 80, height: 20, is_visible: true }
          ]
        : [],
      links: [
        { text: "To cancel your membership, call our hotline", href: "#", font_size: "10px", is_visible: true }
      ],
      checkboxes: checkboxLabel.trim()
        ? [
            { label: checkboxLabel.trim(), is_checked: isChecked, is_visible: true }
          ]
        : [],
      forms: [],
      timers: [
        { text: "00:01:45", is_counting_down: true }
      ],
      meta: {
        title: "Website Scan",
        description: "Dark pattern analysis"
      }
    };

    onScan(payload);
  };

  const loadPreset = (preset) => {
    setUrl(preset.url);
    setPageText(preset.text);
    if (preset.buttons && preset.buttons.length > 1) {
      setButtonText(preset.buttons[1].text);
    } else {
      setButtonText("");
    }
    if (preset.checkboxes && preset.checkboxes.length > 0) {
      setCheckboxLabel(preset.checkboxes[0].label);
      setIsChecked(preset.checkboxes[0].is_checked);
    } else {
      setCheckboxLabel("");
      setIsChecked(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-xs border border-slate-200/80 p-6">
      {/* Preset demo buttons */}
      <div className="mb-6">
        <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2 flex items-center gap-1.5">
          <Sparkles className="w-3.5 h-3.5 text-indigo-500" />
          Quick Test Demos
        </label>
        <div className="flex flex-wrap gap-2 mt-2">
          {PRESET_DEMOS.map((p, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => loadPreset(p)}
              className="text-xs px-3 py-1.5 rounded-lg border border-slate-200 hover:border-indigo-400 hover:bg-indigo-50/50 text-slate-700 transition-colors cursor-pointer"
            >
              {p.name}
            </button>
          ))}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
            Website URL
          </label>
          <div className="relative">
            <Globe className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="url"
              required
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com/checkout"
              className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm text-slate-800"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
            Extracted Page Text & Context
          </label>
          <div className="relative">
            <FileText className="absolute left-3.5 top-3.5 w-4 h-4 text-slate-400" />
            <textarea
              rows={4}
              value={pageText}
              onChange={(e) => setPageText(e.target.value)}
              placeholder="Paste visible text or offer terms from the webpage..."
              className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm text-slate-800"
            />
          </div>
          <p className="text-[11px] text-slate-400 mt-1">
            The AI engine checks this text using natural language classification and deterministic pattern rules.
          </p>
        </div>

        {/* Advanced DOM parameters accordion */}
        <div>
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="text-xs font-medium text-slate-600 hover:text-indigo-600 flex items-center gap-1 cursor-pointer"
          >
            {showAdvanced ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            {showAdvanced ? 'Hide DOM & Element Simulation' : 'Simulate DOM Elements (Buttons, Checkboxes)'}
          </button>

          {showAdvanced && (
            <div className="mt-3 p-4 bg-slate-50 rounded-lg border border-slate-200 space-y-3">
              <div>
                <label className="block text-xs text-slate-600 mb-1">
                  Negative / Decline Button Label
                </label>
                <input
                  type="text"
                  value={buttonText}
                  onChange={(e) => setButtonText(e.target.value)}
                  placeholder="e.g. No, I prefer paying full price"
                  className="w-full px-3 py-1.5 text-xs rounded border border-slate-200 bg-white"
                />
              </div>

              <div>
                <label className="block text-xs text-slate-600 mb-1">
                  Checkbox Label
                </label>
                <input
                  type="text"
                  value={checkboxLabel}
                  onChange={(e) => setCheckboxLabel(e.target.value)}
                  placeholder="e.g. Automatically enroll in insurance"
                  className="w-full px-3 py-1.5 text-xs rounded border border-slate-200 bg-white"
                />
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="dom-checked"
                  checked={isChecked}
                  onChange={(e) => setIsChecked(e.target.checked)}
                  className="rounded text-indigo-600"
                />
                <label htmlFor="dom-checked" className="text-xs text-slate-700">
                  Pre-checked by default (triggers Sneaking detection if optional)
                </label>
              </div>
            </div>
          )}
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 px-4 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-sm flex items-center justify-center gap-2 shadow-sm transition-colors cursor-pointer disabled:opacity-60"
        >
          {loading ? (
            <>
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Scanning and analyzing with AI engine...
            </>
          ) : (
            <>
              <Search className="w-4 h-4" />
              Scan Website Now
            </>
          )}
        </button>
      </form>
    </div>
  );
}

