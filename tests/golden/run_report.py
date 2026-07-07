"""
Standalone runner (outside pytest) that produces the raw comparison JSON used
for the Groq-vs-xAI report. Not part of the pytest suite itself — the pytest
harness (test_golden_set.py) remains the CI-facing acceptance gate; this
script just captures full per-case detail + timing for reporting.

Usage:
    LLM_PROVIDER=groq python3 tests/golden/run_report.py > /tmp/golden-run/groq.json
    LLM_PROVIDER=xai  python3 tests/golden/run_report.py > /tmp/golden-run/xai.json
"""
import asyncio
import json
import os
import sys
import time
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND_DIR))

GOLDEN = json.loads((Path(__file__).parent / "golden-set-v1.json").read_text())
CASES = GOLDEN["cases"]

_ONLY_IDS = os.environ.get("GOLDEN_ONLY_IDS", "").strip()
if _ONLY_IDS:
    _wanted = set(_ONLY_IDS.split(","))
    CASES = [c for c in CASES if c["id"] in _wanted]


async def main() -> None:
    from app.services.rag import rag_pipeline
    from app.prompts.golden_set_classification import GOLDEN_SET_CLASSIFICATION_PROMPT

    rag_pipeline.load_knowledge_base()
    chain = GOLDEN_SET_CLASSIFICATION_PROMPT | rag_pipeline._llm

    provider = os.environ.get("LLM_PROVIDER", "")
    out = {"provider": provider, "cases": []}

    for case in CASES:
        t0 = time.monotonic()
        retrieved = rag_pipeline.retrieve_relevant_articles(case["input"])
        try:
            response = await chain.ainvoke({
                "scenario": case["input"],
                "retrieved_articles": retrieved,
            })
            raw = response.content if hasattr(response, "content") else str(response)
            raw = raw.strip()
            if raw.startswith("```"):
                raw = raw.strip("`")
                if raw.lower().startswith("json"):
                    raw = raw[4:]
                raw = raw.strip()
            parsed = json.loads(raw)
            got = {
                "risk_tier": parsed.get("risk_tier"),
                "articles": parsed.get("articles", []) or [],
                "applicable_from": parsed.get("applicable_from"),
                "flags": parsed.get("flags", []) or [],
                "rationale": parsed.get("rationale", ""),
                "error": None,
            }
        except Exception as exc:  # noqa: BLE001 - report, don't crash the run
            got = {
                "risk_tier": "__error__",
                "articles": [],
                "applicable_from": None,
                "flags": [],
                "rationale": "",
                "error": str(exc)[:300],
            }
        elapsed = round(time.monotonic() - t0, 2)
        out["cases"].append({
            "id": case["id"],
            "expected": case["expected"],
            "got": got,
            "elapsed_seconds": elapsed,
        })
        print(f"  {case['id']}: {got['risk_tier']} ({elapsed}s)", file=sys.stderr)

    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
