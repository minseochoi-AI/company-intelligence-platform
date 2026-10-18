# Company analysis output contract

Return these sections:

1. **Question and boundary** — entity, jurisdiction, as-of date, purpose, exclusions.
2. **Verified identity** — stable identifiers and unresolved identity conflicts.
3. **Observed facts** — claim, source ID, observation time, artifact locator/hash.
4. **Comparable analysis** — only semantically compatible rows; state the signature.
5. **Inferences** — reasoning separated from observed facts with confidence and alternatives.
6. **Unknowns and conflicts** — missing fields, stale evidence, contradictory sources.
7. **Next evidence action** — the smallest query that can close a material gap.

Do not express an investment recommendation. If exporting for career or venture analysis, produce `EvidenceBundle`/`EvidenceBundleRef` version `1.0.0`. Restricted or unknown-rights sources may support internal reasoning but must not be represented as reusable training or product data.
