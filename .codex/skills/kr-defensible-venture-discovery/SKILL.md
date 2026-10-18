---
name: kr-defensible-venture-discovery
description: Discover and test Korean startup opportunities against founder constraints, competitors, data rights, grants, and technical barriers.
---

# KR Defensible Venture Discovery

Treat each opportunity as a falsifiable hypothesis, not an idea score. A grant, public dataset, algorithm, or absence of obvious competitors is not itself a market.

## Modes

- `CONFIGURE`: record founder resources, time, cash, geography, field access, hardware tolerance, regulatory tolerance, sales horizon, and non-goals before research.
- `BASELINE`: map problem holder, buyer, user, payer, workflow, spend proxy, alternatives, incumbents, procurement path, and data rights.
- `GAP`: list which required fields are missing or too stale to compare.
- `AUGMENT`: research only the material gaps; preserve previous evidence and revisions.
- `RECLASSIFY`: apply [market-archetypes.md](references/market-archetypes.md) after competitor and substitute searches.
- `DECIDE`: compare surviving hypotheses against constraints and produce experiments, kill criteria, and a venture `DomainPlan`. A human makes the final choice.

## Workflow

1. Read [research-workflow.md](references/research-workflow.md) and create or update a `VentureSession`. Do not start broad browsing until `CONFIGURE` has explicit unknowns.
2. Separate source acquisition rights, analysis rights, product-use rights, personal-data constraints, and refresh cost using [evidence-and-barriers.md](references/evidence-and-barriers.md). OpenAI model output is an inference, not a data source or owned dataset.
3. Generate hypotheses in the user's feasible intersection: software capability, available Korean public/server/grant resources, domain access, physical integration, and protectable technical learning. Include a software-only control hypothesis to expose unnecessary hardware.
4. For each hypothesis, quantify TAM/SAM/SOM only from explicit units and assumptions. Record market concentration, named incumbents, substitutes, switching costs, regulatory/procurement gates, data access, build/deployment cost, and time-to-first-paid-pilot.
5. Run competitor searches before assigning an archetype. “No result” means `unverified-white-space`, never `uncontested` or “blue ocean.” Use CIL only after naming an actual company or institution, and consume its validated `EvidenceBundleRef` rather than importing CIL calculations.
6. Validate artifacts with `python3 scripts/venture_artifacts.py validate-session <session.json>` and `validate-opportunity <hypothesis.json>`. Use `gaps` to plan the next bounded research pass.
7. Produce a venture `DomainPlan`/`DomainPlanRef`. This skill is only the comparison caller: the shared non-skill `interop.py` owns `DualPathComparison` creation, reports missing axes, and always leaves `decision: human-required`.

Use `decision-campaign-workbook` only after a multi-decision implementation scope is proposed. Link via `CampaignLink`; do not inherit, copy, or mutate its approval workflow.
