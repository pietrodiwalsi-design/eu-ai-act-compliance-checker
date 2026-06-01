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
}

export interface ComplianceReport {
  id: string;
  assessment_id: string;
  risk_tier: RiskTier;
  overall_score: number;   // 0–100
  checks: ComplianceCheck[];
  generated_at: string;    // ISO datetime
  processing_time_seconds: number;
}

export type WizardAnswers = Record<string, string | string[] | boolean>;

export interface Assessment {
  id: string;
  created_at: string;
  answers: WizardAnswers;
  report?: ComplianceReport;
  status: 'pending' | 'processing' | 'complete' | 'error';
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
