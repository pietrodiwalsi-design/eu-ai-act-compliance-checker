from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    APP_NAME:    str = "EU AI Act Compliance Checker"
    APP_VERSION: str = "0.1.0"
    DEBUG:       bool = False

    # LLM — priority: Groq (free/OSS) → Anthropic → OpenAI
    GROQ_API_KEY:      str = ""                        # free at console.groq.com
    GROQ_LLM_MODEL:    str = "llama-3.3-70b-versatile" # best free Groq model
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY:    str = ""
    LLM_MODEL:         str = "claude-sonnet-4-5"        # Anthropic fallback
    LLM_FALLBACK:      str = "gpt-4o"                  # OpenAI last resort

    # Vector store (Chroma)
    CHROMA_PERSIST_DIR:     str = "./data/chroma_db"
    KNOWLEDGE_BASE_DIR:     str = "./data/knowledge_base"
    COLLECTION_NAME:        str = "eu_ai_act"

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


settings = Settings()
