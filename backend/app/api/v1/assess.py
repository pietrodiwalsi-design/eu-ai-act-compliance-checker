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

from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import TokenData, get_current_user

from app.models.assessment import (
    AssessmentRequest,
    AssessmentResponse,
    ComplianceReport,
    RiskTier,
    WhatIfRequest,
    WhatIfResponse,
)
from app.services.classifier import classify_risk_tier
from app.services.deterministic_checks import run_deterministic_checks
from app.services.persistence import list_assessments as persistence_list_assessments, load_report, save_assessment, save_report
from app.services.rag import rag_pipeline
from app.services.remediation import calculate_overall_score, enrich_checks_with_remediation
from langchain_anthropic import ChatAnthropic
from app.prompts.classification import WHAT_IF_PROMPT
import os

router = APIRouter()




@router.post("/assess", response_model=ComplianceReport, status_code=201)
async def run_assessment(request: AssessmentRequest, _: TokenData = Depends(get_current_user)) -> ComplianceReport:
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

        # ── 2. Deterministic checks (fast, rule-based) ──────────────────────
        deterministic_checks = run_deterministic_checks(request.answers, risk_tier)

        # ── 3. RAG + LLM analysis ────────────────────────────────────────────
        llm_checks = await asyncio.wait_for(
            rag_pipeline.generate_compliance_analysis(request.answers, risk_tier),
            timeout=170.0,  # leave buffer within 3-min SLA
        )

        # Merge deterministic + LLM checks (deterministic first, then LLM)
        checks = deterministic_checks + llm_checks

        # ── 4. Enrich with remediation ───────────────────────────────────────
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

        # Persist to file system
        save_report(report)
        assessment = AssessmentResponse(
            id=assessment_id,
            created_at=datetime.now(timezone.utc),
            answers=request.answers,
            report=report,
            status="complete",
        )
        save_assessment(assessment)

        return report

    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Assessment timed out. The system took longer than 3 minutes to process.",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/assessments", response_model=List[AssessmentResponse])
async def list_assessments(_: TokenData = Depends(get_current_user)) -> List[AssessmentResponse]:
    """Return all assessments (newest first)."""
    return persistence_list_assessments()


@router.get("/reports/{report_id}", response_model=ComplianceReport)
async def get_report(report_id: str, _: TokenData = Depends(get_current_user)) -> ComplianceReport:
    """Fetch a specific compliance report by ID."""
    report = load_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"Report {report_id!r} not found")
    return report


@router.post("/whatif", response_model=WhatIfResponse)
async def what_if_analysis(request: WhatIfRequest, _: TokenData = Depends(get_current_user)) -> WhatIfResponse:
    """
    Re-evaluate risk tier and obligations for a different deployment context.
    Uses the WHAT_IF_PROMPT to call the LLM.
    """
    original_tier = classify_risk_tier(request.original_answers)

    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        temperature=0.3,
    )

    chain = WHAT_IF_PROMPT | llm
    response = await chain.ainvoke({
        "answers": request.original_answers,
        "original_tier": original_tier.value,
        "new_context": request.new_context,
    })

    # Simple parsing - in production this would be more robust
    content = response.content
    new_tier = original_tier  # fallback
    if "prohibited" in content.lower():
        new_tier = RiskTier.PROHIBITED
    elif "high_risk" in content.lower() or "high-risk" in content.lower():
        new_tier = RiskTier.HIGH_RISK
    elif "limited_risk" in content.lower():
        new_tier = RiskTier.LIMITED_RISK
    else:
        new_tier = RiskTier.MINIMAL_RISK

    changed = new_tier != original_tier

    # Extract top 3 obligations heuristically
    key_obligations = []
    for line in content.split("\n"):
        if any(kw in line.lower() for kw in ["article", "obligation", "must", "shall"]):
            key_obligations.append(line.strip())
            if len(key_obligations) >= 3:
                break

    return WhatIfResponse(
        original_tier=original_tier,
        new_tier=new_tier,
        changed=changed,
        analysis=content,
        key_obligations=key_obligations[:3] or ["Review full analysis for obligations"],
    )
