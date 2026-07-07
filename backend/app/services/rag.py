"""
Lightweight RAG pipeline: keyword search + LangChain + Groq/Claude/GPT-4o.

No heavy embedding models — works within Render free tier (512MB RAM).

LLM priority order:
  1. Groq  (GROQ_API_KEY)       → Llama 3.3 70B  — free, fast, open-source
  2. Claude (ANTHROPIC_API_KEY) → Claude Sonnet   — fallback
  3. OpenAI (OPENAI_API_KEY)    → GPT-4o          — last resort

Workflow:
  1. On startup, load EU AI Act .txt files into memory (~27KB total)
  2. For each assessment: keyword-match relevant articles → inject into prompt
  3. LLM returns structured JSON → parse → ComplianceCheck list
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_xai import ChatXAI

from app.core.config import settings
from app.models.assessment import ComplianceCheck, RiskTier
from app.prompts.classification import COMPLIANCE_ANALYSIS_PROMPT

logger = logging.getLogger(__name__)


from pydantic import BaseModel
class ComplianceCheckList(BaseModel):
    checks: List[ComplianceCheck]

class RAGPipeline:
    """
    Lightweight in-memory pipeline.
    Loads EU AI Act articles as plain text; uses keyword scoring for retrieval.
    No ONNX / ChromaDB / sentence-transformers — safe for 512MB free tier.
    """

    def __init__(self) -> None:
        self._articles: List[Tuple[str, str]] = []   # (filename, content)
        self._llm = self._build_llm()

    # ── LLM factory ───────────────────────────────────────────────────────────

    def _build_llm(self) -> Any:
        """
        Provider factory. Explicit selection via LLM_PROVIDER env var
        ("groq" | "xai" | "anthropic" | "openai") makes provider choice a
        configuration decision, not a code change.

        If LLM_PROVIDER is unset, falls back to legacy auto-detect order
        (Groq -> Anthropic -> OpenAI) for backward compatibility with
        existing deployments that never set the new var.
        """
        provider = (settings.LLM_PROVIDER or "").strip().lower()

        builders = {
            "groq": self._build_groq,
            "xai": self._build_xai,
            "anthropic": self._build_anthropic,
            "openai": self._build_openai,
        }

        if provider:
            if provider not in builders:
                raise RuntimeError(
                    f"Unknown LLM_PROVIDER '{provider}' — expected one of "
                    f"{sorted(builders)}"
                )
            llm = builders[provider]()
            if llm is None:
                raise RuntimeError(
                    f"LLM_PROVIDER='{provider}' selected but its API key is not "
                    "configured (check env / /root/.secrets/eu-ai-act.env)."
                )
            return llm

        # Legacy auto-detect (unchanged default behaviour)
        for name in ("groq", "anthropic", "openai"):
            llm = builders[name]()
            if llm is not None:
                return llm

        raise RuntimeError(
            "No LLM API key configured — set LLM_PROVIDER + the matching key "
            "(GROQ_API_KEY, XAI_API_KEY, ANTHROPIC_API_KEY, or OPENAI_API_KEY)."
        )

    def _build_groq(self) -> Any:
        if not settings.GROQ_API_KEY:
            return None
        logger.info("Using Groq: %s", settings.GROQ_LLM_MODEL)
        return ChatGroq(
            model=settings.GROQ_LLM_MODEL,
            api_key=settings.GROQ_API_KEY,
            temperature=0,
            max_tokens=4096,
        )

    def _build_xai(self) -> Any:
        if not settings.XAI_API_KEY:
            return None
        logger.info("Using xAI: %s", settings.XAI_LLM_MODEL)
        return ChatXAI(
            model=settings.XAI_LLM_MODEL,
            api_key=settings.XAI_API_KEY,
            temperature=0,
            max_tokens=4096,
        )

    def _build_anthropic(self) -> Any:
        if not settings.ANTHROPIC_API_KEY:
            return None
        logger.info("Using Anthropic Claude: %s", settings.LLM_MODEL)
        return ChatAnthropic(
            model=settings.LLM_MODEL,
            api_key=settings.ANTHROPIC_API_KEY,
            max_tokens=4096,
            temperature=0,
        )

    def _build_openai(self) -> Any:
        if not settings.OPENAI_API_KEY:
            return None
        logger.info("Using OpenAI fallback: %s", settings.LLM_FALLBACK)
        return ChatOpenAI(
            model=settings.LLM_FALLBACK,
            api_key=settings.OPENAI_API_KEY,
            temperature=0,
        )

    # ── Knowledge base loading ────────────────────────────────────────────────

    def load_knowledge_base(self) -> None:
        """Load all EU AI Act .txt files into memory. Called once on startup."""
        kb_dir = Path(settings.KNOWLEDGE_BASE_DIR)
        if not kb_dir.exists():
            logger.warning("Knowledge base directory not found: %s", kb_dir)
            return

        self._articles = []
        for path in sorted(kb_dir.glob("**/*.txt")):
            try:
                content = path.read_text(encoding="utf-8")
                self._articles.append((path.name, content))
            except Exception as exc:
                logger.warning("Failed to load %s: %s", path, exc)

        total_kb = sum(len(c) for _, c in self._articles) // 1024
        logger.info(
            "Loaded %d EU AI Act articles (~%d KB) into memory",
            len(self._articles), total_kb,
        )

    # ── Retrieval (keyword scoring) ───────────────────────────────────────────

    def retrieve_relevant_articles(self, query: str, k: int = 6) -> str:
        """
        Score articles by keyword overlap with the query.
        Returns the top-k articles as a single concatenated string.
        """
        if not self._articles:
            return "No EU AI Act articles loaded. Apply general compliance principles."

        query_tokens = set(query.lower().split())

        scored: List[Tuple[float, str, str]] = []
        for name, content in self._articles:
            content_lower = content.lower()
            score = sum(1 for tok in query_tokens if tok in content_lower)
            scored.append((score, name, content))

        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:k]

        parts = []
        for _, name, content in top:
            parts.append(f"=== {name} ===\n{content}")

        return "\n\n".join(parts)

    # ── Analysis ──────────────────────────────────────────────────────────────

    async def generate_compliance_analysis(
        self,
        answers: Dict[str, Any],
        risk_tier: RiskTier,
    ) -> List[ComplianceCheck]:
        """Run the full compliance analysis chain."""
        query = " ".join([
            answers.get("sector", ""),
            answers.get("system_description", ""),
            risk_tier.value,
        ])

        retrieved_text = self.retrieve_relevant_articles(query)

        structured_llm = self._llm.with_structured_output(ComplianceCheckList)
        chain = COMPLIANCE_ANALYSIS_PROMPT | structured_llm
        
        try:
            response = await chain.ainvoke({
                "risk_tier": risk_tier.value,
                "retrieved_articles": retrieved_text,
                "answers": json.dumps(answers, indent=2),
            })
            if hasattr(response, 'checks'):
                return response.checks
            return []
        except Exception as exc:
            logger.error("Structured LLM output failed: %s", exc)
            raise ValueError(f"Failed to generate structured compliance checks: {exc}") from exc


# Singleton — instantiated once on app startup via lifespan
rag_pipeline = RAGPipeline()
