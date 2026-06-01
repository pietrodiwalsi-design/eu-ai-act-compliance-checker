# EU AI Act Compliance Checker

> **Private Repository** — MVP development for an automated EU AI Act compliance assessment tool.

## What This Is

A SaaS web application that helps organizations assess their AI systems against the EU AI Act. Users input their use-case via a 15-question wizard or model card upload, and receive a structured compliance report with risk classification, gap analysis, and actionable remediation steps — all in under 3 minutes.

## Repository Structure

```
/
├── README.md                    # This file
├── docs/
│   ├── requirements.md          # Functional & Non-Functional Requirements
│   ├── development-plan.md      # Full development plan (phased roadmap)
│   └── architecture.md          # System architecture (TBD)
├── frontend/                    # Next.js 14+ dashboard (TBD)
└── backend/                     # LangChain/LlamaIndex API (TBD)
```

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14+, TypeScript, Tailwind CSS |
| Backend | Python, FastAPI, LangChain / LlamaIndex |
| LLM | Claude 3.5 Sonnet / GPT-4o |
| RAG | Pinecone / Chroma + EU AI Act official text |
| Auth & Multi-tenant | Clerk / Auth0 + Stripe |
| Deployment | Vercel (frontend) + Fly.io / Render (backend) |

## Links

- Live URL: TBD (post Phase 5 deployment)
- Requirements: [docs/requirements.md](docs/requirements.md)
- Development Plan: [docs/development-plan.md](docs/development-plan.md)
