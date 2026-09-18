export type RiskTier = 'prohibited' | 'high_risk' | 'limited_risk' | 'minimal_risk';

export type CheckStatus = 'pass' | 'fail' | 'warning' | 'na';

export interface ComplianceCheck {
  article: string;         // e.g. "Article 5", "Article 10"
  requirement: string;
  status: CheckStatus;
  score: number;           // 0–100
  rationale: string;
  remediation?: string;
  source_citation: string; // exact Act passage
  self_declared?: boolean; // true if this "pass" rests only on the respondent's own claim, not verified evidence
  evidence?: string | null; // description of the supporting artefact, if any
}

export interface ComplianceReport {
  id: string;
  assessment_id: string;
  risk_tier: RiskTier;
  // null = "not assessed" (zero scoreable checks) — render as "niet
  // beoordeeld", NEVER default this to a number in the UI.
  overall_score: number | null;
  checks: ComplianceCheck[];
  generated_at: string;    // ISO datetime
  processing_time_seconds: number;
  answers?: WizardAnswers;
}

export type WizardAnswers = Record<string, string | string[] | boolean>;

export interface Assessment {
  id: string;
  created_at: string;
  answers: WizardAnswers;
  report?: ComplianceReport;
  status: 'pending' | 'processing' | 'complete' | 'error';
}

export interface WhatIfResponse {
  original_tier: RiskTier;
  new_tier: RiskTier;
  changed: boolean;
  analysis: string;
  key_obligations: string[];
}

export interface WizardQuestion {
  id: string;
  step: number;
  question: string;
  helpText?: string;
  type: 'text' | 'textarea' | 'select' | 'radio' | 'boolean';
  options?: { label: string; value: string }[];
  required: boolean;
  euAiActArticle?: string; // which article this maps to
}
