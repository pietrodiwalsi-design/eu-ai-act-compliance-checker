"""
Deterministic (rule-based) compliance checks derived directly from wizard answers.
These run BEFORE the RAG/LLM pipeline and are merged with LLM results.
"""
from typing import List
from app.models.assessment import ComplianceCheck, RiskTier


def run_deterministic_checks(answers: dict, risk_tier: RiskTier) -> List[ComplianceCheck]:
    """
    Run rule-based checks derived directly from wizard answers.
    Returns ComplianceCheck objects with proper source citations.
    """
    checks: List[ComplianceCheck] = []

    # ── Article 12 — Logging ────────────────────────────────────────────────
    logging = answers.get("logging")
    if logging == "no" and risk_tier in (RiskTier.HIGH_RISK, RiskTier.PROHIBITED):
        checks.append(ComplianceCheck(
            article="Article 12",
            requirement="Automatic logging of AI system events",
            status="fail",
            score=20,
            rationale="Logging is disabled. Article 12 requires automatic recording of events for high-risk and prohibited systems.",
            remediation="Enable automatic logging of all AI system operations, including start/end timestamps and key decisions.",
            source_citation="High-risk AI systems shall be designed and developed with the technical capability to automatically record events (logs) while the high-risk AI system is operating."
        ))
    elif logging == "partial":
        checks.append(ComplianceCheck(
            article="Article 12",
            requirement="Automatic logging of AI system events",
            status="warning",
            score=60,
            rationale="Logging is only partially implemented. Full traceability is required under Article 12.",
            remediation="Expand logging to cover all required events: period of use, input data, and verification steps.",
            source_citation="Logging capabilities shall enable the identification of situations that may result in the high-risk AI system presenting a risk."
        ))
    elif logging == "yes":
        checks.append(ComplianceCheck(
            article="Article 12",
            requirement="Automatic logging of AI system events",
            status="pass",
            score=95,
            rationale="Logging is fully enabled as required for this risk tier.",
            remediation=None,
            source_citation="High-risk AI systems shall be designed and developed with the technical capability to automatically record events (logs)."
        ))

    # ── Article 13 — Transparency disclosure ────────────────────────────────
    ai_disclosure = answers.get("ai_disclosure")
    if ai_disclosure == "no":
        checks.append(ComplianceCheck(
            article="Article 13",
            requirement="Transparency and provision of information to deployers",
            status="fail",
            score=10,
            rationale="No AI disclosure is provided to users. Article 13 requires clear information about system capabilities and limitations.",
            remediation="Implement clear disclosure that users are interacting with an AI system, including capabilities and limitations.",
            source_citation="High-risk AI systems shall be designed and developed in such a way as to ensure that their operation is sufficiently transparent to enable deployers to interpret the system's output."
        ))
    elif ai_disclosure == "yes":
        checks.append(ComplianceCheck(
            article="Article 13",
            requirement="Transparency and provision of information to deployers",
            status="pass",
            score=90,
            rationale="AI disclosure is provided to users.",
            remediation=None,
            source_citation="High-risk AI systems shall be accompanied by instructions for use... that include concise, complete, correct and clear information."
        ))
    elif ai_disclosure == "na":
        checks.append(ComplianceCheck(
            article="Article 13",
            requirement="Transparency and provision of information to deployers",
            status="na",
            score=100,
            rationale="Transparency obligations do not apply to this use case.",
            remediation=None,
            source_citation="This obligation shall not apply to AI systems authorised by law to detect, prevent, investigate and prosecute criminal offences."
        ))

    # ── Article 14 — Human oversight ────────────────────────────────────────
    human_oversight = answers.get("human_oversight")
    if human_oversight == "no" and risk_tier == RiskTier.HIGH_RISK:
        checks.append(ComplianceCheck(
            article="Article 14",
            requirement="Human oversight measures",
            status="fail",
            score=15,
            rationale="No human oversight is implemented. Article 14 requires effective human oversight for all high-risk AI systems.",
            remediation="Implement human oversight mechanisms allowing a natural person to monitor, intervene, and override AI outputs.",
            source_citation="High-risk AI systems shall be designed and developed in such a way... that they can be effectively overseen by natural persons during the period in which they are in use."
        ))
    elif human_oversight == "partial":
        checks.append(ComplianceCheck(
            article="Article 14",
            requirement="Human oversight measures",
            status="warning",
            score=55,
            rationale="Human oversight is only partially implemented. Full oversight capability is required for high-risk systems.",
            remediation="Ensure at least one natural person can fully monitor, interpret, and override AI system outputs.",
            source_citation="Human oversight measures shall enable the individuals to whom human oversight is assigned to... decide, in any particular situation, not to use the high-risk AI system or otherwise disregard, override or reverse the output."
        ))
    elif human_oversight == "yes_full":
        checks.append(ComplianceCheck(
            article="Article 14",
            requirement="Human oversight measures",
            status="pass",
            score=95,
            rationale="Full human oversight is implemented as required.",
            remediation=None,
            source_citation="High-risk AI systems shall be designed and developed in such a way... that they can be effectively overseen by natural persons."
        ))

    # ── Article 11 — Technical documentation ────────────────────────────────
    tech_docs = answers.get("technical_documentation")
    if tech_docs == "no" and risk_tier == RiskTier.HIGH_RISK:
        checks.append(ComplianceCheck(
            article="Article 11",
            requirement="Technical documentation (Annex IV)",
            status="fail",
            score=20,
            rationale="Technical documentation is missing. Article 11 requires comprehensive documentation before placing a high-risk AI system on the market.",
            remediation="Create technical documentation covering: general description, design specifications, data requirements, human oversight measures, and accuracy/robustness/cybersecurity measures.",
            source_citation="The technical documentation of a high-risk AI system shall be drawn up before that system is placed on the market or put into service and shall be kept up-to date."
        ))
    elif tech_docs == "in_progress":
        checks.append(ComplianceCheck(
            article="Article 11",
            requirement="Technical documentation (Annex IV)",
            status="warning",
            score=50,
            rationale="Technical documentation is still being developed. Complete documentation is required before deployment.",
            remediation="Finalize technical documentation including all Annex IV elements and establish a process to keep it up to date.",
            source_citation="The technical documentation shall be drawn up in such a way as to demonstrate that the high-risk AI system complies with the requirements set out in this Chapter."
        ))
    elif tech_docs == "yes":
        checks.append(ComplianceCheck(
            article="Article 11",
            requirement="Technical documentation (Annex IV)",
            status="pass",
            score=95,
            rationale="Technical documentation is complete and maintained.",
            remediation=None,
            source_citation="The technical documentation of a high-risk AI system shall be drawn up before that system is placed on the market or put into service and shall be kept up-to date."
        ))

    return checks