'use client';

import { useState } from 'react';
import Link from 'next/link';

const TIER_LABELS: Record<string, string> = {
  prohibited:   '🚫 Prohibited',
  high_risk:    '🔴 High Risk',
  limited_risk: '🟡 Limited Risk',
  minimal_risk: '🟢 Minimal Risk',
};

interface LocalReport {
  id: string;
  risk_tier: string;
  overall_score: number;
  generated_at: string;
  system_description: string;
}

// Read from localStorage once, synchronously, during initial render —
// avoids the extra render + "setState in effect" lint warning that comes
// from reading it inside a useEffect body just to call setState().
function readAssessmentsFromLocalStorage(): LocalReport[] {
  if (typeof window === 'undefined') return []; // SSR/build-time guard
  try {
    return JSON.parse(localStorage.getItem('reports_index') || '[]');
  } catch {
    return [];
  }
}

export default function DashboardPage() {
  const [assessments] = useState<LocalReport[]>(readAssessmentsFromLocalStorage);
  const [loading] = useState(false);

  return (
    <main className="min-h-screen bg-slate-900 text-white">
      <div className="max-w-5xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="flex items-center justify-between mb-10">
          <div>
            <Link href="/" className="text-slate-400 text-sm hover:text-white transition-colors">← Home</Link>
            <h1 className="text-2xl font-bold mt-2">Assessment Dashboard</h1>
          </div>
          <Link
            href="/assess"
            className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-medium px-5 py-2.5 rounded-xl text-sm transition-colors"
          >
            + New Assessment
          </Link>
        </div>

        {/* Content */}
        {loading ? (
          <div className="flex items-center justify-center py-24">
            <div className="w-8 h-8 rounded-full border-4 border-blue-500 border-t-transparent animate-spin" />
          </div>
        ) : assessments.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-24 text-center">
            <div className="text-5xl mb-4">📋</div>
            <p className="text-xl font-semibold">No assessments yet</p>
            <p className="text-slate-400 text-sm mt-2 mb-6">Run your first EU AI Act compliance check to get started.</p>
            <Link
              href="/assess"
              className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-medium px-6 py-3 rounded-xl transition-colors"
            >
              Start Assessment →
            </Link>
          </div>
        ) : (
          <div className="space-y-3">
            {assessments.map((a) => (
              <Link
                key={a.id}
                href={`/report/${a.id}`}
                className="block bg-slate-800/60 border border-white/10 rounded-2xl p-5 hover:bg-slate-800 transition-colors"
              >
                <div className="flex items-center justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-sm truncate">
                      {a.system_description?.slice(0, 80) || 'Assessment'}
                      {a.system_description?.length > 80 ? '…' : ''}
                    </p>
                    <p className="text-xs text-slate-400 mt-1">{new Date(a.generated_at).toLocaleString()}</p>
                  </div>
                  <div className="flex items-center gap-3 flex-shrink-0">
                    <span className="text-sm text-slate-300">{TIER_LABELS[a.risk_tier] ?? a.risk_tier}</span>
                    <span className="font-semibold text-sm">{a.overall_score}/100</span>
                    <span className="text-xs px-2 py-0.5 rounded-full border bg-emerald-500/10 border-emerald-500/20 text-emerald-300">
                      complete
                    </span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
