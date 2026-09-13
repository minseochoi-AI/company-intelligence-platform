from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .analysis_service import build_company_timeline, evaluate_ai_event, evaluate_valuation_scenarios
from .analytics import (
    dcf_scenarios,
    difference_in_differences,
    event_study,
    financial_metrics,
    future_value_score,
    hiring_change,
    macro_sensitivity,
    rank_companies,
    event_study_prerequisites,
    valuation_prerequisites,
)
from .config import Settings
from .connectors.registry import source_health
from .evidence import write_json
from .exporting import build_export_bundle
from .facets import build_job_facets
from .interactive import ArrowMenu, build_interactive_request, load_scripted_selector, write_interactive_profile
from .job_search import JobSearchProfile, normalize_provider_payloads, search_job_dataframes
from .models import SearchProfile
from .pipeline import actual_analysis
from .reporting import write_validation_report
from .query_contract import company_search_profile_from_mapping
from .run_manifest import build_run_manifest, write_run_manifest
from .screening import ScreenerProfile, screen_companies
from .search import (
    explain_company_evaluation,
    rank_candidate_evaluations,
    rank_candidates,
    validate_search_profile,
)
from .validation import validate
from .warehouse import Warehouse


def _demo(settings: Settings) -> dict:
    facts = {
        "revenue": 1000.0,
        "revenue_previous": 900.0,
        "gross_profit": 430.0,
        "operating_income": 180.0,
        "net_income": 130.0,
        "cfo": 210.0,
        "capex": 70.0,
        "cash": 300.0,
        "debt": 200.0,
        "ebitda": 230.0,
        "current_assets": 500.0,
        "current_liabilities": 250.0,
        "interest_expense": 20.0,
        "nopat": 140.0,
        "invested_capital": 700.0,
        "employees": 100.0,
        "cost_of_revenue": 570.0,
        "average_inventory": 95.0,
    }
    peer_rows = [
        {
            "entity_id": "A",
            "country": "US",
            "industry": "SOFTWARE",
            "size_bucket": "L",
            "growth": 0.15,
            "margin": 0.22,
            "leverage": 0.4,
        },
        {
            "entity_id": "B",
            "country": "US",
            "industry": "SOFTWARE",
            "size_bucket": "L",
            "growth": 0.08,
            "margin": 0.18,
            "leverage": 1.1,
        },
        {
            "entity_id": "C",
            "country": "US",
            "industry": "SOFTWARE",
            "size_bucket": "L",
            "growth": 0.11,
            "margin": 0.25,
            "leverage": 0.7,
        },
    ]
    snapshots = [
        {"entity_id": "A", "snapshot_date": "2026-01-01", "job_id": "1"},
        {"entity_id": "A", "snapshot_date": "2026-01-01", "job_id": "2"},
        {"entity_id": "A", "snapshot_date": "2026-02-01", "job_id": "2"},
        {"entity_id": "A", "snapshot_date": "2026-02-01", "job_id": "3"},
        {"entity_id": "A", "snapshot_date": "2026-02-01", "job_id": "4"},
    ]
    result = {
        "financial_metrics": financial_metrics(facts),
        "peer_ranking": rank_companies(
            peer_rows, {"growth": 0.4, "margin": 0.4, "leverage": 0.2}, {"leverage": False}
        ),
        "macro_sensitivity": macro_sensitivity(
            [0.01, 0.02, -0.01, 0.03, 0.01, -0.02, 0.04, 0.02],
            {
                "rate_change": [0.0, 0.01, 0.02, 0.01, -0.01, 0.0, -0.02, -0.01],
                "fx_change": [0.01, -0.01, 0.02, -0.02, 0.01, 0.03, -0.01, 0.0],
            },
        ),
        "hiring_change": hiring_change(snapshots),
        "event_study": event_study(
            [0.01, 0.02, -0.01, 0.03, 0.05, 0.01, -0.02, 0.01, 0.02],
            [0.005, 0.01, -0.005, 0.01, 0.015, 0.005, -0.01, 0.0, 0.01],
            4,
            (1, 3),
        ),
        "difference_in_differences": difference_in_differences(
            [10, 11, 12], [14, 15, 16], [9, 10, 11], [10, 11, 12]
        ),
        "dcf": dcf_scenarios(revenue=1000.0, net_debt=-100.0, shares=100.0),
        "future_value": future_value_score(
            {
                "financial_health": 80,
                "profitability": 75,
                "growth_quality": 70,
                "valuation": 60,
                "macro_industry_fit": 65,
                "operations_workforce": 72,
                "disclosure_governance": 85,
            },
            {"operations_workforce": 0.6, "macro_industry_fit": 0.8},
        ),
    }
    write_json(settings.artifact_dir / "demo_analytics.json", result)
    return result


