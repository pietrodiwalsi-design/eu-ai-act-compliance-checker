"""
Golden-set regression harness for the EU AI Act compliance engine.

Run:  pytest tests/golden/ -v

Wiring (one adapter, marked TODO): implement `classify(case_input) -> dict`
against the real engine (service layer preferred over HTTP for speed).
The adapter must return:
    {
      "risk_tier": str,          # prohibited | high | limited | minimal |
                                 # not_high_risk_art_6_3 | gpai_systemic_risk |
                                 # sectoral_lead_annex_I_section_B | out_of_scope
      "articles": [str],         # cited articles
      "applicable_from": str|None,  # ISO date the engine communicates
      "flags": [str],            # e.g. human_review, not_legal_advice, ...
    }

Design notes:
- Prohibited recall/precision are HARD gates (test fails on any miss).
- Tier agreement threshold: >= 24/26 (92%).
- Article + date checks are reported as warnings below threshold, hard-fail
  under 80% (see METRICS at bottom).
"""

import json
import sys
from pathlib import Path

import pytest

GOLDEN = json.loads((Path(__file__).parent / "golden-set-v1.json").read_text())
CASES = GOLDEN["cases"]

# Make `app` importable (tests/golden/ -> repo root -> backend/)
BACKEND_DIR = Path(__file__).resolve().parents[2] / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


# ---------------------------------------------------------------------------
# Adapter: calls the REAL RAG pipeline (same knowledge-base retrieval + same
# LLM instance as production, selected via LLM_PROVIDER) against golden-set
# free-text scenarios. Not mocked. See app/prompts/golden_set_classification.py
# for why a dedicated prompt is used instead of the wizard-answers prompt.
# ---------------------------------------------------------------------------
def classify(case_input: str) -> dict:
    import asyncio
    import json as _json

    from app.services.rag import rag_pipeline
    from app.prompts.golden_set_classification import GOLDEN_SET_CLASSIFICATION_PROMPT

    async def _run() -> dict:
        if not rag_pipeline._articles:
            rag_pipeline.load_knowledge_base()

        retrieved = rag_pipeline.retrieve_relevant_articles(case_input)
        chain = GOLDEN_SET_CLASSIFICATION_PROMPT | rag_pipeline._llm
        response = await chain.ainvoke({
            "scenario": case_input,
            "retrieved_articles": retrieved,
        })

        raw = response.content if hasattr(response, "content") else str(response)
        raw = raw.strip()
        # Strip markdown fences if the model added them despite instructions.
        if raw.startswith("```"):
            raw = raw.strip("`")
            if raw.lower().startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        try:
            parsed = _json.loads(raw)
        except _json.JSONDecodeError as exc:
            return {
                "risk_tier": "__parse_error__",
                "articles": [],
                "applicable_from": None,
                "flags": [],
                "rationale": f"JSON parse error: {exc}. Raw (truncated): {raw[:300]!r}",
            }

        return {
            "risk_tier": parsed.get("risk_tier"),
            "articles": parsed.get("articles", []) or [],
            "applicable_from": parsed.get("applicable_from"),
            "flags": parsed.get("flags", []) or [],
            "rationale": parsed.get("rationale", ""),
        }

    return asyncio.run(_run())


def _norm_articles(arts):
    return {a.lower().replace(" ", "") for a in arts}


@pytest.fixture(scope="session")
def results():
    return {c["id"]: classify(c["input"]) for c in CASES}


# ---- HARD GATE 1: prohibited recall = 100% --------------------------------
@pytest.mark.parametrize("case", [c for c in CASES if c["expected"]["risk_tier"] == "prohibited"],
                         ids=lambda c: c["id"])
def test_prohibited_recall(case, results):
    got = results[case["id"]]
    assert got["risk_tier"] == "prohibited", (
        f"{case['id']}: MISSED PROHIBITION — got '{got['risk_tier']}'. "
        f"Zero tolerance: {case['rationale']}"
    )


# ---- HARD GATE 2: prohibited precision (the S02 trap) ----------------------
@pytest.mark.parametrize("case", [c for c in CASES if c["expected"]["risk_tier"] != "prohibited"],
                         ids=lambda c: c["id"])
def test_prohibited_precision(case, results):
    got = results[case["id"]]
    assert got["risk_tier"] != "prohibited", (
        f"{case['id']}: FALSE PROHIBITION — expected '{case['expected']['risk_tier']}'. "
        f"{case['rationale']}"
    )


# ---- HARD GATE 3: disclaimers on high/prohibited ---------------------------
@pytest.mark.parametrize("case",
                         [c for c in CASES if c["expected"]["risk_tier"] in ("prohibited", "high")],
                         ids=lambda c: c["id"])
def test_high_and_prohibited_carry_disclaimers(case, results):
    got = results[case["id"]]
    flags = set(got.get("flags", []))
    assert "not_legal_advice" in flags, f"{case['id']}: missing not-legal-advice disclaimer"
    assert "human_review" in flags, f"{case['id']}: missing human-review recommendation"


# ---- Aggregate metrics ------------------------------------------------------
def test_tier_agreement_threshold(results):
    hits = sum(1 for c in CASES if results[c["id"]]["risk_tier"] == c["expected"]["risk_tier"])
    misses = [f"{c['id']}: expected {c['expected']['risk_tier']}, got {results[c['id']]['risk_tier']}"
              for c in CASES if results[c["id"]]["risk_tier"] != c["expected"]["risk_tier"]]
    assert hits >= 24, f"Tier agreement {hits}/{len(CASES)} < 24/26 (92%).\n" + "\n".join(misses)


def test_primary_article_accuracy(results):
    dated = [c for c in CASES if c["expected"]["primary_articles"]]
    hits = sum(
        1 for c in dated
        if _norm_articles(c["expected"]["primary_articles"]) & _norm_articles(results[c["id"]].get("articles", []))
    )
    assert hits / len(dated) >= 0.80, f"Primary-article accuracy {hits}/{len(dated)} < 80%"


def test_post_omnibus_dates(results):
    dated = [c for c in CASES if c["expected"]["applicable_from"]]
    hits = sum(
        1 for c in dated
        if (results[c["id"]].get("applicable_from") or "").startswith(c["expected"]["applicable_from"])
    )
    assert hits / len(dated) >= 0.80, (
        f"Applicability-date accuracy {hits}/{len(dated)} < 80% — "
        "engine is likely still on pre-Omnibus (2024) timelines."
    )
