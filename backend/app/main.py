from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router
from app.core.config import settings
from app.services.rag import rag_pipeline

logger = logging.getLogger(__name__)


def get_allowed_origins() -> list[str]:
    """Build allowed origins list. Use FRONTEND_URL if set, else ["*"] only in DEBUG."""
    if settings.FRONTEND_URL:
        return [settings.FRONTEND_URL]
    if settings.DEBUG:
        return ["*"]
    if settings.ALLOWED_ORIGINS == ["*"]:
        logger.warning(
            "ALLOWED_ORIGINS is still ['*'] in production! "
            "Set FRONTEND_URL or ALLOWED_ORIGINS explicitly."
        )
    return settings.ALLOWED_ORIGINS


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the RAG knowledge base on startup."""
    rag_pipeline.load_knowledge_base()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# CORS — production-safe configuration
allowed_origins = get_allowed_origins()
allow_credentials = "*" not in allowed_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(router)


@app.get("/", tags=["health"])
async def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }
