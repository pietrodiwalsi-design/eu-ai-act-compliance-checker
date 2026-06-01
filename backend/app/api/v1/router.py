from fastapi import APIRouter
from app.api.v1 import assess

router = APIRouter(prefix="/api/v1")
router.include_router(assess.router, tags=["assessments"])
