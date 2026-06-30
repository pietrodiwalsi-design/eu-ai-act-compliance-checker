"""
GDPR Article 17 — Right to Erasure endpoints (NFR-03).

DELETE /api/v1/assessments/{id}  — delete a single assessment + linked report
DELETE /api/v1/data              — delete ALL user data (full erasure)
GET    /api/v1/data/export       — export all user data (portability, Art. 20)
"""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.deps import TokenData, get_current_user
from app.models.assessment import AssessmentResponse
from app.services.persistence import (
    delete_all_user_data,
    delete_assessment,
    list_assessments,
)

router = APIRouter()


class DeletionResponse(BaseModel):
    status: str
    detail: str
    deleted_count: int = 0


class DataExportResponse(BaseModel):
    status: str
    assessments: List[AssessmentResponse]
    total_records: int


@router.delete("/assessments/{assessment_id}", response_model=DeletionResponse)
async def gdpr_delete_assessment(
    assessment_id: str,
    _: TokenData = Depends(get_current_user),
) -> DeletionResponse:
    """Delete a single assessment and its linked report (GDPR Art. 17)."""
    found = delete_assessment(assessment_id)
    if not found:
        raise HTTPException(status_code=404, detail=f"Assessment {assessment_id!r} not found")
    return DeletionResponse(
        status="deleted",
        detail=f"Assessment {assessment_id} and linked report permanently deleted.",
        deleted_count=1,
    )


@router.delete("/data", response_model=DeletionResponse)
async def gdpr_delete_all_data(
    _: TokenData = Depends(get_current_user),
) -> DeletionResponse:
    """Delete ALL user assessments and reports (GDPR full erasure)."""
    count = delete_all_user_data()
    return DeletionResponse(
        status="deleted",
        detail=f"All user data permanently deleted ({count} files removed).",
        deleted_count=count,
    )


@router.get("/data/export", response_model=DataExportResponse)
async def gdpr_export_data(
    _: TokenData = Depends(get_current_user),
) -> DataExportResponse:
    """Export all user data in JSON (GDPR Art. 20 — data portability)."""
    assessments = list_assessments()
    return DataExportResponse(
        status="ok",
        assessments=assessments,
        total_records=len(assessments),
    )
