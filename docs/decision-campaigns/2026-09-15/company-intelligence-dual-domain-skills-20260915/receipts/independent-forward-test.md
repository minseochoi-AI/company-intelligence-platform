# Independent forward-test round 2 — final

## Verdict

**PASS.** The two realistic requests route and stop correctly, the updated artifact contracts reject all tested invalid cases, generated comparison provenance is hash-bound and verifiable, and ownership is consistent across the skills, boundary document, and executable behavior.

## Request 1: saved-evidence Korean company analysis

- `COMPANY_INTEL_PROJECT_ROOT` is unset and the company name is absent.
- Correct action: ask for the CIL checkout and exact company identity; explicitly record the as-of date, analysis/comparison question, and allowed evidence age as unresolved.
- Stop before `원천-상태` or any company analysis command.
- After inputs exist: verify `<root>/config/providers.json`, run saved-data source status and the smallest matching command, validate the run manifest, and return the seven-section report.
- Downstream output is `EvidenceBundle`/`EvidenceBundleRef`; company analysis does not own a `DomainPlan`.

## Request 2: Korean defensible venture discovery

- Correct action: remain in `CONFIGURE`; do not browse, classify markets, size TAM/SAM/SOM, recommend a market, or emit a `DomainPlan` yet.
- A session containing the known resources, Korea, agriculture/welfare/education, and `desired_barriers: ["physical"]` validates.
- The new runway, prototype-budget, certifications, and forbidden-path fields are present and required; omitting a new required field is rejected.
- Unknown scalar constraints remain `null`. The computed nine gaps cover time, cash, field access, runway, prototype budget, risk, hardware/regulatory tolerance, and sales horizon.
- `research_gaps` now requires exact equality: omitting calculated gaps and adding a fake extra gap are both rejected.

## Shared comparison contract

- Invalid ISO date: rejected.
- Malformed axis row: rejected.
- Valid career and venture `DomainPlanRef`: verified.
- Generated comparison: accepted with five exact axes, consistent status/unresolved axes, `decision: human-required`, safe relative ref paths, matching ref-file SHA-256 values, and digest-derived comparison ID.
- All-zero/tampered ref digests: rejected by resolving the paths relative to the comparison file and hashing the real ref files.
- Parent-traversing `../refs/...` paths: rejected; `compare` also fails when its output location would require parent traversal.

## Ownership

- Career and venture-discovery own their domain reasoning and `DomainPlan` production.
- Company-analysis owns company reasoning and `EvidenceBundle` production.
- The shared non-skill package owns validation, hash-bound references, and neutral `DualPathComparison` generation; venture is only the caller; the human owns the decision.
- Executable confirmation: company `DomainPlan` rejected, company `EvidenceBundle` accepted, career/venture refs accepted, comparison generated only by shared `interop.py`.

## Fresh verification results

- Valid CONFIGURE session: exit 0.
- Omitted gap / extra fake gap / missing new field: exit 1 each.
- Invalid date / malformed axis / tampered SHA / parent traversal: exit 1 each.
- Career ref / venture ref / generated comparison / company EvidenceBundle: exit 0.
- Company DomainPlan: exit 1.
- Venture and interop self-tests: exit 0.
