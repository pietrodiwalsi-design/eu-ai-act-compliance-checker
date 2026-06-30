import Link from 'next/link';

export default function HomePage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 text-white">
      {/* Header */}
      <header className="border-b border-white/10 px-6 py-4 flex items-center justify-between max-w-7xl mx-auto">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-blue-500 flex items-center justify-center text-sm font-bold">EU</div>
          <span className="font-semibold text-lg">AI Act Checker</span>
        </div>
        <nav className="flex gap-6 text-sm text-slate-300">
          <Link href="/dashboard" className="hover:text-white transition-colors">Dashboard</Link>
          <Link href="/assess" className="hover:text-white transition-colors">New Assessment</Link>
          <Link href="/how-to-use" className="hover:text-white transition-colors">How to Use</Link>
        </nav>
      </header>

      {/* Hero */}
      <section className="max-w-4xl mx-auto px-6 py-24 text-center">
        <div className="inline-flex items-center gap-2 bg-blue-500/10 border border-blue-500/20 rounded-full px-4 py-1.5 text-sm text-blue-300 mb-8">
          <span className="w-2 h-2 rounded-full bg-blue-400 animate-pulse" />
          EU AI Act — In force from August 2024
        </div>

        <h1 className="text-5xl font-bold leading-tight mb-6">
          Is your AI system<br />
          <span className="text-blue-400">EU AI Act compliant?</span>
        </h1>

        <p className="text-xl text-slate-300 max-w-2xl mx-auto mb-10 leading-relaxed">
          Answer 15 questions about your AI system and get a full compliance report in under 3 minutes —
          with risk classification, gap analysis, and actionable remediation steps mapped to exact EU AI Act Articles.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/assess"
            className="inline-flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold px-8 py-4 rounded-xl text-lg transition-colors"
          >
            Start Free Assessment →
          </Link>
          <Link
            href="/dashboard"
            className="inline-flex items-center justify-center gap-2 bg-white/5 hover:bg-white/10 border border-white/10 text-white font-semibold px-8 py-4 rounded-xl text-lg transition-colors"
          >
            View Dashboard
          </Link>
        </div>
      </section>

      {/* Feature Cards */}
      <section className="max-w-5xl mx-auto px-6 pb-24 grid grid-cols-1 md:grid-cols-3 gap-6">
        {[
          {
            icon: '🎯',
            title: 'Automated Risk Classification',
            desc: 'Instantly classified into Prohibited, High-Risk, Limited Risk, or Minimal Risk based on EU AI Act criteria.',
          },
          {
            icon: '🔴',
            title: 'Traffic-Light Compliance Score',
            desc: 'Red / Yellow / Green indicator per article with a 0–100 overall score to pinpoint critical gaps.',
          },
          {
            icon: '📋',
            title: 'Actionable Remediation',
            desc: 'Specific steps to fix every compliance gap, mapped to the exact EU AI Act article and EDPB guidance.',
          },
        ].map((f) => (
          <div key={f.title} className="bg-white/5 border border-white/10 rounded-2xl p-6 hover:bg-white/8 transition-colors">
            <div className="text-3xl mb-4">{f.icon}</div>
            <h3 className="font-semibold text-lg mb-2">{f.title}</h3>
            <p className="text-slate-400 text-sm leading-relaxed">{f.desc}</p>
          </div>
        ))}
      </section>
    </main>
  );
}
