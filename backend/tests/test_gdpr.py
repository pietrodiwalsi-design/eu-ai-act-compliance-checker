"""Tests for GDPR deletion and export endpoints (NFR-03)."""
import json
import pytest
from pathlib import Path

from app.services.persistence import (
    ASSESSMENTS_DIR,
    delete_all_user_data,
    delete_assessment,
    delete_report,
    save_assessment,
    save_report,
    load_assessment,
    load_report,
    _reports_cache,
    _assessments_cache,
)
from app.models.assessment import (
    AssessmentResponse,
    ComplianceReport,
    ComplianceCheck,
    RiskTier,
)
from datetime import datetime, timezone


def _make_report(report_id: str = "r1", assessment_id: str = "a1") -> ComplianceReport:
    return ComplianceReport(
        id=report_id,
        assessment_id=assessment_id,
        risk_tier=RiskTier.MINIMAL_RISK,
        overall_score=80,
        checks=[
            ComplianceCheck(
                article="Article 5",
                requirement="Not prohibited",
                status="pass",
                score=100,
                rationale="OK",
                source_citation="Art 5(1)",
            )
        ],
        generated_at=datetime.now(timezone.utc),
        processing_time_seconds=1.5,
    )


def _make_assessment(assessment_id: str = "a1", report: ComplianceReport = None) -> AssessmentResponse:
    return AssessmentResponse(
        id=assessment_id,
        created_at=datetime.now(timezone.utc),
        answers={"q1": "test"},
        report=report,
        status="complete",
    )


@pytest.fixture(autouse=True)
def clean_data():
    """Clean up test data before and after each test."""
    _reports_cache.clear()
    _assessments_cache.clear()
    yield
    # Cleanup any test files
    for p in ASSESSMENTS_DIR.glob("*test_*.json"):
        p.unlink(missing_ok=True)


def test_delete_report():
    report = _make_report(report_id="test_r1")
    save_report(report)
    assert load_report("test_r1") is not None
    assert delete_report("test_r1") is True
    assert load_report("test_r1") is None


def test_delete_assessment_cascades_report():
    report = _make_report(report_id="test_r2", assessment_id="test_a2")
    save_report(report)
    assessment = _make_assessment(assessment_id="test_a2", report=report)
    save_assessment(assessment)

    assert delete_assessment("test_a2") is True
    # Both assessment and linked report should be gone
    assert load_assessment("test_a2") is None
    assert load_report("test_r2") is None


def test_delete_nonexistent_returns_false():
    assert delete_assessment("nonexistent_id_xyz") is False
    assert delete_report("nonexistent_id_xyz") is False


def test_delete_all_user_data():
    # Save a few items
    for i in range(3):
        r = _make_report(report_id=f"test_bulk_r{i}", assessment_id=f"test_bulk_a{i}")
        save_report(r)
        a = _make_assessment(assessment_id=f"test_bulk_a{i}", report=r)
        save_assessment(a)

    count = delete_all_user_data()
    assert count >= 6  # 3 reports + 3 assessments at minimum
    assert len(_reports_cache) == 0
    assert len(_assessments_cache) == 0
