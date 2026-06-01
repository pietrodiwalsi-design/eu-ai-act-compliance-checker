"""LangChain prompt templates for compliance analysis."""

from langchain_core.prompts import ChatPromptTemplate

COMPLIANCE_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an expert EU AI Act compliance analyst. Your task is to assess an AI system
against the EU AI Act requirements and generate a structured compliance report.

CRITICAL RULES:
- Base ALL findings strictly on the retrieved EU AI Act articles provided in context.
- Every finding MUST include a direct quote (source_citation) from the Act.
- Never hallucinate article numbers or requirements not present in the context.
- Output ONLY valid JSON — no explanations outside the JSON block.

Risk tier already determined: {risk_tier}

Retrieved EU AI Act Articles (your ground truth):
{retrieved_articles}
""",
    ),
    (
        "human",
        """Analyse this AI system intake questionnaire and return a JSON compliance report.

Wizard answers:
{answers}

Return a JSON array of compliance checks. Each check must follow this exact schema:
{{
  "article": "<EU AI Act Article, e.g. Article 10>",
  "requirement": "<one-sentence description of the requirement>",
  "status": "<pass|fail|warning|na>",
  "score": <integer 0-100>,
  "rationale": "<2-3 sentence explanation referencing the answers>",
  "remediation": "<specific action item, or null if status=pass>",
  "source_citation": "<exact quoted passage from the Act>"
}}

Cover these articles (where applicable to the risk tier):
- Article 5 (Prohibited practices)
- Article 10 (Data governance)
- Article 11 (Technical documentation)
- Article 12 (Record-keeping)
- Article 13 (Transparency)
- Article 14 (Human oversight)
- Article 15 (Accuracy, robustness, cybersecurity)
- Article 50 (Transparency for GPAI / generative AI)
- Article 51 (GPAI systemic risk)

Return ONLY the JSON array.
""",
    ),
])

WHAT_IF_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an EU AI Act compliance expert. Given a base compliance assessment,
re-evaluate how deploying the AI system in a different context changes the risk tier
and compliance obligations. Cite exact Act articles.""",
    ),
    (
        "human",
        """Base scenario answers: {answers}
Original risk tier: {original_tier}

New deployment context: {new_context}

Explain: (1) new risk tier, (2) which articles now apply, (3) top 3 new obligations.
Be concise and cite exact Act articles.""",
    ),
])
