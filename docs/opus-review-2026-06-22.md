# EU AI Act Compliance Checker — Senior Code Review (2026-06-22)

**Reviewer:** Opus (subagent)  
**Scope:** Full backend + key frontend + deployment configs  
**Target:** Render.com + proposed Hetzner VPS split

---

## 1. Code Quality Issues

### Critical
- **backend/app/services/rag.py:140** — `json.loads(raw)` with zero error handling. Any LLM deviation (extra text, truncated JSON, markdown) crashes the entire `/assess` endpoint with 500.
- **backend/app/services/rag.py:128-135** — Brittle markdown fence stripping. Fails on ` ```json\n{...}\n``` ` variations or when LLM returns plain text.
- **backend/app/api/v1/assess.py:98-112** — `what_if_analysis` has hardcoded `claude-3-5-sonnet-20241022` and naive string matching for tier detection. No fallback, no structured output.
- **backend/app/services/rag.py:52** — `_build_llm()` runs at import time via singleton `rag_pipeline = RAGPipeline()`. Crashes entire app if no API keys present.

### High
- **backend/app/core/config.py:27** — `JWT_SECRET_KEY = "change-me-in-production"` — default is a landmine.
- **backend/app/main.py:25** — CORS allows `["*"]` + `allow_credentials=True` (invalid per spec; browsers reject it).
- Missing: No request validation limits, no rate limiting, no structured logging.

---

## 2. Architecture Improvements

- **RAG pipeline** (`rag.py`) mixes embedding adapter, vector store init, LLM factory, and analysis in one class. Split into `LLMFactory`, `VectorStoreManager`, and `ComplianceAnalyzer`.
- **No dependency injection.** `rag_pipeline` is a global singleton imported everywhere. Makes testing impossible.
- **Persistence layer** (`persistence.py`) is stubbed (in-memory dicts). No real DB, no migrations, no transactions.
- **Frontend proxy** (`frontend/src/app/api/v1/[...path]/route.ts`) hardcodes `http://backend:8000` — breaks on any non-docker deployment.
- **Risk classification + deterministic checks** live in separate services but are not versioned or testable in isolation.

---

## 3. Security Gaps

- **Zero auth enforcement.** JWT settings exist in config but no `Depends(get_current_user)` on any route in `assess.py`.
- **CORS misconfiguration** (`main.py:22-27`): `["*"]` + credentials is broken. Render deployment leaves it wide open.
- **Secrets handling:** `render.yaml` relies on manual dashboard secrets + `generateValue` for JWT. No `.env.example` or validation on startup.
- **Input validation:** `AssessmentRequest.answers` is `Dict[str, object]` with no schema. Arbitrary data reaches the LLM.
- **No HTTPS enforcement**, no security headers middleware.

---

## 4. AI/RAG Pipeline Improvements

- **Embeddings** (`rag.py:70-85`): Using ChromaDB's `DefaultEmbeddingFunction` (weak all-MiniLM). Legal text needs better domain embeddings (e.g. `BAAI/bge-small-en-v1.5` or OpenAI `text-embedding-3-small`).
- **Prompt** (`prompts/classification.py`): Forces JSON but provides no Pydantic/JSON schema to the LLM. High hallucination risk on `source_citation`.
- **Retrieval strategy:** Fixed `k=8`, no metadata filtering by risk tier, no reranking, no query expansion.
- **Model config** (`rag.py:30`): `temperature=0` + `max_tokens=4096` is good, but no fallback chain on rate limits or model deprecation.
- **WHAT_IF_PROMPT** is underused and poorly parsed downstream.

---

## 5. Deployment Readiness (Render.com)

### render.yaml problems
- **Next.js standalone** (`startCommand: node .next/standalone/server.js`) requires `output: "standalone"` in `next.config.js` — not verified.
- **Chroma on free tier:** `CHROMA_PERSIST_DIR=./data/chroma_db` will be ephemeral. Free Render disks are tiny and get wiped on deploy.
- **Knowledge base:** `KNOWLEDGE_BASE_DIR` must be populated at build time or via Git LFS — no mechanism shown.
- **Two services** share no common network; frontend proxy must use the public `BACKEND_URL`.
- Missing: health checks, auto-scaling config, proper `uvicorn` worker count.

### docker-compose.yml
- References `Dockerfile.local` that do not exist in the repo.
- Volumes and healthchecks are good, but no `.dockerignore`, no multi-stage builds.

---

## 6. Hetzner VPS + Tailscale Funnel + Render Split Recommendation

**Verdict: Viable but requires non-trivial changes.**

### What works well
- Backend on Hetzner (stateful Chroma + knowledge base) makes sense.
- Tailscale Funnel + JWT gives strong auth + private exposure.
- Frontend on Render is cheap and fine for static + serverless proxy.

### Required changes
1. **Backend (Hetzner)**
   - Add real JWT middleware (`app/api/deps.py`) and protect all `/api/v1/*` routes except health.
   - Set `ALLOWED_ORIGINS` to the exact Render frontend URL only.
   - Run Chroma with persistent volume (not ephemeral `./data`).
   - Add proper structured logging + Sentry.
   - Expose only via Tailscale Funnel (`tailscale funnel 8000`).

2. **Frontend (Render)**
   - Set `BACKEND_URL` to the Tailscale Funnel HTTPS URL.
   - Add `Authorization: Bearer <token>` header in the proxy route (currently missing).
   - Implement login flow or magic-link to obtain JWT.

3. **Auth flow**
   - Move from "JWT settings exist" to "JWT required on every assessment".
   - Add refresh token + short-lived access tokens.

4. **Data**
   - Seed knowledge base via Git + volume mount or S3 + init container.
   - Never rely on Render's ephemeral disk for Chroma.

**Bottom line:** The split is architecturally sound **only if** auth is actually enforced and CORS is locked down. Without those two changes it is less secure than the current all-Render setup.

---

## Summary of Top 5 Issues (ranked)

1. No authentication middleware despite JWT config — every `/assess` call is unauthenticated.
2. `json.loads()` crash on LLM output in `rag.py:140` — single point of total failure.
3. Chroma using default weak embeddings + ephemeral disk on Render.
4. `ALLOWED_ORIGINS=["*"]` + credentials in production config.
5. render.yaml + docker-compose reference missing Dockerfiles and will fail on first deploy.