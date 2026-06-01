"""
Remediation engine — maps compliance gaps to actionable remediation steps.

Phase 1: lookup table per article + risk tier.
Phase 2: LLM-generated bespoke remediation with LangChain.
"""
from app.models.assessment import ComplianceCheck, RiskTier

# Per-article remediation playbook
REMEDIATION_PLAYBOOK: dict[str, str] = {
    "Article 5":  "Immediately cease or redesign the prohibited practice. Conduct a legal review to confirm the system falls outside Article 5 prohibited uses before re-deployment.",
    "Article 10": "Establish a formal data governance policy: document data sources, run bias audits, obtain legal basis for all training data (GDPR Art. 6), and implement a data quality monitoring process.",
    "Article 11": "Draft Annex IV-compliant technical documentation covering: system purpose, architecture, training methodology, performance metrics, and known limitations. Assign a responsible owner.",
    "Article 12": "Implement automated event logging covering all system decisions, inputs, and outputs. Define a log retention policy (minimum 10 years for high-risk systems) and ensure logs are tamper-proof.",
    "Article 13": "Add clear, prominent disclosures informing users they are interacting with an AI system. For high-risk systems, publish technical documentation accessible to downstream deployers.",
    "Article 14": "Implement a human-in-the-loop review mechanism with documented override capability. Train operators to recognise and correct automation bias. Test override procedures regularly.",
    "Article 15": "Conduct adversarial robustness testing and document results. Implement input validation, anomaly detection, and fallback mechanisms. Commission a cybersecurity assessment.",
    "Article 50": "Disclose AI-generated content with machine-readable watermarks or explicit labels. For chatbots, display 'You are interacting with an AI' at session start.",
    "Article 51": "Register the GPAI model in the EU AI Act GPAI register. Publish a training data summary with copyright compliance evidence. Document systemic risk mitigation measures.",
    "Annex III":  "Complete a Conformity Assessment before deployment. Register the high-risk system in the EU database (Art. 71). Appoint a qualified person responsible for compliance.",
}


def enrich_checks_with_remediation(
    checks: list[ComplianceCheck],
    risk_tier: RiskTier,
) -> list[ComplianceCheck]:
    """
    Ensure every failing or warning check has a populated remediation field.
    Falls back to the playbook if the LLM left it empty.
    """
    enriched = []
    for check in checks:
        c = check.model_copy()
        if c.status in ("fail", "warning") and not c.remediation:
            # Try to match by article key
            for article_key, action in REMEDIATION_PLAYBOOK.items():
                if article_key.lower() in c.article.lower():
                    c.remediation = action
                    break
            else:
                c.remediation = (
                    f"Review the system's compliance with {c.article} "
                    f"and implement the required controls before deployment."
                )
        enriched.append(c)
    return enriched


def calculate_overall_score(checks: list[ComplianceCheck]) -> int:
    """Weighted average score across all applicable checks."""
    applicable = [c for c in checks if c.status != "na"]
    if not applicable:
        return 100
    return round(sum(c.score for c in applicable) / len(applicable))
