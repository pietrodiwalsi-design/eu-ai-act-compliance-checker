from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class RiskTier(str, Enum):
    PROHIBITED   = "prohibited"
    HIGH_RISK    = "high_risk"
    LIMITED_RISK = "limited_risk"
    MINIMAL_RISK = "minimal_risk"


class ComplianceCheck(BaseModel):
    article:         str                                    # e.g. "Article 5", "Article 10"
    requirement:     str
    status:          Literal["pass", "fail", "warning", "na"]
    score:           int = Field(..., ge=0, le=100)         # 0–100
    rationale:       str
    remediation:     Optional[str] = None
    source_citation: str                                    # exact Act passage


class ComplianceReport(BaseModel):
    id:                      str
    assessment_id:           str
    risk_tier:               RiskTier
    overall_score:           int = Field(..., ge=0, le=100)
    checks:                  List[ComplianceCheck]
    generated_at:            datetime
    processing_time_seconds: float


class AssessmentRequest(BaseModel):
    answers: Dict[str, object]  # wizard answers keyed by question id


class AssessmentResponse(BaseModel):
    id:         str
    created_at: datetime
    answers:    Dict[str, object]
    report:     Optional[ComplianceReport] = None
    status:     Literal["pending", "processing", "complete", "error"] = "pending"
