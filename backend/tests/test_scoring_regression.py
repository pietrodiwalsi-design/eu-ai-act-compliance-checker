"""
Regression tests for the absence-of-evidence scoring bug (2026-09-18 review).

Core problem that was fixed: a system about which nothing is known used to
score as fully "compliant" (100). These tests assert the opposite —
"green" scores on known-bad or known-empty input must never happen. A
regression here means the accuracy gate described in the review has
regressed and the build should fail.

Covers FIX 1, FIX 2, FIX 3, FIX 5 in
  backend/app/services/deterministic_checks.py
  backend/app/services/remediation.py
  backend/app/models/assessment.py
"""
from app.models.assessment import RiskTier
from app.services.deterministic_checks import run_deterministic_checks
from app.services.remediation import calculate_overall_score


# ---------------------------------------------------------------------------
# FIX 1 + FIX 5 (negative case 1): all answers "na" -> overall score must
# NOT silently become 100. It must be `None` ("not assessed"), because every
# emitted check for a minimal-risk system is itself status="na" (Articles
# 11/12/14 do not apply outside high-risk/prohibited).
# ---------------------------------------------------------------------------
def test_all_na_answers_never_score_100_or_default_to_compliant():
    checks = run_deterministic_checks({}, RiskTier.MINIMAL_RISK)
    # Every check should be explicitly "na" with a rationale (never silent).
    assert len(checks) > 0
    for c in checks:
        assert c.status == "na"
        assert c.rationale  # never an empty/silent rationale
    score = calculate_overall_score(checks)
    assert score is None, (
        f"Expected 'not assessed' (None) for an all-N/A minimal-risk system, got {score}. "
        "A system with no applicable checks must never be reported as compliant."
    )
    assert score != 100


# ---------------------------------------------------------------------------
# FIX 5 (negative case 2): empty/missing answers on a HIGH_RISK system
# (where Articles 11/12/14 DO apply) must NOT score 100. Missing wizard
# answers must be treated as unknown/unverified (status="warning"), never
# as a free pass.
# ---------------------------------------------------------------------------
def test_empty_answers_on_high_risk_system_never_score_100():
    checks = run_deterministic_checks({}, RiskTier.HIGH_RISK)
    assert len(checks) == 4  # Articles 12, 13, 14, 11 each emit exactly one check
    for c in checks:
        assert c.status in ("warning", "fail"), (
            f"{c.article}: missing wizard answer on a high-risk system must never "
            f"be silently treated as compliant (got status={c.status!r})"
        )
        assert c.score < 100
    score = calculate_overall_score(checks)
    assert score is not None
    assert score < 100, f"Empty answers on a high-risk system scored {score} — should never be near-perfect."


# ---------------------------------------------------------------------------
# FIX 5 (negative case 3): limited-risk system with logging="no" — before
# the fix, this emitted ZERO Article 12 findings (the check only fired for
# HIGH_RISK/PROHIBITED), so a missing control could never drag the score
# down. Now every tier gets an explicit Article 12 finding.
# ---------------------------------------------------------------------------
def test_limited_risk_with_logging_no_still_yields_article_12_finding():
    checks = run_deterministic_checks({"logging": "no"}, RiskTier.LIMITED_RISK)
    article_12 = [c for c in checks if c.article == "Article 12"]
    assert len(article_12) == 1, "Article 12 must always emit exactly one finding, for every risk tier."
    # For LIMITED_RISK the obligation itself does not legally apply, so this
    # is correctly "na" — but it must be an EXPLICIT na with a rationale,
    # never silence, and never conflated with "logging is fine".
    assert article_12[0].status == "na"
    assert "does not apply" in article_12[0].rationale.lower() or "niet" in article_12[0].rationale.lower()


def test_high_risk_with_logging_no_produces_a_failing_article_12_finding():
    """Sanity check: on a tier where Article 12 DOES apply, logging=no must fail, not vanish."""
    checks = run_deterministic_checks({"logging": "no"}, RiskTier.HIGH_RISK)
    article_12 = [c for c in checks if c.article == "Article 12"]
    assert len(article_12) == 1
    assert article_12[0].status == "fail"
    assert article_12[0].score < 50


# ---------------------------------------------------------------------------
# FIX 3: self-declared "yes" with no evidence must be capped, and the cap
# must be reflected transparently in the rationale — never silently scored
# as if it were an audited/verified pass.
# ---------------------------------------------------------------------------
def test_self_declared_yes_without_evidence_is_capped_below_verified_pass():
    checks = run_deterministic_checks(
        {"technical_documentation": "yes"}, RiskTier.HIGH_RISK
    )
    art11 = next(c for c in checks if c.article == "Article 11")
    assert art11.status == "pass"
    assert art11.self_declared is True
    assert art11.evidence is None
    assert art11.score <= 70, (
        f"Self-declared 'yes' with no evidence scored {art11.score} — "
        "must be capped at or below the unverified ceiling."
    )
    assert "self-declared" in art11.rationale.lower()


def test_self_declared_yes_with_evidence_is_not_capped():
    checks = run_deterministic_checks(
        {
            "technical_documentation": "yes",
            "technical_documentation_evidence": "Annex IV pack reviewed 2026-08-01, ref DOC-4471",
        },
        RiskTier.HIGH_RISK,
    )
    art11 = next(c for c in checks if c.article == "Article 11")
    assert art11.status == "pass"
    assert art11.self_declared is True
    assert art11.evidence is not None
    assert art11.score == 95, "Score with real evidence attached should reach the full verified pass score."
