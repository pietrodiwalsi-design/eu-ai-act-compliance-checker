'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { ComplianceReport, WhatIfResponse } from '@/types/assessment';
import ScoreCard from '@/components/compliance/ScoreCard';
import TrafficLight from '@/components/compliance/TrafficLight';

interface ReportPageProps {
  params: { id: string };
}

export default function ReportPage({ params }: ReportPageProps) {
  const [report, setReport] = useState<ComplianceReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // What-If state
  const [showWhatIf, setShowWhatIf] = useState(false);
  const [whatIfContext, setWhatIfContext] = useState('');
  const [whatIfResult, setWhatIfResult] = useState<WhatIfResponse | null>(null);
  const [whatIfLoading, setWhatIfLoading] = useState(false);

  useEffect(() => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';
    fetch(`${apiUrl}/api/v1/reports/${params.id}`)
      .then((r) => {
        if (!r.ok) throw new Error(`Report not found (${r.status})`);
        return r.json();
      })
      .then(setReport)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [params.id]);

  const handleExportPDF = () => {
    // Simple browser print with print-optimized styles
    // The @media print rules in globals.css handle hiding nav etc.
    window.print();
  };

  const runWhatIf = async () => {
    if (!report || !whatIfContext.trim()) return;

    setWhatIfLoading(true);
    const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

    try {
      const res = await fetch(`${apiUrl}/api/v1/whatif`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          original_answers: report.answers ?? {},
          new_context: whatIfContext.trim(),
        }),
      });

      if (!res.ok) throw new Error('What-If analysis failed');
      const data: WhatIfResponse = await res.json();
      setWhatIfResult(data);
    } catch (e: any) {
      alert(e.message || 'What-If analysis failed');
    } finally {
      setWhatIfLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 text-white flex items-center justify-center">
        <div className="w-10 h-10 rounded-full border-4 border-blue-500 border-t-transparent animate-spin" />
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="min-h-screen bg-slate-900 text-white flex flex-col items-center justify-center gap-4">
        <p className="text-xl font-semibold">Report not found</p>
        <Link href="/dashboard" className="text-blue-400 hover:underline text-sm">← Back to dashboard</Link>
      </div>
    );
  }

  const failCount    = report.checks.filter((c) => c.status === 'fail').length;
  const warningCount = report.checks.filter((c) => c.status === 'warning').length;
  const passCount    = report.checks.filter((c) => c.status === 'pass').length;

  return (
    <main className="min-h-screen bg-slate-900 text-white print:bg-white print:text-black">
      <div className="max-w-5xl mx-auto px-6 py-12 print:py-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-10 print:mb-4">
          <div>
            <Link href="/dashboard" className="text-slate-400 text-sm hover:text-white transition-colors print:hidden">← All assessments</Link>
            <h1 className="text-2xl font-bold mt-2">Compliance Report</h1>
            <p className="text-slate-400 text-sm mt-1 print:text-gray-600">
              Generated {new Date(report.generated_at).toLocaleString()} · {report.processing_time_seconds.toFixed(1)}s
            </p>
          </div>
          <button
            onClick={handleExportPDF}
            className="px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-sm hover:bg-white/10 transition-colors print:hidden"
          >
            Export PDF
          </button>
        </div>

        {/* Summary row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10 print:mb-6">
          <ScoreCard score={report.overall_score} riskTier={report.risk_tier} />

          {/* Stats */}
          <div className="md:col-span-2 grid grid-cols-3 gap-4 content-start">
            {[
              { label: 'Passed',   count: passCount,    color: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/20' },
              { label: 'Warnings', count: warningCount, color: 'text-amber-400',   bg: 'bg-amber-400/10',   border: 'border-amber-400/20' },
              { label: 'Failed',   count: failCount,    color: 'text-red-400',     bg: 'bg-red-500/10',     border: 'border-red-500/20' },
            ].map((s) => (
              <div key={s.label} className={`rounded-2xl border p-6 text-center ${s.bg} ${s.border} print:bg-white print:border-gray-300`}>
                <p className={`text-4xl font-bold ${s.color} print:text-black`}>{s.count}</p>
                <p className="text-slate-400 text-sm mt-1 print:text-gray-600">{s.label}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Compliance checks table */}
        <h2 className="text-lg font-semibold mb-4 print:text-black">Article-by-Article Breakdown</h2>
        <div className="space-y-3 print:space-y-2">
          {report.checks.map((check, i) => (
            <div key={i} className="bg-slate-800/60 border border-white/10 rounded-2xl p-5 print:bg-white print:border-gray-300 print:text-black">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-xs font-mono text-blue-300 bg-blue-500/10 border border-blue-500/20 px-2 py-0.5 rounded print:bg-gray-100 print:text-black print:border-gray-300">
                      {check.article}
                    </span>
                    <TrafficLight status={check.status} size="sm" />
                    <span className="text-xs text-slate-400 ml-auto print:text-gray-600">{check.score}/100</span>
                  </div>
                  <p className="font-medium text-sm print:text-black">{check.requirement}</p>
                  <p className="text-slate-400 text-sm mt-1 leading-relaxed print:text-gray-700">{check.rationale}</p>
                  {check.remediation && (
                    <div className="mt-3 p-3 bg-amber-400/5 border border-amber-400/20 rounded-lg print:bg-amber-50 print:border-amber-300">
                      <p className="text-xs text-amber-300 font-medium mb-1 print:text-amber-700">Remediation</p>
                      <p className="text-sm text-slate-300 print:text-gray-800">{check.remediation}</p>
                    </div>
                  )}
                  {check.source_citation && (
                    <p className="text-xs text-slate-500 mt-2 italic print:text-gray-600">"{check.source_citation}"</p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* What-If Simulator Panel */}
        <div className="mt-12 pt-8 border-t border-white/10 print:hidden">
          <button
            onClick={() => setShowWhatIf(!showWhatIf)}
            className="flex items-center gap-2 text-lg font-semibold mb-4 hover:text-blue-400 transition-colors"
          >
            {showWhatIf ? '▼' : '▶'} What-If Scenario Simulator
          </button>

          {showWhatIf && (
            <div className="bg-slate-800/40 border border-white/10 rounded-2xl p-6">
              <p className="text-sm text-slate-400 mb-3">
                Describe a different deployment context to see how the risk tier and obligations would change.
              </p>

              <textarea
                value={whatIfContext}
                onChange={(e) => setWhatIfContext(e.target.value)}
                placeholder="e.g. Deploying this system in a public school for emotion detection of students..."
                className="w-full h-24 bg-slate-900 border border-white/10 rounded-xl p-4 text-sm resize-y focus:outline-none focus:border-blue-500/50"
              />

              <button
                onClick={runWhatIf}
                disabled={!whatIfContext.trim() || whatIfLoading}
                className="mt-4 px-6 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-900 disabled:text-blue-400 rounded-xl text-sm font-medium transition-colors"
              >
                {whatIfLoading ? 'Analyzing...' : 'Run What-If Analysis'}
              </button>

              {whatIfResult && (
                <div className="mt-6 p-5 bg-slate-900/60 border border-white/10 rounded-xl">
                  <div className="flex items-center gap-3 mb-4">
                    <span className="text-sm text-slate-400">Original:</span>
                    <span className="px-3 py-0.5 text-xs rounded-full bg-white/10">{whatIfResult.original_tier}</span>
                    <span className="text-slate-400">→</span>
                    <span className="text-sm text-slate-400">New:</span>
                    <span className={`px-3 py-0.5 text-xs rounded-full ${whatIfResult.changed ? 'bg-amber-500/20 text-amber-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
                      {whatIfResult.new_tier}
                    </span>
                    {whatIfResult.changed && <span className="text-xs text-amber-400">(changed)</span>}
                  </div>

                  <div className="prose prose-invert prose-sm max-w-none text-slate-300 whitespace-pre-wrap">
                    {whatIfResult.analysis}
                  </div>

                  {whatIfResult.key_obligations.length > 0 && (
                    <div className="mt-4">
                      <p className="text-xs text-slate-400 mb-2">Key new obligations:</p>
                      <ul className="text-sm text-slate-300 space-y-1 list-disc pl-5">
                        {whatIfResult.key_obligations.map((o, i) => (
                          <li key={i}>{o}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}