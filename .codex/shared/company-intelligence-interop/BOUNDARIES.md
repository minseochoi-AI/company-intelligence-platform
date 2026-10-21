# Company Intelligence Interop Boundaries

This directory is a versioned, non-skill contract package. It does not trigger an agent and does not own research workflows.

- The career and venture-discovery skills own their domain reasoning and `DomainPlan` production. Company-analysis owns company reasoning and `EvidenceBundle` production.
- This package owns structural validation, hash-bound references, and `DualPathComparison` generation.
- A comparison reports comparable and missing axes; it never chooses employment or entrepreneurship for the user.
- `implementation_plan_sha256` remains campaign implementation authority. `DomainPlanRef.sha256` and `EvidenceBundleRef.sha256` bind domain artifacts.
- Skills may emit `CampaignLink` proposals. Only `decision-campaign-workbook` owns approval, scope locks, cohorts, authorization, and completion receipts.
- Connector candidates are not production dependencies until evidence, rights, quota, security, and operations gates pass.
- Reference paths must be relative to the reference file, may not traverse parents, and must match their SHA-256 digest.


Version 2.0.0 is explicit. Its schemas live in cil_contracts/resources/research.
Evidence kinds distinguish observed/computed/source_modelled/assumption/proposal/unknown/conflict.
Missing values need reasons; numerical confidence requires calibration evidence.
DomainPlan v2 uses Money {amount, currency}; currency conflicts remain unresolved.
References bind the same version as their targets. Comparison never converts currency or chooses a path.
The v1 schema files and v1 artifact bytes remain unchanged.
