"""
File-based persistence for assessments and reports (Phase 2).
Replaces in-memory dicts. Stores JSON files under ./data/assessments/
"""
from __future__ import annotations

import json
from datetime import datetime
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