"""
Deterministic (rule-based) compliance checks derived directly from wizard answers.
These run BEFORE the RAG/LLM pipeline and are merged with LLM results.

Hardening notes (2026-09-18, review by Claude Sonnet — all 3 remediated here):

FIX 2 — Every article check below now runs on EVERY risk tier, unconditionally.
Previously Article 12 only fired for HIGH_RISK/PROHIBITED, and Articles 11/14
only fired for HIGH_RISK. That meant a LIMITED_RISK system with logging="no"
silently produced ZERO findings for Article 12 — a missing control could
never drag the score down because no check was ever emitted to score it.
Now: if the article's obligation genuinely does not apply to this tier, we
emit an explicit status="na" check with a rationale explaining why (never
silence). If the wizard answer is missing or an unrecognised value, we emit
status="warning" (never silence, never a free pass).

FIX 3 — A wizard answer of "yes" is the USER'S OWN CLAIM, not verified
evidence. Every check now carries `self_declared` and `evidence` fields
(see app/models/assessment.py). Self-declared "yes" with no evidence is
capped at score=70 and the rationale says so explicitly — it can no longer
score as if it were an audited pass (90-95).
"""
from typing import List, Optional

from app.models.assessment import ComplianceCheck, RiskTier

# Tiers where Chapter III obligations (Art. 11-15) apply in full.
_HIGH_RISK_TIERS = (RiskTier.HIGH_RISK,)
_PROHIBITED_OR_HIGH = (RiskTier.HIGH_RISK, RiskTier.PROHIBITED)

# Self-declared cap: a "yes" with no supporting evidence artefact can never
# score as high as a verified pass.
SELF_DECLARED_UNVERIFIED_CAP = 70


def _self_declared_score(claimed_score: int, evidence: Optional[str]) -> tuple[int, str]:
    """Cap a self-declared 'pass' score when no evidence artefact is supplied."""
    if evidence:
        return claimed_score, ""
    capped = min(claimed_score, SELF_DECLARED_UNVERIFIED_CAP)
    note = (
        f" [Self-declared: this reflects the respondent's own answer, not a "
        f"verified artefact. Score capped at {SELF_DECLARED_UNVERIFIED_CAP} "
        f"until supporting evidence is attached.]"
    )
    return capped, note


