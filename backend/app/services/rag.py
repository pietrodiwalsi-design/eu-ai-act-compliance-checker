"""
RAG pipeline: Chroma vector store + LangChain + Groq/Claude/GPT-4o.

LLM priority order:
  1. Groq  (GROQ_API_KEY)    → Llama 3.3 70B  — free, fast, open-source
  2. Claude (ANTHROPIC_API_KEY) → Claude Sonnet   — fallback
  3. OpenAI (OPENAI_API_KEY)   → GPT-4o          — last resort

Workflow:
  1. On startup, load EU AI Act text chunks from data/knowledge_base/
  2. For each assessment: retrieve relevant articles → pass to LLM with prompt
  3. Parse structured JSON output → ComplianceCheck list
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from langchain_anthropic import ChatAnthropic
from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_core.documents import Document
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings
from app.models.assessment import ComplianceCheck, RiskTier
from app.prompts.classification import COMPLIANCE_ANALYSIS_PROMPT

logger = logging.getLogger(__name__)


class RAGPipeline:
    """Manages the vector store and LLM chain for compliance analysis."""

    def __init__(self) -> None:
        self._vectorstore: Chroma | None = None
        self._llm = self._build_llm()

    # ── LLM factory ───────────────────────────────────────────────────────────

    def _build_llm(self) -> Any:
        # 1️⃣  Groq — free, open-source Llama 3.3 70B (preferred)
        if settings.GROQ_API_KEY:
            logger.info("Using Groq: %s", settings.GROQ_LLM_MODEL)
            return ChatGroq(
                model=settings.GROQ_LLM_MODEL,
                api_key=settings.GROQ_API_KEY,
                temperature=0,
                max_tokens=4096,
            )
        # 2️⃣  Anthropic Claude — fallback
        if settings.ANTHROPIC_API_KEY:
            logger.info("Using Anthropic Claude: %s", settings.LLM_MODEL)
            return ChatAnthropic(
                model=settings.LLM_MODEL,
                api_key=settings.ANTHROPIC_API_KEY,
                max_tokens=4096,
                temperature=0,
            )
        # 3️⃣  OpenAI — last resort
        if settings.OPENAI_API_KEY:
            logger.info("Using OpenAI fallback: %s", settings.LLM_FALLBACK)
            return ChatOpenAI(
                model=settings.LLM_FALLBACK,
                api_key=settings.OPENAI_API_KEY,
                temperature=0,
            )
        raise RuntimeError(
            "No LLM API key configured — set GROQ_API_KEY (free), "
            "ANTHROPIC_API_KEY, or OPENAI_API_KEY in .env"
        )

    # ── Vector store ──────────────────────────────────────────────────────────

    def _get_embeddings(self):
        # Lightweight LangChain-compatible wrapper around ChromaDB's built-in
        # onnxruntime embeddings — no PyTorch / CUDA required
        from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
        from langchain_core.embeddings import Embeddings

        chroma_fn = DefaultEmbeddingFunction()

        class _ChromaEmbeddingsAdapter(Embeddings):
            def embed_documents(self, texts: list) -> list:
                return chroma_fn(texts)

            def embed_query(self, text: str) -> list:
                return chroma_fn([text])[0]

        return _ChromaEmbeddingsAdapter()

    def load_knowledge_base(self) -> None:
        """Load EU AI Act text chunks into Chroma. Call once on app startup."""
        persist_dir = Path(settings.CHROMA_PERSIST_DIR)
        kb_dir = Path(settings.KNOWLEDGE_BASE_DIR)

        # If Chroma already persisted, reuse it
        if persist_dir.exists() and any(persist_dir.iterdir()):
            logger.info("Loading existing Chroma index from %s", persist_dir)
            self._vectorstore = Chroma(
                collection_name=settings.COLLECTION_NAME,
                embedding_function=self._get_embeddings(),
                persist_directory=str(persist_dir),
            )
            return

        # Otherwise, build from source files
        if not kb_dir.exists() or not any(kb_dir.iterdir()):
            logger.warning(
                "Knowledge base directory %s is empty. "
                "Add EU AI Act text chunks (.txt files) to populate the RAG index.",
                kb_dir,
            )
            self._vectorstore = Chroma(
                collection_name=settings.COLLECTION_NAME,
                embedding_function=self._get_embeddings(),
                persist_directory=str(persist_dir),
            )
            return

        logger.info("Building Chroma index from %s", kb_dir)
        loader = DirectoryLoader(str(kb_dir), glob="**/*.txt", loader_cls=TextLoader)
        docs: List[Document] = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_documents(docs)

        self._vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self._get_embeddings(),
            collection_name=settings.COLLECTION_NAME,
            persist_directory=str(persist_dir),
        )
        logger.info("Indexed %d chunks into Chroma", len(chunks))

    # ── Retrieval ─────────────────────────────────────────────────────────────

    def retrieve_relevant_articles(self, query: str, k: int = 8) -> List[Document]:
        """Retrieve the k most relevant EU AI Act passages for a given query."""
        if self._vectorstore is None:
            logger.warning("Vector store not initialised — returning empty articles")
            return []
        return self._vectorstore.similarity_search(query, k=k)

    # ── Analysis ──────────────────────────────────────────────────────────────

    async def generate_compliance_analysis(
        self,
        answers: Dict[str, Any],
        risk_tier: RiskTier,
    ) -> List[ComplianceCheck]:
        """
        Run the full compliance analysis chain.

        Returns a list of ComplianceCheck objects.
        """
        # Build retrieval query from key wizard answers
        query_parts = [
            f"sector: {answers.get('sector', '')}",
            f"description: {answers.get('system_description', '')}",
            f"risk_tier: {risk_tier.value}",
        ]
        query = " ".join(query_parts)

        retrieved_docs = self.retrieve_relevant_articles(query)
        retrieved_text = "\n\n---\n\n".join(d.page_content for d in retrieved_docs) or (
            "No specific articles retrieved. Apply general EU AI Act principles."
        )

        # Build and invoke the chain
        chain = COMPLIANCE_ANALYSIS_PROMPT | self._llm

        response = await chain.ainvoke({
            "risk_tier": risk_tier.value,
            "retrieved_articles": retrieved_text,
            "answers": json.dumps(answers, indent=2),
        })

        # Parse JSON output
        raw = response.content if hasattr(response, "content") else str(response)

        # Strip markdown code fences if present
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        checks_data: List[dict] = json.loads(raw)
        return [ComplianceCheck(**c) for c in checks_data]


# Singleton — instantiated once on app startup via lifespan
rag_pipeline = RAGPipeline()