def _records(value: Any) -> list[dict[str, Any]]:
    """Convert a DataFrame-like result to JSON rows without changing values."""

    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict):
        records = to_dict("records")
        if isinstance(records, list):
            return [item for item in records if isinstance(item, dict)]
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _job_verdict_counts(frames: Any) -> dict[str, int]:
    return {
        "matched": len(frames.jobs),
        "strict_matches": len(frames.strict_matches),
        "unverifiable": len(frames.unverifiable_candidates),
        "no_match": len(frames.no_matches),
        "conflict": len(frames.conflicts),
    }


def _supplied_table_rows(supplied: dict[str, Any], name: str) -> list[dict[str, Any]]:
    """Accept both an export table object and ``JobDataFrames.as_records``."""

    tables = supplied.get("tables") if isinstance(supplied.get("tables"), dict) else supplied
    value = tables.get(name, []) if isinstance(tables, dict) else []
    if isinstance(value, dict):
        value = value.get("rows", [])
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="company-intel")
    subparsers = parser.add_subparsers(dest="command", required=True)
    validation_parser = subparsers.add_parser("validate", help="Call and validate provider probes")
    validation_parser.add_argument("--providers", default="all", help="Comma-separated provider or probe ids")
    validation_parser.add_argument("--timeout", type=float, default=45.0)
    validation_parser.add_argument("--retries", type=int, default=2)
    subparsers.add_parser("init-db", help="Initialize DuckDB schema")
    subparsers.add_parser("ingest-evidence", help="Load validation evidence metadata into DuckDB")
    subparsers.add_parser(
        "ingest-normalized", help="Load normalized financial, macro, price and job rows into DuckDB"
    )
    subparsers.add_parser("demo-analytics", help="Execute all analytic engines on deterministic demo data")
    subparsers.add_parser(
        "analyze-actual", help="Build an evidence-linked analysis from collected API samples"
    )
    search_parser = subparsers.add_parser("search", help="Search stored company evidence with an explicit profile")
    search_parser.add_argument("--profile", type=Path, required=True, help="JSON SearchProfile input")
    company_search_parser = subparsers.add_parser("company-search", help="Alias for search with an explicit company profile")
    company_search_parser.add_argument("--profile", type=Path, required=True)
    subparsers.add_parser("provider-status", help="Show configured provider activation and semantic boundaries")
    interactive_parser = subparsers.add_parser(
        "interactive", help="Choose an evidence-aware local CLI workflow with arrow keys"
    )
    interactive_parser.add_argument("--data-dir", type=Path, default=Path("artifacts"), help="Saved local JSON snapshots only")
    interactive_parser.add_argument("--output", type=Path, default=Path("artifacts/interactive"))
    interactive_parser.add_argument("--script", type=Path, help="Saved JSON answers for non-TTY/repeatable selection")
    interactive_parser.add_argument("--dry-run", action="store_true", help="Print the compiled command without executing it")
    job_search_parser = subparsers.add_parser(
        "job-search", help="Normalize and filter saved provider job responses into DataFrames"
    )
    job_search_parser.add_argument("--profile", type=Path, required=True)
    job_search_parser.add_argument(
        "--payload", action="append", required=True, help="provider=/path/to/response.json"
    )
    job_search_parser.add_argument("--output", type=Path, required=True)
    export_parser = subparsers.add_parser("export", help="Export stored company, job and requirement evidence")
    export_parser.add_argument("--output", type=Path, required=True)
    export_parser.add_argument("--entity-id", action="append", default=[])
    export_parser.add_argument("--no-xlsx", action="store_true")
    export_parser.add_argument("--tables", type=Path, help="JSON tables for an evidence-first local export")
    screen_parser = subparsers.add_parser("screen", help="Rank only comparability-compatible companies")
    screen_parser.add_argument("--profile", type=Path, required=True)
    screen_parser.add_argument("--rows", type=Path, required=True)
    timeline_parser = subparsers.add_parser("timeline", help="Build an evidence-gated company timeline")
    timeline_parser.add_argument("--rows", type=Path, required=True)
    timeline_parser.add_argument("--entity-id", required=True)
    timeline_parser.add_argument("--as-of", required=True)
    valuation_parser = subparsers.add_parser("valuation", help="Run an evidence-gated valuation scenario")
    valuation_parser.add_argument("--input", type=Path, required=True)
    event_parser = subparsers.add_parser("ai-event", help="Run an evidence-gated AI event analysis")
    event_parser.add_argument("--input", type=Path, required=True)
    explain_parser = subparsers.add_parser("explain", help="Render a saved result's limitations and provenance")
    explain_parser.add_argument("--input", type=Path, required=True)
    serve_parser = subparsers.add_parser("serve", help="Run FastAPI")
    serve_parser.add_argument("--host", default="0.0.0.0")
    serve_parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args(argv)
    settings = Settings.from_env(Path.cwd())

    if args.command == "interactive":
        if args.script:
            selector = load_scripted_selector(args.script)
        elif not sys.stdin.isatty() or not sys.stdout.isatty():
            print(json.dumps({
                "status": "tty_required", "message": "Use --script for a repeatable non-TTY interactive selection.",
                "boundary": "No provider refresh was attempted.",
            }, ensure_ascii=False, indent=2))
            return 1
        else:
            selector = ArrowMenu()
        request = build_interactive_request(selector, args.data_dir, args.output)
        request = write_interactive_profile(request, args.output)
        print(json.dumps(request.as_dict(), ensure_ascii=False, indent=2))
        if not request.runnable:
            return 1
        if args.dry_run:
            return 0
        # The compiled argv always calls one existing local-data command.  It
        # intentionally contains no refresh, provider validation, install, or
        # application-submission branch.
        return main(list(request.argv))

    if args.command == "validate":
        providers = {item.strip() for item in args.providers.split(",") if item.strip()}
        payload = validate(settings, providers, args.timeout, args.retries)
        write_validation_report(settings.artifact_dir / "runtime_report_ko.md", payload)
        print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))
        return 0 if all(item["status"] in {"passed", "missing_secret"} for item in payload["results"]) else 1
    if args.command == "init-db":
        Warehouse(settings).initialize()
        print(f"Initialized {Warehouse(settings).path}")
        return 0
    if args.command == "ingest-evidence":
        count = Warehouse(settings).ingest_validation_evidence()
        print(f"Loaded {count} evidence rows")
        return 0
    if args.command == "ingest-normalized":
        counts = Warehouse(settings).ingest_normalized_artifacts()
        print(json.dumps(counts, ensure_ascii=False, indent=2))
        return 0
    if args.command == "demo-analytics":
        result = _demo(settings)
        print(
            json.dumps(
                {"outputs": list(result), "path": str(settings.artifact_dir / "demo_analytics.json")},
                ensure_ascii=False,
            )
        )
        return 0
    if args.command == "analyze-actual":
        result = actual_analysis(settings)
        print(
            json.dumps(
                {"outputs": list(result), "path": str(settings.artifact_dir / "actual_analysis.json")},
                ensure_ascii=False,
            )
        )
        return 0
    if args.command == "provider-status":
        print(json.dumps(source_health(settings), ensure_ascii=False, indent=2))
        return 0
    if args.command in {"search", "company-search"}:
        value = json.loads(args.profile.read_text(encoding="utf-8"))
        semantic_keys = {
            "semantic_filters", "ownership_sectors", "ownership_sector", "legal_forms", "legal_form",
            "business_activities", "business_activity", "market_statuses", "market_status",
            "public_institution_types", "public_institution_type", "entity_categories", "entity_category",
            "source_operations", "source_operation", "providers", "provider", "require_resolved_identity",
            "unknown_policy",
        }
        if args.command == "company-search" or semantic_keys & set(value):
            profile = validate_search_profile(company_search_profile_from_mapping(value))
        else:
            profile = validate_search_profile(SearchProfile(
                countries=tuple(value.get("countries", [])), job_keywords=tuple(value.get("job_keywords", [])),
                industries=tuple(value.get("industries", [])), required_capabilities=tuple(value.get("required_capabilities", [])),
                languages=tuple(value.get("languages", [])), employment_types=tuple(value.get("employment_types", [])),
                country_allocation=value.get("country_allocation", {}),
            ))
        candidates = Warehouse(settings).search_candidates(profile.countries)
        evaluations = rank_candidate_evaluations(profile, candidates)
        legacy = [item.__dict__ for item in rank_candidates(profile, candidates)]
        counts: dict[str, int] = {}
        for evaluation in evaluations:
            counts[evaluation.status] = counts.get(evaluation.status, 0) + 1
        print(json.dumps({
            "profile": value,
            "candidates": legacy,
            "evaluations": [explain_company_evaluation(item) for item in evaluations],
            "verdict_counts": dict(sorted(counts.items())),
        }, ensure_ascii=False, indent=2, default=str))
        return 0
    if args.command == "job-search":
        value = json.loads(args.profile.read_text(encoding="utf-8"))
        tuple_fields = {
            "countries", "job_keywords", "occupations", "locations", "workplace_types",
            "employment_types", "languages", "posting_languages", "business_units", "industries", "company_types",
            "required_requirement_terms", "preferred_requirement_terms", "required_languages",
        }
        profile_values = {
            field: tuple(value.get(field, [])) if field in tuple_fields else value.get(field)
            for field in JobSearchProfile.__dataclass_fields__
            if field in value
        }
        payloads = {}
        for item in args.payload:
            if "=" not in item:
                raise ValueError("--payload must be provider=/path/to/response.json")
            provider, raw_path = item.split("=", 1)
            payload_path = Path(raw_path)
            payload = json.loads(payload_path.read_text(encoding="utf-8"))
            if not (isinstance(payload, dict) and payload.get("collected_at")):
                validation_path = payload_path.parent.parent / "validation_results.json"
                if validation_path.is_file():
                    validation = json.loads(validation_path.read_text(encoding="utf-8"))
                    collected_at = next(
                        (
                            row.get("collected_at")
                            for row in validation.get("results", [])
                            if row.get("provider") == provider and row.get("collected_at")
                        ),
                        None,
                    )
                    if collected_at:
                        payload = (
                            {**payload, "collected_at": collected_at}
                            if isinstance(payload, dict)
                            else {"jobs": payload, "collected_at": collected_at}
                        )
            payloads[provider] = payload
        frames = search_job_dataframes(payloads, JobSearchProfile(**profile_values))
        files = frames.write_csv(args.output)
        # Facets describe all locally supplied rows, not just rows that passed
        # the current filter.  This keeps a zero-result search explainable and
        # makes the manifest a faithful snapshot-scoped selection record.
        all_jobs, _all_requirements, _all_sources = normalize_provider_payloads(payloads)
        facets = build_job_facets(all_jobs)
        verdict_counts = _job_verdict_counts(frames)
        run_manifest = build_run_manifest(
            "job-search",
            value,
            facets,
            _records(frames.sources),
            verdict_counts,
            {path.name: path for path in files},
        )
        manifest_path = write_run_manifest(args.output / "run-manifest.json", run_manifest)
        print(json.dumps({
            "metadata": frames.metadata,
            "verdict_counts": verdict_counts,
            "facets": facets,
            "run_manifest": {"run_id": run_manifest["run_id"], "path": str(manifest_path)},
            "files": [str(path) for path in files] + [str(manifest_path)],
        }, ensure_ascii=False, indent=2))
        return 0
    if args.command == "screen":
        profile = json.loads(args.profile.read_text(encoding="utf-8"))
        rows = json.loads(args.rows.read_text(encoding="utf-8"))
        result = screen_companies(rows, ScreenerProfile(
            tuple(profile["countries"]), tuple(profile["industries"]), tuple(profile["size_buckets"]),
            profile["metrics"], profile.get("directions", {}), profile.get("as_of"), profile.get("minimum_peer_size", 2),
            profile.get("comparability_group"), profile.get("require_complete_signature", True),
        ))
        print(json.dumps({"rankings": result.rankings.to_dict("records"), "exclusions": result.exclusions.to_dict("records"), "metadata": result.metadata}, ensure_ascii=False, default=str))
        return 0
    if args.command == "timeline":
        rows = json.loads(args.rows.read_text(encoding="utf-8"))
        result = build_company_timeline(rows, entity_id=args.entity_id, as_of=args.as_of)
        print(json.dumps({"timeline": result["timeline"].to_dict("records"), "exclusions": result["exclusions"].to_dict("records"), "metadata": result["metadata"]}, ensure_ascii=False, default=str))
        return 0
    if args.command == "valuation":
        value = json.loads(args.input.read_text(encoding="utf-8"))
        prerequisites = valuation_prerequisites(
            value.get("revenue"), value.get("net_debt"), value.get("shares"), value.get("evidence")
        )
        if prerequisites["status"] != "ready":
            print(json.dumps({"status": prerequisites["status"], "prerequisites": prerequisites}, ensure_ascii=False, default=str))
            return 0
        result = evaluate_valuation_scenarios(**value)
        print(json.dumps({**result, "prerequisites": prerequisites}, ensure_ascii=False, default=str))
        return 0
    if args.command == "ai-event":
        value = json.loads(args.input.read_text(encoding="utf-8"))
        prerequisites = event_study_prerequisites(
            value.get("asset_returns", []), value.get("benchmark_returns", []), value.get("event_index"),
            value.get("event_evidence"), value.get("treated_pre"), value.get("treated_post"),
            value.get("control_pre"), value.get("control_post"),
        )
        if prerequisites["status"] != "association-only":
            print(json.dumps({"status": prerequisites["status"], "prerequisites": prerequisites}, ensure_ascii=False, default=str))
            return 0
        result = evaluate_ai_event(**value)
        print(json.dumps({**result, "prerequisites": prerequisites}, ensure_ascii=False, default=str))
        return 0
    if args.command == "explain":
        value = json.loads(args.input.read_text(encoding="utf-8"))
        if value.get("run_id") and isinstance(value.get("lineage"), dict):
            print(json.dumps({
                "status": "run-lineage",
                "run_id": value.get("run_id"),
                "command": value.get("command"),
                "verdict_counts": value.get("verdict_counts", {}),
                "facet_count": len(value.get("facets", [])) if isinstance(value.get("facets"), list) else 0,
                "source_count": len(value.get("sources", [])) if isinstance(value.get("sources"), list) else 0,
                "lineage": value["lineage"],
                "limitations": [
                    "This record describes saved snapshots only; it does not refresh provider state.",
                    "Unknown and no-match verdicts remain distinct in the linked output tables.",
                ],
            }, ensure_ascii=False, default=str))
        elif isinstance(value.get("tables"), dict) and isinstance(value.get("metadata"), dict):
            tables = value["tables"]
            print(json.dumps({
                "status": "local-result",
                "metadata": value["metadata"],
                "tables": {name: len(_supplied_table_rows(value, name)) for name in (
                    "jobs", "strict_matches", "unverifiable_candidates", "no_matches", "conflicts", "requirements",
                )},
                "limitations": value["metadata"].get("limitations", []),
            }, ensure_ascii=False, default=str))
        else:
            print(json.dumps({"status": value.get("status"), "limitations": value.get("limitations") or value.get("warning") or value.get("metadata"), "source": value.get("source")}, ensure_ascii=False, default=str))
        return 0
    if args.command == "export":
        if args.tables:
            supplied = json.loads(args.tables.read_text(encoding="utf-8"))
            data = {
                name: _supplied_table_rows(supplied, name)
                for name in (
                    "companies", "capabilities", "jobs", "requirements", "sources", "exclusions", "locations",
                    "career_overlap", "strict_matches", "no_matches", "unverifiable", "unverifiable_candidates", "conflicts", "facets",
                )
            }
            metadata = supplied.get("metadata") if isinstance(supplied.get("metadata"), dict) else {}
            run_manifest = supplied.get("run_manifest") if isinstance(supplied.get("run_manifest"), dict) else None
            if run_manifest is None:
                run_manifest = build_run_manifest(
                    "export",
                    {"tables_path": str(args.tables)},
                    data["facets"],
                    data["sources"],
                    {},
                    {"input_tables.json": args.tables},
                )
            allowed_root = args.output.parent
        else:
            data = Warehouse(settings).materialize_export_snapshot(args.entity_id or None)
            metadata = {"entity_ids": args.entity_id}
            run_manifest = build_run_manifest(
                "export",
                {"entity_ids": args.entity_id},
                [],
                data.get("sources", []),
                {},
            )
            allowed_root = settings.artifact_dir
        bundle = build_export_bundle(
            args.output,
            include_xlsx=not args.no_xlsx,
            allowed_root=allowed_root,
            metadata=metadata,
            run_manifest=run_manifest,
            **data,
        )
        print(json.dumps(bundle.manifest, ensure_ascii=False, indent=2))
        return 0
    if args.command == "serve":
        import uvicorn

        uvicorn.run("company_intel.api:app", host=args.host, port=args.port)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
