from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.api.v1 import assess
from app.api.deps import create_access_token
from app.core.config import settings

router = APIRouter(prefix="/api/v1")
router.include_router(assess.router, tags=["assessments"])


class TokenRequest(BaseModel):
    api_key: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/auth/token", response_model=TokenResponse, tags=["auth"])
async def get_token(request: TokenRequest) -> TokenResponse:
    """Exchange a valid API key for a JWT access token."""
    if not settings.API_KEY or request.api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    token = create_access_token(data={"sub": request.api_key})
    return TokenResponse(access_token=token)
