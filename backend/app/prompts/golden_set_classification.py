"""
Free-text classification prompt for the golden-set regression harness.

Why this exists separately from `classification.py`:
The production engine's public contract (`POST /assess`) takes structured
wizard `answers: dict`, not free text. The golden-set fixtures are free-text
scenario descriptions ("A municipality wants to deploy..."), matching how a
real user would describe their system before any wizard exists for it.

To measure the REAL engine (RAG pipeline + knowledge base + LLM, not a mock)
against free text, this prompt reuses the exact same knowledge-base
retrieval (`rag_pipeline.retrieve_relevant_articles`) and the exact same LLM
instance (provider-selected via LLM_PROVIDER) as production — it only swaps
the input shape (scenario text in, tier+articles+date+flags out) so the
model's full tier vocabulary can be expressed. See golden-set-v1.json for the
full label set: prohibited | high | limited | minimal | not_high_risk_art_6_3
| gpai_systemic_risk | sectoral_lead_annex_I_section_B | out_of_scope.

This intentionally does NOT force the golden-set output into the production
4-tier enum (prohibited/high_risk/limited_risk/minimal_risk) — collapsing the
richer golden-set vocabulary into 4 buckets would hide a real product gap
(the engine cannot currently express Art. 6(3) derogations, GPAI systemic
risk, or Annex I Section B as distinct tiers). That mismatch is reported as
a finding, not silently normalized away.
"""

from langchain_core.prompts import ChatPromptTemplate

GOLDEN_SET_CLASSIFICATION_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an expert EU AI Act compliance analyst. Classify the described AI
system against the EU AI Act (Regulation (EU) 2024/1689) AS AMENDED BY THE DIGITAL
OMNIBUS ON AI (political agreement 7 May 2026; final package June/July 2026).

CRITICAL — you must apply the POST-OMNIBUS legal baseline, not the original 2024 text:
- Annex III high-risk obligations apply from 2 December 2027 (was 2 Aug 2026).
- Annex I high-risk obligations apply from 2 August 2028 (was 2 Aug 2027).
- Article 50(2) watermarking: 2 December 2026 for systems already on the market
  before 2 Aug 2026; immediate for systems placed on the market after that date.
- Article 5 prohibitions now also cover non-consensual intimate imagery (NCII /
  "nudifiers") and AI-generated CSAM, effective 2 December 2026.
- The Machinery Regulation interaction moved AI Act Annex I from Section A
  (dual compliance) to Section B (sectoral law / Machinery Regulation leads),
  effective 2 August 2028.
- "Safety component" is now interpreted narrowly: it excludes pure assistance,
  optimization, convenience, or quality-control functions unless their failure
  could endanger health or safety.
- Article 6(3) registration obligations were simplified (Annex VIII Section B
  points 7 and 9 deleted) but the underlying obligation to register remains.

Base ALL findings strictly on the retrieved EU AI Act articles provided below as
ground truth. Never hallucinate article numbers. Output ONLY valid JSON.

Retrieved EU AI Act Articles (ground truth for this case):
{retrieved_articles}
""",
    ),
    (
        "human",
        """Classify this AI system scenario:

{scenario}

Return exactly one JSON object with this schema:
{{
  "risk_tier": "<one of: prohibited | high | limited | minimal | "
               "not_high_risk_art_6_3 | gpai_systemic_risk | "
               "sectoral_lead_annex_I_section_B | out_of_scope>",
  "articles": ["<EU AI Act article(s) that primarily apply, e.g. 'Art. 5(1)(c)'>"],
  "applicable_from": "<ISO date YYYY-MM-DD this obligation set applies from, "
                      "under the POST-OMNIBUS timeline, or null if not applicable "
                      "(e.g. minimal-risk or out-of-scope systems with no specific "
                      "obligation start date)>",
  "flags": ["<zero or more of: prohibited_practice | human_review | "
            "not_legal_advice | effective_date_future>"],
  "rationale": "<1-2 sentence legal rationale citing the specific article/provision>"
}}

Rules:
- risk_tier must be exactly one of the eight listed values — no others.
- If risk_tier is "prohibited" or "high", flags MUST include both
  "not_legal_advice" and "human_review".
- If the applicable date under the post-Omnibus timeline is in the future
  relative to today, include "effective_date_future" in flags.
- Return ONLY the JSON object, no prose, no markdown fences.
""",
    ),
])
