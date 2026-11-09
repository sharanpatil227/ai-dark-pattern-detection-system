import { Shield, Cpu, Code2, Database, EyeOff, Lock, CheckCircle2 } from 'lucide-react';

export default function AboutPage() {
  const categories = [
    {
      name: 'Confirm Shaming',
      desc: 'Emotionally manipulative opt-out language designed to guilt the user into accepting an unwanted offer.',
      example: '"No thanks, I hate saving money" or "No, I prefer paying full price"',
    },
    {
      name: 'Fake Urgency',
      desc: 'Misleading timers, high-demand pressure badges, and artificial scarcity designed to induce impulsive buying.',
      example: '"Only 2 minutes left!" or "4 other users have this in their cart right now"',
    },
    {
      name: 'Sneaking / Pre-selection',
      desc: 'Quietly adding unwanted add-ons, warranties, insurance, or subscriptions into the user cart by default.',
      example: 'Pre-checked checkboxes for supplemental magazine subscriptions or package protection.',
    },
    {
      name: 'Hidden Costs',
      desc: 'Disclosing mandatory service fees, administrative surcharges, or resort fees only at the very final checkout step.',
      example: 'Undisclosed handling charges revealed after credit card details are entered.',
    },
    {
      name: 'Forced Continuity',
      desc: 'Free trial offers that automatically convert into expensive recurring monthly or annual memberships with buried disclosure.',
      example: '7-day trial that silently rolls over into non-refundable recurring annual fee.',
    },
    {
      name: 'Obstruction (Roach Motel)',
      desc: 'Making subscription cancellation excessively difficult while signup is immediate and frictionless.',
      example: 'Requiring a phone call to a toll-free number during limited business hours to cancel an online service.',
    },
    {
      name: 'Misdirection',
      desc: 'Using visual hierarchy, deceptive button styling, and extreme contrast disparity to distract users from opt-out choices.',
      example: 'Massive colorful "Accept All" button paired with a faint invisible "Settings" link.',
    },
  ];

  return (
    <div className="space-y-8 max-w-5xl mx-auto pb-12">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
          About AI Dark Pattern Detection System
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          An academic and enterprise-grade cybersecurity and UI/UX audit platform designed to identify deceptive interface patterns.
        </p>
      </div>

      {/* Overview Card */}
      <div className="bg-white rounded-xl shadow-xs border border-slate-200/80 p-6">
        <h2 className="text-base font-bold text-slate-800 mb-2">
          Project Objective
        </h2>
        <p className="text-sm text-slate-600 leading-relaxed">
          Dark patterns are deceptive user interface designs engineered to trick users into performing actions they might not otherwise take—such as buying unwanted insurance, surrendering private data, or entering binding recurring subscriptions. DarkGuard pairs rule-based pattern matching, DOM layout analysis, and Machine Learning NLP classification to audit and expose these deceptive techniques in real time.
        </p>
      </div>

      {/* Detection Pipeline Layers */}
      <div>
        <h2 className="text-lg font-bold text-slate-800 mb-4">
          Four-Layer Detection Architecture
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-xs">
            <div className="w-10 h-10 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center mb-3">
              <Code2 className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-bold text-slate-800">1. Rule Engine</h3>
            <p className="text-xs text-slate-500 mt-2">
              Deterministic regular expressions and heuristic rules target unambiguous deceptive phrases and pre-ticked inputs.
            </p>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-xs">
            <div className="w-10 h-10 rounded-lg bg-purple-50 text-purple-600 flex items-center justify-center mb-3">
              <Cpu className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-bold text-slate-800">2. NLP Classifier</h3>
            <p className="text-xs text-slate-500 mt-2">
              TF-IDF feature extraction combined with trained Logistic Regression classifies semantic context and guilt-tripping language.
            </p>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-xs">
            <div className="w-10 h-10 rounded-lg bg-teal-50 text-teal-600 flex items-center justify-center mb-3">
              <EyeOff className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-bold text-slate-800">3. DOM Analyzer</h3>
            <p className="text-xs text-slate-500 mt-2">
              Analyzes button size ratios, visual prominence disparity, tiny cancellation fonts, and hidden form fields.
            </p>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-xs">
            <div className="w-10 h-10 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center mb-3">
              <Shield className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-bold text-slate-800">4. Risk Scoring</h3>
            <p className="text-xs text-slate-500 mt-2">
              Aggregates detections with severity weights, confidence scaling, and category diversity to produce a 0-100 risk rating.
            </p>
          </div>
        </div>
      </div>

      {/* Core Dark Pattern Taxonomies */}
      <div>
        <h2 className="text-lg font-bold text-slate-800 mb-4">
          Core Dark Pattern Taxonomies Detected
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {categories.map((cat, idx) => (
            <div
              key={idx}
              className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-xs"
            >
              <h3 className="text-sm font-bold text-slate-800 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-indigo-500" />
                {cat.name}
              </h3>
              <p className="text-xs text-slate-600 mt-1.5 leading-relaxed">
                {cat.desc}
              </p>
              <div className="mt-3 p-2 bg-slate-50 rounded text-[11px] font-mono text-slate-600 border border-slate-100">
                <span className="text-slate-400 font-sans font-semibold">Example: </span>
                {cat.example}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Privacy Standards */}
      <div className="bg-indigo-50/60 rounded-xl border border-indigo-100 p-6 flex items-start gap-4">
        <Lock className="w-6 h-6 text-indigo-600 shrink-0 mt-1" />
        <div>
          <h3 className="text-sm font-bold text-indigo-900">
            Privacy & Data Security by Design
          </h3>
          <p className="text-xs text-indigo-800/80 mt-1 leading-relaxed">
            The Chrome extension and dashboard strictly adhere to privacy standards. Form passwords, credit card credentials, email addresses, and session authentication tokens are automatically sanitized in the browser and never transmitted over the network.
          </p>
        </div>
      </div>
    </div>
  );
}

