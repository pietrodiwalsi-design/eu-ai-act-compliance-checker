"""
File-based persistence for assessments and reports (Phase 2).
Replaces in-memory dicts. Stores JSON files under ./data/assessments/
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from app.models.assessment import AssessmentResponse, ComplianceReport

# Base directory for persisted assessments
ASSESSMENTS_DIR = Path(__file__).parent.parent.parent / "data" / "assessments"
ASSESSMENTS_DIR.mkdir(parents=True, exist_ok=True)

# In-memory cache — survives within a running process (covers same-request-cycle lookups)
_reports_cache: dict = {}
_assessments_cache: dict = {}


def _report_path(report_id: str) -> Path:
    return ASSESSMENTS_DIR / f"{report_id}.json"


def _assessment_path(assessment_id: str) -> Path:
    return ASSESSMENTS_DIR / f"assessment_{assessment_id}.json"


def save_report(report: ComplianceReport) -> None:
    """Write a ComplianceReport to data/assessments/{id}.json and cache in memory."""
    _reports_cache[report.id] = report
    try:
        path = _report_path(report.id)
        path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    except Exception as exc:
        import logging
        logging.getLogger(__name__).warning("Failed to write report to disk: %s", exc)


def load_report(report_id: str) -> Optional[ComplianceReport]:
    """Load a ComplianceReport by ID — checks memory cache first, then disk."""
    if report_id in _reports_cache:
        return _reports_cache[report_id]
    path = _report_path(report_id)
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    report = ComplianceReport(**data)
    _reports_cache[report_id] = report  # warm cache
    return report


def save_assessment(assessment: AssessmentResponse) -> None:
    """Write an AssessmentResponse to data/assessments/assessment_{id}.json and cache."""
    _assessments_cache[assessment.id] = assessment
    try:
        path = _assessment_path(assessment.id)
        path.write_text(assessment.model_dump_json(indent=2), encoding="utf-8")
    except Exception as exc:
        import logging
        logging.getLogger(__name__).warning("Failed to write assessment to disk: %s", exc)


def load_assessment(assessment_id: str) -> Optional[AssessmentResponse]:
    """Load an AssessmentResponse by ID. Returns None if not found."""
    path = _assessment_path(assessment_id)
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return AssessmentResponse(**data)


def list_assessments() -> List[AssessmentResponse]:
    """Load all assessments, sorted newest first."""
    assessments: List[AssessmentResponse] = []
    for path in sorted(ASSESSMENTS_DIR.glob("assessment_*.json"), reverse=True):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            assessments.append(AssessmentResponse(**data))
        except Exception:
            # Skip corrupted files
            continue
    return assessments


# ── GDPR data deletion (NFR-03) ─────────────────────────────────────────────


def delete_assessment(assessment_id: str) -> bool:
    """Delete a single assessment and its linked report. Returns True if found.

    Accepts EITHER an assessment ID OR a report ID. The frontend only ever
    knows/displays the *report* ID (see report/[id]/page.tsx and the
    dashboard's localStorage cache) — it has no way to look up the separate
    assessment ID that this function historically required, which meant the
    delete endpoint always 404'd when called the way the UI actually calls
    it. Found + confirmed via an end-to-end test while wiring up the
    frontend delete button, 2026-07-07.
    """
    # First try treating the input as an assessment ID (original behaviour).
    assessment = load_assessment(assessment_id)
    resolved_assessment_id = assessment_id

    if assessment is None:
        # Fall back: treat the input as a report ID and find the assessment
        # that links to it.
        report = load_report(assessment_id)
        if report is not None:
            for candidate in list_assessments():
                if candidate.report and candidate.report.id == assessment_id:
                    assessment = candidate
                    resolved_assessment_id = candidate.id
                    break

    found = False

    if assessment and assessment.report:
        delete_report(assessment.report.id)

    # Delete assessment file (using whichever ID we actually resolved to)
    path = _assessment_path(resolved_assessment_id)
    if path.exists():
        path.unlink()
        found = True
    _assessments_cache.pop(resolved_assessment_id, None)

    # If we only ever found a bare report (no assessment record at all,
    # e.g. legacy data), still delete the report file itself.
    if not found and assessment is None:
        found = delete_report(assessment_id)

    return found


def delete_report(report_id: str) -> bool:
    """Delete a single report. Returns True if found."""
    found = False
    path = _report_path(report_id)
    if path.exists():
        path.unlink()
        found = True
    _reports_cache.pop(report_id, None)
    return found


def delete_all_user_data() -> int:
    """Delete ALL assessments and reports (full GDPR erasure). Returns count deleted."""
    count = 0
    for path in ASSESSMENTS_DIR.glob("*.json"):
        try:
            path.unlink()
            count += 1
        except Exception:
            continue
    _reports_cache.clear()
    _assessments_cache.clear()
    return count