def run_deterministic_checks(answers: dict, risk_tier: RiskTier) -> List[ComplianceCheck]:
    """
    Run rule-based checks derived directly from wizard answers.
    Returns ComplianceCheck objects with proper source citations.

    Every article below ALWAYS emits exactly one ComplianceCheck, for every
    risk tier. There is no code path that silently emits nothing.
    """
    checks: List[ComplianceCheck] = []

    # ── Article 12 — Logging ────────────────────────────────────────────────
    logging_answer = answers.get("logging")
    evidence = answers.get("logging_evidence")

    if risk_tier not in _PROHIBITED_OR_HIGH:
        checks.append(ComplianceCheck(
            article="Article 12",
            requirement="Automatic logging of AI system events",
            status="na",
            score=100,
            rationale=(
                f"Article 12's mandatory automatic-logging obligation applies to "
                f"high-risk and prohibited AI systems. This system is classified as "
                f"'{risk_tier.value}', so this specific obligation does not apply — "
                f"logging may still be good practice, but it is not a legal requirement here."
            ),
            remediation=None,
            source_citation="High-risk AI systems shall be designed and developed with the technical capability to automatically record events (logs) while the high-risk AI system is operating.",
            self_declared=False,
        ))
    elif logging_answer == "no":
        checks.append(ComplianceCheck(
            article="Article 12",
            requirement="Automatic logging of AI system events",
            status="fail",
            score=20,
            rationale="Logging is disabled. Article 12 requires automatic recording of events for high-risk and prohibited systems.",
            remediation="Enable automatic logging of all AI system operations, including start/end timestamps and key decisions.",
            source_citation="High-risk AI systems shall be designed and developed with the technical capability to automatically record events (logs) while the high-risk AI system is operating.",
            self_declared=True,
            evidence=evidence,
        ))
    elif logging_answer == "partial":
        checks.append(ComplianceCheck(
            article="Article 12",
            requirement="Automatic logging of AI system events",
            status="warning",
            score=60,
            rationale="Logging is only partially implemented. Full traceability is required under Article 12.",
            remediation="Expand logging to cover all required events: period of use, input data, and verification steps.",
            source_citation="Logging capabilities shall enable the identification of situations that may result in the high-risk AI system presenting a risk.",
            self_declared=True,
            evidence=evidence,
        ))
    elif logging_answer == "yes":
        score, note = _self_declared_score(95, evidence)
        checks.append(ComplianceCheck(
            article="Article 12",
            requirement="Automatic logging of AI system events",
            status="pass",
            score=score,
            rationale="Logging is fully enabled as required for this risk tier." + note,
            remediation=None,
            source_citation="High-risk AI systems shall be designed and developed with the technical capability to automatically record events (logs).",
            self_declared=True,
            evidence=evidence,
        ))
    else:
        # Missing or unrecognised wizard value for a tier where this
        # obligation DOES apply — never silence, never a free pass.
        checks.append(ComplianceCheck(
            article="Article 12",
            requirement="Automatic logging of AI system events",
            status="warning",
            score=40,
            rationale=(
                f"No usable answer was provided for the logging question "
                f"(got: {logging_answer!r}), but this system's risk tier "
                f"('{risk_tier.value}') requires Article 12 logging. Treated as "
                f"unverified/unknown, not as compliant."
            ),
            remediation="Answer the logging question in the wizard and provide evidence of automatic event logging.",
            source_citation="High-risk AI systems shall be designed and developed with the technical capability to automatically record events (logs) while the high-risk AI system is operating.",
            self_declared=False,
        ))

    # ── Article 13 — Transparency disclosure ────────────────────────────────
    # Article 13 sits in Chapter III with 11/12/14 and only binds high-risk
    # (and prohibited) systems. Gated the same way for consistency — it was
    # previously ungated, the same "missing control can't drag the score
    # down" pattern flagged for Articles 11/12/14.
    ai_disclosure = answers.get("ai_disclosure")
    disclosure_evidence = answers.get("ai_disclosure_evidence")

    if risk_tier not in _HIGH_RISK_TIERS:
        checks.append(ComplianceCheck(
            article="Article 13",
            requirement="Transparency and provision of information to deployers",
            status="na",
            score=100,
            rationale=(
                f"Article 13's deployer-transparency obligation applies specifically "
                f"to high-risk AI systems. This system is classified as "
                f"'{risk_tier.value}', so this obligation does not apply here "
                f"(general Article 50 disclosure duties may still apply separately)."
            ),
            remediation=None,
            source_citation="High-risk AI systems shall be designed and developed in such a way as to ensure that their operation is sufficiently transparent to enable deployers to interpret the system's output.",
            self_declared=False,
        ))
    elif ai_disclosure == "no":
        checks.append(ComplianceCheck(
            article="Article 13",
            requirement="Transparency and provision of information to deployers",
            status="fail",
            score=10,
            rationale="No AI disclosure is provided to users. Article 13 requires clear information about system capabilities and limitations.",
            remediation="Implement clear disclosure that users are interacting with an AI system, including capabilities and limitations.",
            source_citation="High-risk AI systems shall be designed and developed in such a way as to ensure that their operation is sufficiently transparent to enable deployers to interpret the system's output.",
            self_declared=True,
            evidence=disclosure_evidence,
        ))
    elif ai_disclosure == "yes":
        score, note = _self_declared_score(90, disclosure_evidence)
        checks.append(ComplianceCheck(
            article="Article 13",
            requirement="Transparency and provision of information to deployers",
            status="pass",
            score=score,
            rationale="AI disclosure is provided to users." + note,
            remediation=None,
            source_citation="High-risk AI systems shall be accompanied by instructions for use... that include concise, complete, correct and clear information.",
            self_declared=True,
            evidence=disclosure_evidence,
        ))
    elif ai_disclosure == "na":
        checks.append(ComplianceCheck(
            article="Article 13",
            requirement="Transparency and provision of information to deployers",
            status="na",
            score=100,
            rationale="Transparency obligations do not apply to this use case (e.g. law-enforcement exemption).",
            remediation=None,
            source_citation="This obligation shall not apply to AI systems authorised by law to detect, prevent, investigate and prosecute criminal offences.",
            self_declared=False,
        ))
    else:
        checks.append(ComplianceCheck(
            article="Article 13",
            requirement="Transparency and provision of information to deployers",
            status="warning",
            score=40,
            rationale=(
                f"No usable answer was provided for the AI-disclosure question "
                f"(got: {ai_disclosure!r}). Treated as unverified/unknown, not as compliant."
            ),
            remediation="Answer the AI-disclosure question in the wizard.",
            source_citation="High-risk AI systems shall be designed and developed in such a way as to ensure that their operation is sufficiently transparent to enable deployers to interpret the system's output.",
            self_declared=False,
        ))

    # ── Article 14 — Human oversight ────────────────────────────────────────
    human_oversight = answers.get("human_oversight")
    oversight_evidence = answers.get("human_oversight_evidence")

    if risk_tier not in _HIGH_RISK_TIERS:
        checks.append(ComplianceCheck(
            article="Article 14",
            requirement="Human oversight measures",
            status="na",
            score=100,
            rationale=(
                f"Article 14's human-oversight obligation applies specifically to "
                f"high-risk AI systems. This system is classified as '{risk_tier.value}', "
                f"so this obligation does not apply here."
            ),
            remediation=None,
            source_citation="High-risk AI systems shall be designed and developed in such a way... that they can be effectively overseen by natural persons during the period in which they are in use.",
            self_declared=False,
        ))
    elif human_oversight == "no":
        checks.append(ComplianceCheck(
            article="Article 14",
            requirement="Human oversight measures",
            status="fail",
            score=15,
            rationale="No human oversight is implemented. Article 14 requires effective human oversight for all high-risk AI systems.",
            remediation="Implement human oversight mechanisms allowing a natural person to monitor, intervene, and override AI outputs.",
            source_citation="High-risk AI systems shall be designed and developed in such a way... that they can be effectively overseen by natural persons during the period in which they are in use.",
            self_declared=True,
            evidence=oversight_evidence,
        ))
    elif human_oversight == "partial":
        checks.append(ComplianceCheck(
            article="Article 14",
            requirement="Human oversight measures",
            status="warning",
            score=55,
            rationale="Human oversight is only partially implemented. Full oversight capability is required for high-risk systems.",
            remediation="Ensure at least one natural person can fully monitor, interpret, and override AI system outputs.",
            source_citation="Human oversight measures shall enable the individuals to whom human oversight is assigned to... decide, in any particular situation, not to use the high-risk AI system or otherwise disregard, override or reverse the output.",
            self_declared=True,
            evidence=oversight_evidence,
        ))
    elif human_oversight == "yes_full":
        score, note = _self_declared_score(95, oversight_evidence)
        checks.append(ComplianceCheck(
            article="Article 14",
            requirement="Human oversight measures",
            status="pass",
            score=score,
            rationale="Full human oversight is implemented as required." + note,
            remediation=None,
            source_citation="High-risk AI systems shall be designed and developed in such a way... that they can be effectively overseen by natural persons.",
            self_declared=True,
            evidence=oversight_evidence,
        ))
    else:
        checks.append(ComplianceCheck(
            article="Article 14",
            requirement="Human oversight measures",
            status="warning",
            score=40,
            rationale=(
                f"No usable answer was provided for the human-oversight question "
                f"(got: {human_oversight!r}), but this system's risk tier "
                f"('{risk_tier.value}') requires Article 14 oversight. Treated as "
                f"unverified/unknown, not as compliant."
            ),
            remediation="Answer the human-oversight question in the wizard and describe the override mechanism.",
            source_citation="High-risk AI systems shall be designed and developed in such a way... that they can be effectively overseen by natural persons during the period in which they are in use.",
            self_declared=False,
        ))

    # ── Article 11 — Technical documentation ────────────────────────────────
    tech_docs = answers.get("technical_documentation")
    tech_docs_evidence = answers.get("technical_documentation_evidence")

    if risk_tier not in _HIGH_RISK_TIERS:
        checks.append(ComplianceCheck(
            article="Article 11",
            requirement="Technical documentation (Annex IV)",
            status="na",
            score=100,
            rationale=(
                f"Article 11's Annex IV technical-documentation obligation applies "
                f"specifically to high-risk AI systems. This system is classified as "
                f"'{risk_tier.value}', so this obligation does not apply here."
            ),
            remediation=None,
            source_citation="The technical documentation of a high-risk AI system shall be drawn up before that system is placed on the market or put into service and shall be kept up-to date.",
            self_declared=False,
        ))
    elif tech_docs == "no":
        checks.append(ComplianceCheck(
            article="Article 11",
            requirement="Technical documentation (Annex IV)",
            status="fail",
            score=20,
            rationale="Technical documentation is missing. Article 11 requires comprehensive documentation before placing a high-risk AI system on the market.",
            remediation="Create technical documentation covering: general description, design specifications, data requirements, human oversight measures, and accuracy/robustness/cybersecurity measures.",
            source_citation="The technical documentation of a high-risk AI system shall be drawn up before that system is placed on the market or put into service and shall be kept up-to date.",
            self_declared=True,
            evidence=tech_docs_evidence,
        ))
    elif tech_docs == "in_progress":
        checks.append(ComplianceCheck(
            article="Article 11",
            requirement="Technical documentation (Annex IV)",
            status="warning",
            score=50,
            rationale="Technical documentation is still being developed. Complete documentation is required before deployment.",
            remediation="Finalize technical documentation including all Annex IV elements and establish a process to keep it up to date.",
            source_citation="The technical documentation shall be drawn up in such a way as to demonstrate that the high-risk AI system complies with the requirements set out in this Chapter.",
            self_declared=True,
            evidence=tech_docs_evidence,
        ))
    elif tech_docs == "yes":
        score, note = _self_declared_score(95, tech_docs_evidence)
        rationale = "Technical documentation is complete and maintained." if note == "" else (
            "Respondent states technical documentation is complete and maintained." + note
        )
        checks.append(ComplianceCheck(
            article="Article 11",
            requirement="Technical documentation (Annex IV)",
            status="pass",
            score=score,
            rationale=rationale,
            remediation=None,
            source_citation="The technical documentation of a high-risk AI system shall be drawn up before that system is placed on the market or put into service and shall be kept up-to date.",
            self_declared=True,
            evidence=tech_docs_evidence,
        ))
    else:
        checks.append(ComplianceCheck(
            article="Article 11",
            requirement="Technical documentation (Annex IV)",
            status="warning",
            score=40,
            rationale=(
                f"No usable answer was provided for the technical-documentation "
                f"question (got: {tech_docs!r}), but this system's risk tier "
                f"('{risk_tier.value}') requires Article 11 documentation. Treated "
                f"as unverified/unknown, not as compliant."
            ),
            remediation="Answer the technical-documentation question in the wizard and attach the Annex IV package.",
            source_citation="The technical documentation of a high-risk AI system shall be drawn up before that system is placed on the market or put into service and shall be kept up-to date.",
            self_declared=False,
        ))

    return checks
