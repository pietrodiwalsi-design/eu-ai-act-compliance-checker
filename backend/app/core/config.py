from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Anchor to the `backend/` directory (parent of `app/`), not the process's
# current working directory. Without this, `.env` (and, separately,
# KNOWLEDGE_BASE_DIR / CHROMA_PERSIST_DIR below) silently fail to resolve
# whenever the app or test suite is launched from the repo root or anywhere
# else that isn't exactly `backend/` (e.g. `pytest tests/golden/` from the
# repo root, or a CI runner) — confirmed via QA review 2026-07-07.
BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    APP_NAME:    str = "EU AI Act Compliance Checker"
    APP_VERSION: str = "0.1.0"
    DEBUG:       bool = False

    # LLM provider selection — explicit, no silent fallback chain.
    # One of: "groq" | "xai" | "anthropic" | "openai"
    # If unset, falls back to legacy auto-detect (Groq -> Anthropic -> OpenAI)
    # for backward compatibility with existing deployments.
    LLM_PROVIDER: str = ""

    # Groq (free/OSS)
    GROQ_API_KEY:      str = ""                        # free at console.groq.com
    GROQ_LLM_MODEL:    str = "llama-3.3-70b-versatile" # best free Groq model

    # xAI (Grok)
    XAI_API_KEY:       str = ""                        # loaded from /root/.secrets/eu-ai-act.env, never from repo .env
    XAI_LLM_MODEL:      str = "grok-4-fast"

    # Anthropic (fallback)
    ANTHROPIC_API_KEY: str = ""
    LLM_MODEL:         str = "claude-sonnet-4-5"        # Anthropic fallback

    # OpenAI (last resort)
    OPENAI_API_KEY:    str = ""
    LLM_FALLBACK:      str = "gpt-4o"                  # OpenAI last resort

    # Vector store (Chroma)
    CHROMA_PERSIST_DIR:     str = "./data/chroma_db"
    KNOWLEDGE_BASE_DIR:     str = "./data/knowledge_base"
    COLLECTION_NAME:        str = "eu_ai_act"

    @property
    def knowledge_base_path(self) -> Path:
        """KNOWLEDGE_BASE_DIR resolved relative to backend/, not the CWD.

        Absolute values (e.g. an operator override in production) pass
        through unchanged; only relative values (the "./..." default) get
        anchored, so this stays backward compatible with any deployment
        that already sets an absolute path explicitly.
        """
        p = Path(self.KNOWLEDGE_BASE_DIR)
        return p if p.is_absolute() else (BACKEND_DIR / p)

    @property
    def chroma_persist_path(self) -> Path:
        """CHROMA_PERSIST_DIR resolved relative to backend/, not the CWD."""
        p = Path(self.CHROMA_PERSIST_DIR)
        return p if p.is_absolute() else (BACKEND_DIR / p)

    # Auth
    JWT_SECRET_KEY:    str = "change-me-in-production"
    JWT_ALGORITHM:     str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24h

    # CORS — tightened for production
    ALLOWED_ORIGINS: list[str] = []

    # Auth
    API_KEY: str = ""  # Required for /auth/token endpoint

    # Frontend
    FRONTEND_URL: str = ""  # Production frontend URL for CORS

    # Performance
    MAX_REPORT_TIMEOUT_SECONDS: int = 180  # 3 min SLA

    # Rate limiting (NFR-04)
    RATE_LIMIT_MAX_REQUESTS: int = 10   # max requests per window
    RATE_LIMIT_WINDOW_SECONDS: int = 60 # sliding window size


settings = Settings()
