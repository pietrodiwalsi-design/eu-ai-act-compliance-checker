# Development Plan
## EU AI Act Compliance Checker — MVP

> Version: 1.0 | Created: 2026-06-01 | Status: Planning

---

## Executive Summary

This plan covers the MVP build of an automated EU AI Act compliance assessment SaaS. The system takes an AI use-case as input and returns a structured report with risk tier classification, per-article gap analysis, a traffic-light compliance score, and actionable remediation steps — all in under 3 minutes.

Total timeline: **10 weeks** across 5 phases.

---

## Tech Stack

| Layer | Choice | Rationale |
|---|---|---|
| Frontend | Next.js 14 + TypeScript + Tailwind | Fast UI, SSR, type safety |
| Backend | Python + FastAPI | LangChain/LlamaIndex ecosystem |
| LLM | Claude 3.5 Sonnet (primary) / GPT-4o (fallback) | Quality + cost balance |
| RAG Store | Pinecone or Chroma | Semantic retrieval over EU AI Act text |
| Auth | Clerk or Auth0 | Multi-tenant OOTB |
| Billing | Stripe | Per-assessment + subscription |
| Deployment | Vercel (FE) + Fly.io or Render (BE) | Low-ops, scalable |
| Monitoring | LangSmith / Langfuse | LLM observability + audit trail |

---

## Phase 1 — Foundation & Infrastructure (Weeks 1–2)

**Goal:** Working skeleton with intake wizard and RAG pipeline.

### Backend
- [ ] Initialize FastAPI project with Docker
- [ ] Ingest official EU AI Act text + EDPB guidelines into vector store (Pinecone/Chroma)
- [ ] Set up LangChain/LlamaIndex RAG pipeline
- [ ] Basic API endpoint: POST /assess → returns raw classification
- [ ] LLM hallucination guardrails: strict source anchoring (NFR-06)
- [ ] Configure LangSmith for observability

### Frontend
- [ ] Initialize Next.js 14 + TypeScript + Tailwind
- [ ] 15-question intake wizard (FR-01)
- [ ] Model card / technical doc upload (FR-01)
- [ ] Basic auth with Clerk / Auth0 (NFR-04)
- [ ] Stub dashboard page

### Infrastructure
- [ ] GitHub Actions CI pipeline
- [ ] .env structure + secret management
- [ ] Multi-tenant data segregation setup (NFR-03, NFR-04)

**Deliverable:** Wizard collects input, sends to API, receives and displays raw classification.

---

## Phase 2 — Core Compliance Engine (Weeks 3–4)

**Goal:** All 14 functional requirements implemented as working checks.

### Risk Classification
- [ ] FR-02: Automated 4-tier risk classification (Prohibited / High / Limited / Minimal)
- [ ] FR-03: Prohibited Practice filter — Article 5 instant flagging
- [ ] FR-04: Filter Provision evaluation — sector-based downgrade logic

### Article Checks
- [ ] FR-05: Transparency check (Articles 13 & 50)
- [ ] FR-06: Human oversight verification (Article 14)
- [ ] FR-07: Data governance & quality assessment (Article 10)
- [ ] FR-08: Robustness, accuracy & cybersecurity (Article 15)
- [ ] FR-09: Record-keeping & logging check (Article 12)
- [ ] FR-10: GPAI triage + 10²⁵ FLOPs threshold detection

### Reporting
- [ ] FR-12: Traffic-light scoring engine (0–100 score + red/yellow/green per requirement)
- [ ] FR-13: Article-level traceability — RAG citation mapping to exact EU AI Act Articles
- [ ] FR-14: Remediation Engine — structured action items per gap

### Performance
- [ ] NFR-01: Optimize pipeline to meet < 3 minute report generation target

**Deliverable:** End-to-end report generation with all article checks, scoring, traceability, and remediation steps.

---

## Phase 3 — Advanced Features (Weeks 5–6)

**Goal:** "What-If" simulator, polished report, export functionality.

