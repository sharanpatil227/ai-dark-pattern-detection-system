import { ShieldCheck, Cpu, Code, Database } from 'lucide-react';

export default function ScanProgress() {
  const steps = [
    { label: 'Extracting DOM elements and text', icon: Code },
    { label: 'Running rule-based pattern engines', icon: ShieldCheck },
    { label: 'Evaluating semantic NLP classifier', icon: Cpu },
    { label: 'Aggregating risk score & persisting', icon: Database },
  ];

  return (
    <div className="bg-white rounded-xl shadow-xs border border-slate-200/80 p-8 my-6 text-center">
      <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-indigo-50 text-indigo-600 mb-4 animate-pulse">
        <Cpu className="w-7 h-7 animate-spin" />
      </div>
      <h3 className="text-base font-semibold text-slate-800">
        AI Detection Engine Running
      </h3>
      <p className="text-xs text-slate-500 max-w-md mx-auto mt-1 mb-6">
        Inspecting linguistic cues, countdown clocks, visual hierarchy disparity, and sneaking options...
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 max-w-2xl mx-auto">
        {steps.map((s, idx) => {
          const Icon = s.icon;
          return (
            <div
              key={idx}
              className="p-3 rounded-lg bg-slate-50 border border-slate-100 flex flex-col items-center text-center"
            >
              <Icon className="w-5 h-5 text-indigo-500 mb-2 animate-bounce" style={{ animationDelay: `${idx * 150}ms` }} />
              <span className="text-[11px] font-medium text-slate-600">
                {s.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

