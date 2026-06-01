'use client';

import { RiskTier } from '@/types/assessment';

interface ScoreCardProps {
  score: number;        // 0–100
  riskTier: RiskTier;
}

const TIER_CONFIG: Record<RiskTier, { label: string; color: string; bg: string; border: string }> = {
  prohibited:    { label: 'Prohibited',    color: 'text-red-400',     bg: 'bg-red-500/10',     border: 'border-red-500/30' },
  high_risk:     { label: 'High Risk',     color: 'text-orange-400',  bg: 'bg-orange-500/10',  border: 'border-orange-500/30' },
  limited_risk:  { label: 'Limited Risk',  color: 'text-amber-400',   bg: 'bg-amber-400/10',   border: 'border-amber-400/30' },
  minimal_risk:  { label: 'Minimal Risk',  color: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/30' },
};

function getScoreColor(score: number): string {
  if (score >= 80) return '#10b981'; // emerald
  if (score >= 50) return '#f59e0b'; // amber
  return '#ef4444';                  // red
}

function getScoreLabel(score: number): string {
  if (score >= 80) return 'Compliant';
  if (score >= 50) return 'Partially Compliant';
  if (score > 0)   return 'Non-Compliant';
  return 'Prohibited';
}

export default function ScoreCard({ score, riskTier }: ScoreCardProps) {
  const tier = TIER_CONFIG[riskTier];
  const scoreColor = getScoreColor(score);
  const circumference = 2 * Math.PI * 52; // r=52
  const strokeDash = (score / 100) * circumference;

  return (
    <div className="bg-slate-800/60 border border-white/10 rounded-2xl p-8 flex flex-col items-center gap-6">
      {/* Circular progress */}
      <div className="relative w-36 h-36">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
          {/* Track */}
          <circle cx="60" cy="60" r="52" fill="none" stroke="#1e293b" strokeWidth="10" />
          {/* Progress */}
          <circle
            cx="60" cy="60" r="52"
            fill="none"
            stroke={scoreColor}
            strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={`${strokeDash} ${circumference}`}
            style={{ transition: 'stroke-dasharray 0.8s ease' }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl font-bold text-white">{score}</span>
          <span className="text-xs text-slate-400">/ 100</span>
        </div>
      </div>

      {/* Score label */}
      <div className="text-center">
        <p className="font-semibold text-lg text-white">{getScoreLabel(score)}</p>
        <p className="text-slate-400 text-sm mt-1">Overall compliance score</p>
      </div>

      {/* Risk tier badge */}
      <span className={`inline-flex items-center gap-2 rounded-full border px-4 py-1.5 text-sm font-medium ${tier.bg} ${tier.border} ${tier.color}`}>
        {riskTier === 'prohibited' && '🚫'}
        {riskTier === 'high_risk' && '🔴'}
        {riskTier === 'limited_risk' && '🟡'}
        {riskTier === 'minimal_risk' && '🟢'}
        {tier.label}
      </span>
    </div>
  );
}
