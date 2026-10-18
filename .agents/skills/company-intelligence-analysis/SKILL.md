---
name: company-intelligence-analysis
description: Analyze a named company or institution from saved CIL evidence. Not for job preparation, investment advice, or startup discovery.
---

# Company Intelligence Analysis

Operate as a thin evidence orchestrator. Never reimplement CIL calculations in the skill.

1. Resolve the CIL checkout explicitly. Prefer `--프로젝트-경로`; otherwise use `COMPANY_INTEL_PROJECT_ROOT`. Confirm `<root>/config/providers.json` exists.
2. Fix the subject, country, as-of date, comparison question, and allowed evidence age. Mark missing values rather than silently choosing them.
3. Read [analysis-routing.md](references/analysis-routing.md) and choose the smallest saved-data command. Do not refresh providers unless the user explicitly asks for current data.
4. Run `company-intel --프로젝트-경로 <root> 원천-상태` before analysis. Treat activation and last probe as different facts.
5. Use CIL artifacts and CLI results as evidence. Keep facts, inferences, conflicts, and unknowns separate. Do not rank incompatible country, concept, unit, currency, period, vintage, or coverage values.
6. Validate a produced run manifest with `python3 scripts/verify_cil_artifact.py <run-manifest.json>`.
7. Format the result using [output-contract.md](references/output-contract.md). When another domain needs the result, emit an `EvidenceBundle` and hash-bound `EvidenceBundleRef` under the shared non-skill contract. Do not import CIL Python modules into another skill.

If the request crosses into job requirements, route that portion to `company-intelligence-career-research`. If it asks which startup market to enter, route it to `kr-defensible-venture-discovery`. Use `decision-campaign-workbook` only when a material multi-decision implementation campaign needs approval and scope control; do not copy its workflow here.
