'use client';

import { WizardQuestion } from '@/types/assessment';

interface WizardStepProps {
  question: WizardQuestion;
  value: string | string[] | boolean | undefined;
  onChange: (value: string | string[] | boolean) => void;
}

export default function WizardStep({ question, value, onChange }: WizardStepProps) {
  return (
    <div className="space-y-6">
      {/* Article badge */}
      {question.euAiActArticle && (
        <span className="inline-block bg-blue-500/10 border border-blue-500/20 text-blue-300 text-xs px-3 py-1 rounded-full">
          {question.euAiActArticle}
        </span>
      )}

      {/* Question text */}
      <h2 className="text-2xl font-semibold leading-snug">{question.question}</h2>

      {/* Help text */}
      {question.helpText && (
        <p className="text-slate-400 text-sm leading-relaxed">{question.helpText}</p>
      )}

      {/* Input */}
      <div className="mt-4">
        {question.type === 'textarea' && (
          <textarea
            className="w-full bg-slate-800 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none min-h-[140px] text-sm"
            placeholder="Type your answer here…"
            value={typeof value === 'string' ? value : ''}
            onChange={(e) => onChange(e.target.value)}
          />
        )}

        {question.type === 'text' && (
          <input
            type="text"
            className="w-full bg-slate-800 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
            placeholder="Type your answer…"
            value={typeof value === 'string' ? value : ''}
            onChange={(e) => onChange(e.target.value)}
          />
        )}

        {(question.type === 'radio' || question.type === 'select') && question.options && (
          <div className="space-y-3">
            {question.options.map((opt) => (
              <label
                key={opt.value}
                className={`flex items-center gap-4 p-4 rounded-xl border cursor-pointer transition-all ${
                  value === opt.value
                    ? 'border-blue-500 bg-blue-500/10 text-white'
                    : 'border-white/10 bg-slate-800/50 text-slate-300 hover:border-white/20 hover:bg-slate-800'
                }`}
              >
                <div
                  className={`w-5 h-5 rounded-full border-2 flex-shrink-0 flex items-center justify-center transition-all ${
                    value === opt.value ? 'border-blue-500' : 'border-slate-500'
                  }`}
                >
                  {value === opt.value && (
                    <div className="w-2.5 h-2.5 rounded-full bg-blue-500" />
                  )}
                </div>
                <input
                  type="radio"
                  className="sr-only"
                  name={question.id}
                  value={opt.value}
                  checked={value === opt.value}
                  onChange={() => onChange(opt.value)}
                />
                <span className="text-sm">{opt.label}</span>
              </label>
            ))}
          </div>
        )}

        {question.type === 'boolean' && (
          <div className="flex gap-4">
            {(['Yes', 'No'] as const).map((opt) => (
              <button
                key={opt}
                onClick={() => onChange(opt === 'Yes')}
                className={`flex-1 py-3 rounded-xl border text-sm font-medium transition-all ${
                  value === (opt === 'Yes')
                    ? 'border-blue-500 bg-blue-500/10 text-white'
                    : 'border-white/10 bg-slate-800/50 text-slate-300 hover:border-white/20'
                }`}
              >
                {opt}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
