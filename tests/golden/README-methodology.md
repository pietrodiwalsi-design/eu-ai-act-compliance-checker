# EU AI Act Golden Set v1.0 — Methodology & Acceptance Criteria

Expert-labeled regression fixtures for the compliance engine (implements P0 findings
NFR-02 accuracy target + compliance-engine tests from the 2026-07-05 review).

## Legal baseline — IMPORTANT

Labels reflect the AI Act **as amended by the Digital Omnibus on AI** (political
agreement 7 May 2026; EP 16 Jun; Council 29 Jun 2026; OJ publication July 2026):

| Change | Old | New (Omnibus) |
|---|---|---|
| Annex III high-risk obligations | 2 Aug 2026 | **2 Dec 2027** |
| Annex I high-risk obligations | 2 Aug 2027 | **2 Aug 2028** |
| Art. 50(2) watermarking (systems pre-Aug-2026) | 2 Aug 2026 | **2 Dec 2026** (post-Aug-2026 systems: immediate) |
| Art. 5 prohibitions | 8 practices | **+ NCII "nudifiers" + AI-CSAM** (from 2 Dec 2026) |
| Machinery Regulation | Annex I **Section A** (dual compliance) | **Section B** (sectoral law leads) |
| "Safety component" | broad | excludes pure assistance/optimization/convenience/QC unless failure endangers health/safety |
| Art. 6(3) registration | full Annex VIII B | simplified (points 7, 9 deleted; obligation remains) |

**A checker trained/prompted on the 2024 text will fail cases P03, H01 (date), A02, T03.
That is intentional — these are the cases that detect an outdated engine.**

## Case distribution (26)

By expected tier: 10 high-risk (7 Annex III incl. insurance 5(c), medical device,
downstream-GPAI HR, real-time-RBI exception case) · 5 prohibited (incl. 1 new-Omnibus
nudifier) · 4 minimal (incl. the two false-positive traps: 1:1 verification,
motor-insurance pricing) · 3 limited/Art. 50 · 1 Art. 6(3) derogation ·
1 Annex I Section B (machinery, post-Omnibus) · 1 GPAI systemic · 1 out-of-scope.

Sector emphasis: insurance/financial services (H03 life/health = high-risk vs.
N03 motor = NOT high-risk is the single most valuable discriminator for this product's
target market).

## Acceptance criteria (NFR-02, now measurable)

| Metric | Target | Hard/soft |
|---|---|---|
| Risk-tier agreement | ≥ 92% (24/26) | hard |
| Prohibited recall | 100% (all 5 P-cases flagged prohibited) | **hard — zero tolerance** |
| Prohibited precision | no non-P case classified prohibited (S02 trap) | **hard** |
| Primary article correct | ≥ 80% | soft |
| Post-Omnibus dates correct | ≥ 80% of dated cases | hard (product ships wrong advice otherwise) |
| Disclaimer + human-review flag on every High/Prohibited output | 100% | hard (E&O control, FR-liability finding) |

## Maintenance protocol

1. Labels change ONLY with a documented legal source (OJ text, Commission guidance).
2. Every label change = new minor version + entry in the changelog below.
3. Re-run the suite on EVERY prompt change, retrieval-corpus change, or model swap —
   a prompt edit is a legal-logic change (review finding: version your prompts).
4. Review cadence: quarterly, or upon any AI Act amendment/delegated act.

## Changelog

- v1.0 (2026-07-06): initial 26 cases, post-Omnibus baseline. Labeled by Fable
  (research vs. Reg. 2024/1689 + Omnibus final package), pending Peter's review sign-off.

## Sources

- Regulation (EU) 2024/1689 (AI Act)
- Digital Omnibus on AI — final package (Council ST 9247/2026); Covington Inside
  Global Tech summary 28 May 2026; Gibson Dunn / DLA Piper / Hogan Lovells client alerts May–June 2026.
