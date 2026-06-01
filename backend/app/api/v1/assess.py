"""
POST /api/v1/assess  — run a full EU AI Act compliance assessment.
GET  /api/v1/assessments — list all assessments (stub, in-memory for Phase 1).
GET  /api/v1/reports/{id} — fetch a specific report.
"""
from __future__ import annotations

import asyncio
import time
import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, HTTPException

from app.models.assessment import (
    AssessmentRequest,
    AssessmentResponse,
    ComplianceReport,
    RiskTier,
)
from app.services.classifier import classify_risk_tier
from app.services.rag import rag_pipeline
from app.services.remediation import calculate_overall_score, enrich_checks_with_remediation

router = APIRouter()

# In-memory store for Phase 1 (replace with DB in Phase 4)
_assessments: dict[str, AssessmentResponse] = {}
_reports: dict[str, ComplianceReport] = {}


@router.post("/assess", response_model=ComplianceReport, status_code=201)
async def run_assessment(request: AssessmentRequest) -> ComplianceReport:
    """
    Run a full EU AI Act compliance assessment.

    - Classifies risk tier (rule-based)
    - Runs RAG + LLM compliance analysis
    - Enriches with remediation steps
    - Returns structured ComplianceReport

    Target: < 3 minutes (NFR-01)
    """
    start_time = time.monotonic()
    assessment_id = str(uuid.uuid4())

    try:
        # ── 1. Classify risk tier ────────────────────────────────────────────
        risk_tier: RiskTier = classify_risk_tier(request.answers)

        # ── 2. RAG + LLM analysis ────────────────────────────────────────────
        checks = await asyncio.wait_for(
            rag_pipeline.generate_compliance_analysis(request.answers, risk_tier),
            timeout=170.0,  # leave buffer within 3-min SLA
        )

        # ── 3. Enrich with remediation ───────────────────────────────────────
        checks = enrich_checks_with_remediation(checks, risk_tier)

        # ── 4. Calculate overall score ───────────────────────────────────────
        overall_score = calculate_overall_score(checks)

        # ── 5. Assemble report ───────────────────────────────────────────────
        report = ComplianceReport(
            id=str(uuid.uuid4()),
            assessment_id=assessment_id,
            risk_tier=risk_tier,
            overall_score=overall_score,
            checks=checks,
            generated_at=datetime.now(timezone.utc),
            processing_time_seconds=round(time.monotonic() - start_time, 2),
        )

        # Persist (in-memory Phase 1)
        _reports[report.id] = report
        _assessments[assessment_id] = AssessmentResponse(
            id=assessment_id,
            created_at=datetime.now(timezone.utc),
            answers=request.answers,
            report=report,
            status="complete",
        )

        return report

    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Assessment timed out. The system took longer than 3 minutes to process.",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/assessments", response_model=List[AssessmentResponse])
async def list_assessments() -> List[AssessmentResponse]:
    """Return all assessments (newest first)."""
    return sorted(_assessments.values(), key=lambda a: a.created_at, reverse=True)


@router.get("/reports/{report_id}", response_model=ComplianceReport)
async def get_report(report_id: str) -> ComplianceReport:
    """Fetch a specific compliance report by ID."""
    report = _reports.get(report_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"Report {report_id!r} not found")
    return report
