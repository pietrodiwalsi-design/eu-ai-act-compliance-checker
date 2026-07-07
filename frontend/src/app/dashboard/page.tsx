'use client';

import { useState } from 'react';
import Link from 'next/link';

function writeAssessmentsToLocalStorage(assessments: LocalReport[]): void {
  try {
    localStorage.setItem('reports_index', JSON.stringify(assessments));
  } catch {
    // best-effort — localStorage may be unavailable (private browsing, quota, etc.)
  }
}

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
  const [assessments, setAssessments] = useState<LocalReport[]>(readAssessmentsFromLocalStorage);
  const [loading] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.preventDefault(); // don't navigate via the parent <Link>
    e.stopPropagation();

    if (!window.confirm('Delete this assessment permanently? This cannot be undone.')) {
      return;
    }

    setDeletingId(id);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || '';
      const res = await fetch(`${apiUrl}/api/v1/assessments/${id}`, { method: 'DELETE' });
      if (!res.ok && res.status !== 404) {
        // 404 = already gone server-side, still fine to remove locally
        throw new Error(`Delete failed (${res.status})`);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Delete failed';
      alert(message);
      setDeletingId(null);
      return;
    }

    // Remove from local cache regardless (report_{id} + the index entry)
    try {
      localStorage.removeItem(`report_${id}`);
    } catch {
      // ignore
    }
    const next = assessments.filter((a) => a.id !== id);
    setAssessments(next);
    writeAssessmentsToLocalStorage(next);
    setDeletingId(null);
  };

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
                    <button
                      onClick={(e) => handleDelete(e, a.id)}
                      disabled={deletingId === a.id}
                      title="Delete assessment"
                      aria-label="Delete assessment"
                      className="text-slate-500 hover:text-red-400 disabled:opacity-40 disabled:cursor-not-allowed transition-colors p-1.5 rounded-lg hover:bg-red-500/10"
                    >
                      {deletingId === a.id ? (
                        <span className="block w-4 h-4 rounded-full border-2 border-current border-t-transparent animate-spin" />
                      ) : (
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
                          <path fillRule="evenodd" d="M8.75 1A2.75 2.75 0 0 0 6 3.75v.443c-.795.077-1.584.176-2.365.298a.75.75 0 1 0 .23 1.482l.149-.022.841 10.518A2.75 2.75 0 0 0 7.596 19h4.807a2.75 2.75 0 0 0 2.742-2.53l.841-10.52.149.023a.75.75 0 0 0 .23-1.482A41.03 41.03 0 0 0 14 4.193V3.75A2.75 2.75 0 0 0 11.25 1h-2.5ZM10 4c.84 0 1.673.025 2.5.075V3.75c0-.69-.56-1.25-1.25-1.25h-2.5c-.69 0-1.25.56-1.25 1.25v.325C8.327 4.025 9.16 4 10 4ZM8.58 7.72a.75.75 0 0 0-1.5.06l.3 7.5a.75.75 0 1 0 1.5-.06l-.3-7.5Zm4.34.06a.75.75 0 1 0-1.5-.06l-.3 7.5a.75.75 0 1 0 1.5.06l.3-7.5Z" clipRule="evenodd" />
                        </svg>
                      )}
                    </button>
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
