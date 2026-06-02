"""
Risk tier classification service.

Phase 1: rule-based classifier implementing the EU AI Act decision tree.
Phase 2: LLM-enhanced classification via RAG will layer on top.

Decision order (mirrors the Act's logic):
  1. Prohibited practices (Article 5) → PROHIBITED
  2. High-risk sectors (Annex III) + filter provision → HIGH_RISK
  3. Transparency / limited-risk triggers (Articles 13, 50) → LIMITED_RISK
  4. Everything else → MINIMAL_RISK
"""
from app.models.assessment import RiskTier

# Sectors listed in Annex III of the EU AI Act
HIGH_RISK_SECTORS = {
    "healthcare",
    "employment",
    "education",
    "credit_finance",
    "law_enforcement",
    "critical_infrastructure",
    "migration",
    "justice",
}

# Answers that trigger prohibited-practice classification (Article 5)
PROHIBITED_TRIGGERS = {
    "biometric_data":            {"yes_realtime_public"},               # Art. 5(1)(d)
    "scoring_profiling":         {"yes_social"},                      # Art. 5(1)(c) — social scoring
    "manipulation_technique":    {"yes_subliminal"},                  # Art. 5(1)(a)
    "vulnerability_exploitation": {"yes"},                           # Art. 5(1)(b)
    "emotion_recognition_context": {"yes_workplace", "yes_education"}, # Art. 5(1)(e)
    "biometric_categorisation":  {"yes_sensitive"},                 # Art. 5(1)(f)
}


def classify_risk_tier(answers: dict) -> RiskTier:
    """
    Classify an AI system into one of the four EU AI Act risk tiers.

    Args:
        answers: wizard question answers keyed by question id

    Returns:
        RiskTier enum value
    """
    # ── Step 1: Prohibited practices (Article 5) ────────────────────────────
    for field, prohibited_values in PROHIBITED_TRIGGERS.items():
        if answers.get(field) in prohibited_values:
            return RiskTier.PROHIBITED

    # ── Step 2: High-risk (Annex III) ────────────────────────────────────────
    sector = answers.get("sector", "")
    affects_individuals = answers.get("affects_individuals", "no")
    impact_severity = answers.get("impact_severity", "low")

    if sector in HIGH_RISK_SECTORS:
        # Filter provision: downgrade if system is purely procedural and low impact
        is_procedural = (
            affects_individuals in ("no",)
            and impact_severity in ("low",)
        )
        if not is_procedural:
            return RiskTier.HIGH_RISK

    # Foundation model systemic risk also triggers HIGH_RISK
    if answers.get("foundation_model") == "yes_systemic":
        return RiskTier.HIGH_RISK

    # ── Step 3: Limited risk (Articles 13 & 50) ──────────────────────────────
    generative_ai = answers.get("generative_ai", "no")
    if generative_ai in ("yes_text", "yes_media", "yes_chatbot"):
        return RiskTier.LIMITED_RISK

    if answers.get("foundation_model") == "yes_standard":
        return RiskTier.LIMITED_RISK

    # ── Step 4: Minimal risk ─────────────────────────────────────────────────
    return RiskTier.MINIMAL_RISK