### Features
- [ ] FR-11: "What-If" Context Simulator — dynamic scenario re-assessment
- [ ] PDF/JSON report export
- [ ] Comparison view (baseline vs. "what-if" scenario)
- [ ] "How to Use" onboarding guide / help tab
- [ ] Risk heat map visualization (per-article severity grid)

### UX
- [ ] Dashboard with assessment history
- [ ] Per-assessment drill-down view
- [ ] Mobile-responsive layouts

**Deliverable:** Full feature-complete MVP dashboard with scenario testing and export.

---

## Phase 4 — Non-Functional Requirements & Hardening (Weeks 7–8)

**Goal:** Production-grade security, accuracy, scalability.

### Security & Privacy (NFR-03)
- [ ] Verify user data is fully isolated (no cross-tenant leakage)
- [ ] Confirm LLM provider contract: no training on user inputs
- [ ] GDPR-compliant data retention and deletion flows

### Accuracy (NFR-02)
- [ ] Build legal expert benchmark dataset (10+ test cases)
- [ ] Run automated accuracy evaluation vs. baseline
- [ ] Tune prompts / RAG retrieval based on results
- [ ] Document accuracy metrics

### Scalability (NFR-04)
- [ ] Load testing with concurrent multi-tenant assessments
- [ ] Optimize vector store queries
- [ ] Caching layer for repeated article retrievals

### Regulatory Adaptability (NFR-05)
- [ ] Build knowledge-base update pipeline (ingest new delegated acts, CEN-CENELEC standards)
- [ ] Version-controlled knowledge base snapshots
- [ ] Admin interface for triggering KB updates

### Auditability (NFR-06)
- [ ] Full LLM output audit trail in LangSmith / Langfuse
- [ ] Source-citation enforcement in all generated outputs
- [ ] User-facing "explain this rating" with direct Article quotes

**Deliverable:** Production-hardened system with accuracy benchmarks, security audit, and regulatory update pipeline.

---

## Phase 5 — Testing, Documentation & Deployment (Weeks 9–10)

**Goal:** Launch-ready product.

### Testing
- [ ] End-to-end test suite (Playwright for FE, pytest for BE)
- [ ] Regression tests for all 14 functional requirements
- [ ] Performance test: 50 concurrent assessments < 3 min each
- [ ] Security penetration test (OWASP Top 10)

### Documentation
- [ ] API documentation (OpenAPI/Swagger)
- [ ] User guide ("How to Use" tab)
- [ ] Admin / operations runbook
- [ ] Architecture decision records (ADRs)

### Deployment
- [ ] Production Vercel deployment (frontend)
- [ ] Production Fly.io / Render deployment (backend)
- [ ] Custom domain + TLS
- [ ] Monitoring & alerting (Sentry, Uptime checks)
- [ ] Stripe billing integration live

**Deliverable:** Live production URL, full documentation, monitoring in place.

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| LLM hallucinations in legal classification | High | High | Strict RAG anchoring (NFR-06), human review layer |
| EU AI Act delegated acts delayed / changed | Medium | Medium | Modular KB update pipeline (NFR-05) |
| LLM provider rate limits under load | Medium | High | Fallback to GPT-4o, caching layer |
| GDPR breach via data segregation failure | Low | Critical | Isolated tenant DB + security audit in Phase 4 |
| Legal accuracy disputes from customers | Medium | High | Disclaimer: "not legal advice", benchmark disclosure |

---

## Milestones

| Milestone | Target Week | Description |
|---|---|---|
| M1 — Skeleton Live | Week 2 | Intake → API → raw classification |
| M2 — Engine Complete | Week 4 | All 14 FRs working, report generated |
| M3 — Feature Complete | Week 6 | What-if simulator, export, full dashboard |
| M4 — Production-Ready | Week 8 | Security hardened, accuracy benchmarked |
| M5 — MVP Launch | Week 10 | Live URL, billing active, docs published |

---

## Out of Scope (Post-MVP)

- Native mobile app
- Direct EU AI Act regulatory submission workflows
- White-label / custom branding for resellers
- Real-time regulatory change alerts (newsletter/webhook)
- Integration with existing GRC platforms (ServiceNow, Archer)
