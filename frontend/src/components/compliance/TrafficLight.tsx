'use client';

import { CheckStatus } from '@/types/assessment';

interface TrafficLightProps {
  status: CheckStatus;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

const STATUS_CONFIG: Record<CheckStatus, { color: string; bg: string; border: string; label: string }> = {
  pass:    { color: 'bg-emerald-500', bg: 'bg-emerald-500/10', border: 'border-emerald-500/30', label: 'Pass' },
  warning: { color: 'bg-amber-400',   bg: 'bg-amber-400/10',   border: 'border-amber-400/30',   label: 'Warning' },
  fail:    { color: 'bg-red-500',     bg: 'bg-red-500/10',     border: 'border-red-500/30',     label: 'Fail' },
  na:      { color: 'bg-slate-500',   bg: 'bg-slate-500/10',   border: 'border-slate-500/30',   label: 'N/A' },
};

const SIZE_MAP = {
  sm: { dot: 'w-2 h-2', text: 'text-xs', padding: 'px-2 py-0.5' },
  md: { dot: 'w-3 h-3', text: 'text-sm', padding: 'px-3 py-1' },
  lg: { dot: 'w-4 h-4', text: 'text-base', padding: 'px-4 py-1.5' },
};

export default function TrafficLight({ status, size = 'md', showLabel = true }: TrafficLightProps) {
  const cfg = STATUS_CONFIG[status];
  const sz = SIZE_MAP[size];

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border font-medium ${cfg.bg} ${cfg.border} ${sz.padding} ${sz.text}`}
    >
      <span className={`rounded-full flex-shrink-0 ${cfg.color} ${sz.dot}`} />
      {showLabel && <span className="text-white">{cfg.label}</span>}
    </span>
  );
}
