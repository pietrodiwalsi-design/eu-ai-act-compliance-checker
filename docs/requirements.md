# Functional & Non-Functional Requirements
## EU AI Act Compliance Checker — MVP

> Source: Requirements document provided 2026-06-01

---

## Functional Requirements

These define the specific features and checks the Next.js dashboard and LLM backend must perform to assess AI systems against the EU AI Act.

### FR-01 — Web-Based AI Intake
The system must allow users to input their AI use-case via a **15-question interactive web wizard** or by directly pasting technical documentation (e.g., a model card).

### FR-02 — Automated Risk Classification
The system must automatically classify the inputted AI system into one of the **four EU AI Act risk tiers**:
- Prohibited
- High-Risk
- Limited Risk (Transparency)
- Minimal Risk

### FR-03 — Prohibited Practice Filtering (Article 5)
The system must instantly flag applications that pose an "unacceptable risk," such as:
- Social scoring
- Behavioral manipulation
- Real-time remote biometric identification in public spaces for law enforcement

### FR-04 — Filter Provision Evaluation
For systems in typically high-risk sectors, the system must apply the legal "filter provision" to assess whether the AI actually poses a significant risk of harm to health, safety, or fundamental rights — successfully down-grading systems that perform narrow procedural tasks.

### FR-05 — Transparency Check (Articles 13 & 50)
The system must verify that limited and high-risk AI applications (chatbots, deepfakes) notify users they are interacting with AI, and that sufficient technical documentation is generated for downstream users.

### FR-06 — Human Oversight Mechanisms (Article 14)
The system must prompt the user to confirm the existence of appropriate human-in-the-loop oversight measures to prevent automation bias and protect fundamental rights.

### FR-07 — Data Governance & Quality (Article 10)
The system must evaluate training data protocols to ensure data is:
- Relevant and representative
- Free of errors
- Legally compliant (GDPR)
- Checked for statistical biases

### FR-08 — Robustness, Accuracy & Cybersecurity (Article 15)
The system must prompt users on their system's resilience against errors, faults, or adversarial manipulation (cybersecurity threats), ensuring high-risk models meet safety obligations.

### FR-09 — Record-Keeping & Logging (Article 12)
The system must check that the AI system features automated logging of events to ensure traceability and allow for post-market monitoring of serious incidents.

### FR-10 — General-Purpose AI (GPAI) Triage
The system must identify if the model qualifies as a GPAI (e.g., GPT-4 class foundation models). If so, it must check:
- Copyright policy compliance
- Training data summaries
- Whether the model exceeds the **10²⁵ FLOPs** threshold triggering systemic risk obligations

### FR-11 — "What-If" Context Simulator
The system must include a module allowing users to test how deploying their AI in different scenarios (e.g., shifting from general enterprise search → hiring → credit scoring → law enforcement) alters their risk classification and legal obligations.

### FR-12 — Traffic-Light Compliance Scoring
The system must output a **quantitative compliance score (0–100)** alongside a visual **red / yellow / green** indicator for each key requirement, to easily highlight critical vulnerabilities.

### FR-13 — Article-Level Traceability
Utilizing RAG over the official Act text and EDPB guidelines, the system must map every identified compliance gap directly to its corresponding **EU AI Act Article**.

### FR-14 — Actionable Remediation Engine
The system must generate specific, structured recommendations detailing exactly what the compliance team must do (e.g., "Draft a Fundamental Rights Impact Assessment") to turn a "red" or "yellow" gap into a "green" pass.

---

## Non-Functional Requirements

These define the architectural, performance, security, and usability attributes required to make this SaaS product successful and legally reliable.

### NFR-01 — Processing Speed (Time-to-First-Report)
The backend (utilizing LangChain/LlamaIndex and Claude/GPT-4o) must process the user intake and generate the complete compliance report in **under 3 minutes**.

### NFR-02 — Classification Accuracy & Reliability
The system's automated risk categorization and gap analysis must maintain a **high accuracy rate** when benchmarked against a baseline established by human legal experts, minimizing false positives and false negatives.

### NFR-03 — Data Privacy and Confidentiality
Because users will upload sensitive model cards and proprietary use-cases, the system must:
- Employ strict **data segregation**
- Ensure that user inputs are **not used to train** the underlying LLM
- Comply with **GDPR**

### NFR-04 — Multi-Tenant SaaS Architecture
The system must support a scalable, secure multi-tenant architecture to accommodate:
- Per-assessment billing
- Annual subscriptions for distinct corporate compliance teams
- Legal reseller support

### NFR-05 — Regulatory Adaptability (Evolvability)
The RAG knowledge base must be designed for **continuous updates**. As the EU AI Act phases in over the next 6–36 months, the system must easily ingest new:
- Delegated acts
- Codes of practice
- Harmonized standards produced by CEN-CENELEC

### NFR-06 — Auditability of LLM Outputs
The system must mitigate LLM "hallucinations" by strictly anchoring its structured outputs to the retrieved legal texts, allowing users to trace the AI's legal rationale back to the **exact passage** in the EU AI Act or EDPB guidelines.
