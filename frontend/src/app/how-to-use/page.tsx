import Link from 'next/link';

export default function HowToUsePage() {
  return (
    <main className="min-h-screen bg-slate-900 text-white">
      {/* Header */}
      <header className="border-b border-white/10 px-6 py-4 flex items-center justify-between max-w-7xl mx-auto">
        <Link href="/" className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-blue-500 flex items-center justify-center text-sm font-bold">EU</div>
          <span className="font-semibold text-lg">AI Act Checker</span>
        </Link>
        <nav className="flex gap-6 text-sm text-slate-300">
          <Link href="/dashboard" className="hover:text-white transition-colors">Dashboard</Link>
          <Link href="/assess" className="hover:text-white transition-colors">New Assessment</Link>
          <Link href="/how-to-use" className="text-white font-medium transition-colors">How to Use</Link>
        </nav>
      </header>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-6 py-12">
        <h1 className="text-3xl font-bold mb-8">How to Use the EU AI Act Compliance Checker</h1>
        
        <div className="space-y-8 text-slate-300">
          <section className="bg-slate-800/60 border border-white/10 rounded-2xl p-6">
            <h2 className="text-xl font-semibold text-white mb-4">1. Start an Assessment</h2>
            <p className="mb-2">Click on <strong>New Assessment</strong> to begin the intake wizard. You will be asked 15 clear questions about your AI system, covering:</p>
            <ul className="list-disc pl-6 space-y-1">
              <li>The system's main purpose and sector.</li>
              <li>Whether it makes decisions affecting individuals or uses biometric data.</li>
              <li>Details about training data, logging, and human oversight.</li>
            </ul>
          </section>

          <section className="bg-slate-800/60 border border-white/10 rounded-2xl p-6">
            <h2 className="text-xl font-semibold text-white mb-4">2. Wait for the Analysis</h2>
            <p>Once you submit your answers, the system takes up to 3 minutes to process. It uses a combination of deterministic (rule-based) checks and an AI-driven RAG (Retrieval-Augmented Generation) pipeline to compare your system against the official EU AI Act legal texts.</p>
          </section>

          <section className="bg-slate-800/60 border border-white/10 rounded-2xl p-6">
            <h2 className="text-xl font-semibold text-white mb-4">3. Review Your Compliance Report</h2>
            <p className="mb-2">The final report gives you a clear, actionable overview:</p>
            <ul className="list-disc pl-6 space-y-1">
              <li><strong>Risk Tier:</strong> Your system is classified as Minimal, Limited, High-Risk, or Prohibited.</li>
              <li><strong>Traffic-Light Score:</strong> A 0-100 overall score with red/yellow/green indicators for specific requirements.</li>
              <li><strong>Remediation Steps:</strong> Actionable advice telling you exactly what to fix to achieve compliance.</li>
            </ul>
          </section>

          <section className="bg-slate-800/60 border border-white/10 rounded-2xl p-6">
            <h2 className="text-xl font-semibold text-white mb-4">4. Check Your Dashboard</h2>
            <p>All your past assessments are automatically saved to your browser and can be accessed at any time via the <strong>Dashboard</strong> tab. From there, you can re-open past reports to track your compliance progress over time.</p>
          </section>
        </div>

        <div className="mt-12 text-center">
          <Link
            href="/assess"
            className="inline-flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold px-8 py-4 rounded-xl transition-colors"
          >
            Start Your First Assessment →
          </Link>
        </div>
      </div>
    </main>
  );
}
