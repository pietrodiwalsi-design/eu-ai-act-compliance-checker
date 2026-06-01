'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import WizardShell from '@/components/wizard/WizardShell';
import { WizardAnswers } from '@/types/assessment';

type Status = 'wizard' | 'submitting' | 'error';

export default function AssessPage() {
  const router = useRouter();
  const [status, setStatus] = useState<Status>('wizard');
  const [error, setError] = useState<string | null>(null);

  const handleComplete = async (answers: WizardAnswers) => {
    setStatus('submitting');
    setError(null);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';
      const res = await fetch(`${apiUrl}/api/v1/assess`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answers }),
      });

      if (!res.ok) {
        const detail = await res.text();
        throw new Error(detail || `Server error: ${res.status}`);
      }

      const report = await res.json();
      router.push(`/report/${report.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong. Please try again.');
      setStatus('error');
    }
  };

  if (status === 'submitting') {
    return (
      <div className="min-h-screen bg-slate-900 text-white flex flex-col items-center justify-center gap-6">
        <div className="w-14 h-14 rounded-full border-4 border-blue-500 border-t-transparent animate-spin" />
        <div className="text-center">
          <p className="text-xl font-semibold">Analysing your AI system…</p>
          <p className="text-slate-400 mt-2 text-sm">Checking compliance against EU AI Act articles. This takes up to 3 minutes.</p>
        </div>
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div className="min-h-screen bg-slate-900 text-white flex flex-col items-center justify-center gap-6 px-6">
        <div className="text-5xl">⚠️</div>
        <div className="text-center max-w-md">
          <p className="text-xl font-semibold">Assessment failed</p>
          <p className="text-slate-400 mt-2 text-sm">{error}</p>
        </div>
        <button
          onClick={() => setStatus('wizard')}
          className="px-6 py-3 bg-blue-600 hover:bg-blue-500 rounded-xl text-white font-medium transition-colors"
        >
          Try again
        </button>
      </div>
    );
  }

  return <WizardShell onComplete={handleComplete} />;
}
