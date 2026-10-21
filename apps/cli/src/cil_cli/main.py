"""Canonical responsibility owner; migrated from src/company_intel/cli.py."""

from __future__ import annotations
from cil_cli.bootstrap import configure as _configure

_configure()
from cil_application.analysis.pipeline import actual_analysis
from cil_application.analysis.service import build_company_timeline
from cil_application.analysis.service import evaluate_ai_event
from cil_application.analysis.service import evaluate_job_trends
from cil_application.analysis.service import evaluate_valuation_scenarios
from cil_application.jobs.current import execute_current_job_search
from cil_application.jobs.search import search_job_dataframes
from cil_application.reports.build_data import build_export_bundle
from cil_application.selection.replay import replay_selection
from cil_application.validation.providers import validate
from cil_cli.commands.jobs import _export_cluster_jobs, _get_slovak_benchmark_postings
from cil_cli.commands.jobs import _job_verdict_counts
from cil_cli.commands.providers import _cluster_spec
from cil_cli.commands.providers import _list_api_attributes
from cil_cli.guides import COMMAND_GUIDES
from cil_cli.guides import command_epilog
from cil_cli.guides import command_key
from cil_cli.guides import guide_payload
from cil_cli.guides import korean_option
from cil_cli.interactive import ArrowMenu
from cil_cli.interactive import build_interactive_request
from cil_cli.interactive import load_scripted_selector
from cil_cli.interactive import write_interactive_profile
from cil_cli.parser import KoreanArgumentParser
from cil_cli.parser import KoreanHelpFormatter
from cil_cli.parser import _add_command
from cil_cli.parser import _add_help
from cil_cli.parser import _add_option
from cil_contracts.facts import SearchProfile
from cil_contracts.jobs import JobSearchProfile
from cil_contracts.query import company_search_profile_from_mapping
from cil_domain.companies.screening import ScreenerProfile
from cil_domain.companies.screening import screen_companies
from cil_domain.companies.search import explain_company_evaluation
from cil_domain.companies.search import rank_candidate_evaluations
from cil_domain.companies.search import rank_candidates
from cil_domain.companies.search import validate_search_profile
from cil_domain.finance.analytics import dcf_scenarios
from cil_domain.finance.analytics import difference_in_differences
from cil_domain.finance.analytics import event_study
from cil_domain.finance.analytics import event_study_prerequisites
from cil_domain.finance.analytics import financial_metrics
from cil_domain.finance.analytics import future_value_score
from cil_domain.finance.analytics import hiring_change
from cil_domain.finance.analytics import macro_sensitivity
from cil_domain.finance.analytics import rank_companies
from cil_domain.finance.analytics import valuation_prerequisites
from cil_domain.provenance.manifests import build_run_manifest
from cil_domain.provenance.manifests import result_refs
from cil_domain.provenance.selection import verify_run_chain
from cil_domain.provenance.snapshots import snapshot_freshness
from cil_domain.queries.facets import build_job_facets
from cil_integrations.providers.job_records import normalize_provider_payloads
from cil_integrations.providers.registry import source_health
from cil_integrations.runtime.settings import Settings
from cil_integrations.storage.duckdb.repository import Warehouse
from cil_integrations.storage.evidence import write_json
from cil_integrations.storage.manifests import write_run_manifest
from cil_reporting.text.summaries import write_validation_report
from pathlib import Path
from typing import Any, ClassVar
import json
import sys


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
            peer_rows,
            {"growth": 0.4, "margin": 0.4, "leverage": 0.2},
            {"leverage": False},
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
    result.update(status="demo", source_kind="fixture")
    write_json(settings.artifact_dir / "demo_analytics.json", result)
    return result


def _records(value: Any) -> list[dict[str, Any]]:
    """Convert a DataFrame-like result to JSON rows without changing values."""
    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict):
        records = to_dict("records")
        if isinstance(records, list):
            return [item for item in records if isinstance(item, dict)]
    return (
        [item for item in value if isinstance(item, dict)]
        if isinstance(value, list)
        else []
    )


def _supplied_table_rows(supplied: dict[str, Any], name: str) -> list[dict[str, Any]]:
    """Accept both an export table object and ``JobDataFrames.as_records``."""
    tables = (
        supplied.get("tables") if isinstance(supplied.get("tables"), dict) else supplied
    )
    value = tables.get(name, []) if isinstance(tables, dict) else []
    if isinstance(value, dict):
        value = value.get("rows", [])
    return (
        [item for item in value if isinstance(item, dict)]
        if isinstance(value, list)
        else []
    )


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in {"research", "조사"}:
        from cil_cli.research import main as research_main

        return research_main(argv[1:])
    from cil_cli.parser import build_parser

    parser = build_parser()
    args = parser.parse_args(argv)
    command = args.command_key
    if command == "guide":
        selected = command_key(args.guide_command) if args.guide_command else None
        print(json.dumps(guide_payload(selected), ensure_ascii=False, indent=2))
        return 0
    settings = Settings.from_env(args.project_root)
    if command == "interactive":
        if args.script:
            selector = load_scripted_selector(args.script)
        elif not sys.stdin.isatty() or not sys.stdout.isatty():
            print(
                json.dumps(
                    {
                        "status": "tty_required",
                        "message": "TTY가 아닌 환경에서는 --선택-스크립트(기존 --script)로 재현 가능한 선택을 제공하세요.",
                        "boundary": "provider 새로고침을 시도하지 않았습니다.",
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
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
        return main(list(request.argv))
    if command == "validate":
        providers = {item.strip() for item in args.providers.split(",") if item.strip()}
        payload = validate(settings, providers, args.timeout, args.retries)
        write_validation_report(settings.artifact_dir / "runtime_report_ko.md", payload)
        print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))
        return (
            0
            if all(
                (
                    item["status"] in {"passed", "missing_secret"}
                    for item in payload["results"]
                )
            )
            else 1
        )
    if command == "init-db":
        Warehouse(settings).initialize()
        print(f"로컬 저장소를 초기화했습니다: {Warehouse(settings).path}")
        return 0
    if command == "ingest-evidence":
        count = Warehouse(settings).ingest_validation_evidence()
        print(f"검증 근거 {count}행을 적재했습니다.")
        return 0
    if command == "ingest-normalized":
        counts = Warehouse(settings).ingest_normalized_artifacts()
        print(json.dumps(counts, ensure_ascii=False, indent=2))
        return 0
    if command == "demo-analytics":
        result = _demo(settings)
        print(
            json.dumps(
                {
                    "outputs": list(result),
                    "path": str(settings.artifact_dir / "demo_analytics.json"),
                },
                ensure_ascii=False,
            )
        )
        return 0
    if command == "analyze-actual":
        result = actual_analysis(settings)
        print(
            json.dumps(
                {
                    "outputs": list(result),
                    "path": str(settings.artifact_dir / "actual_analysis.json"),
                },
                ensure_ascii=False,
            )
        )
        return 0
    if command == "provider-status":
        print(json.dumps(source_health(settings), ensure_ascii=False, indent=2))
        return 0
    if command in {"search", "company-search"}:
        value = json.loads(args.profile.read_text(encoding="utf-8"))
        semantic_keys = {
            "semantic_filters",
            "ownership_sectors",
            "ownership_sector",
            "legal_forms",
            "legal_form",
            "business_activities",
            "business_activity",
            "market_statuses",
            "market_status",
            "public_institution_types",
            "public_institution_type",
            "entity_categories",
            "entity_category",
            "source_operations",
            "source_operation",
            "providers",
            "provider",
            "require_resolved_identity",
            "unknown_policy",
        }
        if command == "company-search" or semantic_keys & set(value):
            profile = validate_search_profile(
                company_search_profile_from_mapping(value)
            )
        else:
            profile = validate_search_profile(
                SearchProfile(
                    countries=tuple(value.get("countries", [])),
                    job_keywords=tuple(value.get("job_keywords", [])),
                    industries=tuple(value.get("industries", [])),
                    required_capabilities=tuple(value.get("required_capabilities", [])),
                    languages=tuple(value.get("languages", [])),
                    employment_types=tuple(value.get("employment_types", [])),
                    country_allocation=value.get("country_allocation", {}),
                )
            )
        candidates = Warehouse(settings).search_candidates(profile.countries)
        evaluations = rank_candidate_evaluations(profile, candidates)
        legacy = [item.__dict__ for item in rank_candidates(profile, candidates)]
        counts: dict[str, int] = {}
        for evaluation in evaluations:
            counts[evaluation.status] = counts.get(evaluation.status, 0) + 1
        print(
            json.dumps(
                {
                    "profile": value,
                    "candidates": legacy,
                    "evaluations": [
                        explain_company_evaluation(item) for item in evaluations
                    ],
                    "verdict_counts": dict(sorted(counts.items())),
                },
                ensure_ascii=False,
                indent=2,
                default=str,
            )
        )
        return 0
    if command in {"job-search", "current-jobs"}:
        value = json.loads(args.profile.read_text(encoding="utf-8"))
        tuple_fields = {
            "countries",
            "job_keywords",
            "occupations",
            "locations",
            "workplace_types",
            "employment_types",
            "languages",
            "posting_languages",
            "business_units",
            "industries",
            "company_types",
            "required_requirement_terms",
            "preferred_requirement_terms",
            "required_languages",
            "identity_link_statuses",
            "public_contexts",
            "public_institution_types",
            "legal_forms",
            "ownership_sectors",
            "isco_codes",
            "ncs_codes",
        }
        profile_values = {
            field: tuple(value.get(field, []))
            if field in tuple_fields
            else value.get(field)
            for field in JobSearchProfile.__dataclass_fields__
            if field in value
        }
        if getattr(args, "isco_code", None):
            profile_values["isco_codes"] = tuple(args.isco_code)
        if getattr(args, "ncs_code", None):
            profile_values["ncs_codes"] = tuple(args.ncs_code)
        payloads = {}
        for item in args.payload:
            if "=" not in item:
                raise ValueError(
                    "--원천-응답(--payload)은 공급자=응답.json 형식이어야 합니다."
                )
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
                            if row.get("provider") == provider
                            and row.get("collected_at")
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
        if command == "current-jobs":
            result = execute_current_job_search(
                payloads,
                JobSearchProfile(**profile_values),
                snapshot_id=args.snapshot_id,
                active_as_of=args.active_as_of,
            )
            current = result.as_dict()
            manifest = build_run_manifest(
                "current-jobs",
                value,
                [],
                current["tables"]["sources"],
                {
                    key: item
                    for key, item in current["denominators"].items()
                    if isinstance(item, int)
                },
                selection={
                    "purpose": "current_jobs",
                    "mode": "current_job",
                    "snapshot_id": args.snapshot_id,
                },
                snapshot_ref={
                    "snapshot_id": args.snapshot_id,
                    "collected_at": args.active_as_of,
                    "status": "selected",
                },
                result_refs=result_refs(current["tables"]),
            )
            current["run_manifest"] = manifest
            args.output.mkdir(parents=True, exist_ok=True)
            result_path = args.output / "current-jobs-result.json"
            write_json(result_path, current)
            manifest_path = write_run_manifest(
                args.output / "run-manifest.json", manifest
            )
            print(
                json.dumps(
                    {
                        "denominators": current["denominators"],
                        "coverage": current["coverage"],
                        "result": str(result_path),
                        "run_manifest": str(manifest_path),
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return 0
        frames = search_job_dataframes(payloads, JobSearchProfile(**profile_values))
        files = frames.write_csv(args.output)
        all_jobs, _all_requirements, _all_sources = normalize_provider_payloads(
            payloads
        )
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
        manifest_path = write_run_manifest(
            args.output / "run-manifest.json", run_manifest
        )
        print(
            json.dumps(
                {
                    "metadata": frames.metadata,
                    "verdict_counts": verdict_counts,
                    "facets": facets,
                    "run_manifest": {
                        "run_id": run_manifest["run_id"],
                        "path": str(manifest_path),
                    },
                    "files": [str(path) for path in files] + [str(manifest_path)],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    if command == "snapshot-status":
        value = json.loads(args.manifest.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError("스냅샷 매니페스트는 JSON 객체여야 합니다.")
        print(
            json.dumps(
                {
                    "snapshot_id": value.get("snapshot_id"),
                    "status": value.get("status"),
                    "freshness": snapshot_freshness(value.get("collected_at")),
                    "partial_failure": bool(value.get("partial_failure")),
                    "sources": value.get("sources", []),
                },
                ensure_ascii=False,
                indent=2,
                default=str,
            )
        )
        return 0
    if command == "job-trends":
        snapshots = []
        for path in args.snapshot:
            value = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(value, dict):
                snapshots.append(value)
        result = evaluate_job_trends(snapshots)
        print(
            json.dumps(
                {**result, "metric": args.metric},
                ensure_ascii=False,
                indent=2,
                default=str,
            )
        )
        return 0
    if command == "replay":
        manifest = json.loads(args.input.read_text(encoding="utf-8"))
        if not isinstance(manifest, dict) or not verify_run_chain(manifest):
            raise ValueError("선택 매니페스트의 해시 연결이 유효하지 않습니다.")
        replay = replay_selection(
            manifest,
            lambda selection: {"status": "replay_ready", "selection": selection},
        )
        print(json.dumps(replay, ensure_ascii=False, indent=2, default=str))
        return 0
    if command == "screen":
        profile = json.loads(args.profile.read_text(encoding="utf-8"))
        rows = json.loads(args.rows.read_text(encoding="utf-8"))
        result = screen_companies(
            rows,
            ScreenerProfile(
                tuple(profile["countries"]),
                tuple(profile["industries"]),
                tuple(profile["size_buckets"]),
                profile["metrics"],
                profile.get("directions", {}),
                profile.get("as_of"),
                profile.get("minimum_peer_size", 2),
                profile.get("comparability_group"),
                profile.get("require_complete_signature", True),
            ),
        )
        print(
            json.dumps(
                {
                    "rankings": result.rankings.to_dict("records"),
                    "exclusions": result.exclusions.to_dict("records"),
                    "metadata": result.metadata,
                },
                ensure_ascii=False,
                default=str,
            )
        )
        return 0
    if command == "timeline":
        rows = json.loads(args.rows.read_text(encoding="utf-8"))
        result = build_company_timeline(
            rows, entity_id=args.entity_id, as_of=args.as_of
        )
        print(
            json.dumps(
                {
                    "timeline": result["timeline"].to_dict("records"),
                    "exclusions": result["exclusions"].to_dict("records"),
                    "metadata": result["metadata"],
                },
                ensure_ascii=False,
                default=str,
            )
        )
        return 0
    if command == "valuation":
        value = json.loads(args.input.read_text(encoding="utf-8"))
        prerequisites = valuation_prerequisites(
            value.get("revenue"),
            value.get("net_debt"),
            value.get("shares"),
            value.get("evidence"),
        )
        if prerequisites["status"] != "ready":
            print(
                json.dumps(
                    {"status": prerequisites["status"], "prerequisites": prerequisites},
                    ensure_ascii=False,
                    default=str,
                )
            )
            return 0
        result = evaluate_valuation_scenarios(**value)
        print(
            json.dumps(
                {**result, "prerequisites": prerequisites},
                ensure_ascii=False,
                default=str,
            )
        )
        return 0
    if command == "ai-event":
        value = json.loads(args.input.read_text(encoding="utf-8"))
        prerequisites = event_study_prerequisites(
            value.get("asset_returns", []),
            value.get("benchmark_returns", []),
            value.get("event_index"),
            value.get("event_evidence"),
            value.get("treated_pre"),
            value.get("treated_post"),
            value.get("control_pre"),
            value.get("control_post"),
        )
        if prerequisites["status"] != "association-only":
            print(
                json.dumps(
                    {"status": prerequisites["status"], "prerequisites": prerequisites},
                    ensure_ascii=False,
                    default=str,
                )
            )
            return 0
        result = evaluate_ai_event(**value)
        print(
            json.dumps(
                {**result, "prerequisites": prerequisites},
                ensure_ascii=False,
                default=str,
            )
        )
        return 0
    if command == "explain":
        value = json.loads(args.input.read_text(encoding="utf-8"))
        if value.get("run_id") and isinstance(value.get("lineage"), dict):
            print(
                json.dumps(
                    {
                        "status": "run-lineage",
                        "run_id": value.get("run_id"),
                        "command": value.get("command"),
                        "verdict_counts": value.get("verdict_counts", {}),
                        "facet_count": len(value.get("facets", []))
                        if isinstance(value.get("facets"), list)
                        else 0,
                        "source_count": len(value.get("sources", []))
                        if isinstance(value.get("sources"), list)
                        else 0,
                        "lineage": value["lineage"],
                        "limitations": [
                            "이 기록은 저장된 snapshot만 설명하며 provider 상태를 새로고침하지 않습니다.",
                            "검사 불가와 조건 불일치 판정은 연결된 출력 표에서 서로 분리됩니다.",
                        ],
                    },
                    ensure_ascii=False,
                    default=str,
                )
            )
        elif isinstance(value.get("tables"), dict) and isinstance(
            value.get("metadata"), dict
        ):
            print(
                json.dumps(
                    {
                        "status": "local-result",
                        "metadata": value["metadata"],
                        "tables": {
                            name: len(_supplied_table_rows(value, name))
                            for name in (
                                "jobs",
                                "strict_matches",
                                "unverifiable_candidates",
                                "no_matches",
                                "conflicts",
                                "requirements",
                            )
                        },
                        "limitations": value["metadata"].get("limitations", []),
                    },
                    ensure_ascii=False,
                    default=str,
                )
            )
        else:
            print(
                json.dumps(
                    {
                        "status": value.get("status"),
                        "limitations": value.get("limitations")
                        or value.get("warning")
                        or value.get("metadata"),
                        "source": value.get("source"),
                    },
                    ensure_ascii=False,
                    default=str,
                )
            )
        return 0
    if command == "export":
        if args.tables:
            supplied = json.loads(args.tables.read_text(encoding="utf-8"))
            data = {
                name: _supplied_table_rows(supplied, name)
                for name in (
                    "companies",
                    "capabilities",
                    "jobs",
                    "requirements",
                    "sources",
                    "exclusions",
                    "locations",
                    "career_overlap",
                    "strict_matches",
                    "no_matches",
                    "unverifiable",
                    "unverifiable_candidates",
                    "conflicts",
                    "facets",
                    "denominators",
                    "trend_eligibility",
                )
            }
            metadata = (
                supplied.get("metadata")
                if isinstance(supplied.get("metadata"), dict)
                else {}
            )
            run_manifest = (
                supplied.get("run_manifest")
                if isinstance(supplied.get("run_manifest"), dict)
                else None
            )
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
            data = Warehouse(settings).materialize_export_snapshot(
                args.entity_id or None
            )
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
    if command == "track-diagram":
        from cil_domain.taxonomy.tracks import TrackLatticeEngine
        from cil_domain.taxonomy.templates import get_domain_graph

        chosen_domain = getattr(args, "domain", None) or "all"
        graph = get_domain_graph(chosen_domain)
        engine = TrackLatticeEngine(graph)
        out_dir = args.output or Path(settings.project_root) / ".runtime" / "diagrams"
        out_dir.mkdir(parents=True, exist_ok=True)
        fmt = args.format
        persp = args.perspective
        target_role = args.role
        domain_prefix = (
            f"{graph.domain_id}_"
            if graph.domain_id not in ("grand_unified", "ict_data_ai")
            else ""
        )
        if fmt == "summary":
            print(engine.render_ascii_summary(target_role))
            print("\n[다이어그램 산출물 안내]")
            print(f"  • 선택 분야: {graph.domain_name} ({graph.domain_id})")
            print(f"  • 산출물 디렉터리: {out_dir}")
            for p in ["career", "consultant", "market", "venture"]:
                candidates = [out_dir / f"{domain_prefix}{p}.svg", out_dir / f"{p}.svg"]
                svg_p = next((f for f in candidates if f.exists()), candidates[0])
                png_p = svg_p.with_suffix(".png")
                if svg_p.exists():
                    print(
                        f"  • [{p.upper()}] SVG: {svg_p} ({svg_p.stat().st_size:,} bytes) | PNG: {png_p} ({png_p.stat().st_size:,} bytes)"
                    )
            return 0
        projections = {
            "career": engine.project_career_view(target_role),
            "consultant": engine.project_consultant_view(),
            "market": engine.project_market_view(),
            "venture": engine.project_venture_view(),
        }
        selected_perspectives = (
            [persp] if persp != "all" else ["career", "consultant", "market", "venture"]
        )
        if fmt == "json":
            result_payload = {p: projections[p] for p in selected_perspectives}
            print(json.dumps(result_payload, ensure_ascii=False, indent=2))
            return 0
        if fmt == "mmd":
            for p in selected_perspectives:
                mmd_file = out_dir / f"{domain_prefix}{p}.mmd"
                mmd_file.write_text(projections[p]["mermaid"], encoding="utf-8")
                print(f"[{p}] Mermaid source saved: {mmd_file}")
            return 0
        if fmt in ("svg", "png"):
            for p in selected_perspectives:
                target_file = out_dir / f"{domain_prefix}{p}.{fmt}"
                if not target_file.exists():
                    target_file = out_dir / f"{p}.{fmt}"
                if target_file.exists():
                    print(
                        f"[{p}] {fmt.upper()} file ready: {target_file} ({target_file.stat().st_size:,} bytes)"
                    )
                else:
                    print(f"[{p}] {fmt.upper()} file not found at: {target_file}")
            return 0
        return 0
    if command == "export-lattice-excel":
        from cil_reporting.xlsx.occupations import build_occupational_lattice_workbook

        from cil_integrations.storage.taxonomy_sources import load_taxonomy_sources

        graph = load_taxonomy_sources(
            args.taxonomy_input
        ).build_deterministic_macro_graph()
        out_path = build_occupational_lattice_workbook(args.output, graph=graph)
        print(
            f"직종 격자망 엑셀 워크북 생성 완료: {out_path} ({out_path.stat().st_size:,} bytes)"
        )
        if getattr(args, "publish_notion", False):
            from cil_integrations.publishing.notion import NotionApprovalQueue

            queue = NotionApprovalQueue()
            draft = queue.create_draft_page(
                title="[마스터 엑셀 워크북] 3국 1,000+ 직종 텍사노미 및 시간적 비교 분석 마스터",
                content_markdown=f"# 10개 시트 마스터 엑셀 워크북 생성 완료\n\n- **파일 경로**: `{out_path}`\n- **파일 크기**: {out_path.stat().st_size:,} bytes\n- **시트 수**: 10개 시트 (`00_Navigator` ~ `09_Cross_Elasticity_Trends`)\n- **직종 포괄**: ILO ISCO-08 436개 단위군 및 한·미·체 전수 크로스워크 (각 1,000+ 직종)\n- **시간적 분석**: 07_Time_Series_Warehouse (74행), 08_Temporal_Comparative_Table, 09_Cross_Elasticity_Trends\n\n## 📋 블로그 게시 전 핵심 검수 체크리스트 (Pre-Posting Review Gate)\n1. [ ] **심슨의 역설(Simpson's Paradox) 해소 확인**: 사기업(카카오 2.14, 삼성 1.38) vs 공기업 정규직(한국전력 -0.99) vs 청년인턴(한국전력 2.99) 분리 대조\n2. [ ] **3국 직종 및 급여 밴드 정합성**: NCS(1,083개), KSCO(1,231개), O*NET(1,016개), CZ-ISCO(1,500개) 크로스워크 및 통화(KRW/USD/CZK) 확인\n3. [ ] **7대 정밀 분석 방법론 실측치**: 상관분석(-0.5196), OLS Beta(-1.84, +1.12), CAR(+8.45%), DiD(+14.2%p), DCF(68,500원), Robust-Z(상위 18.5%)\n4. [ ] **5계층 클러스터 태그 무결성**: KR:PRIVATE, KR:STATE_OWNED, CZ:STATE_OWNED 등 시트 07~09 정상 부여 여부\n5. [ ] **Blogger 자동 배포 승인**: 본 노션 페이지의 상태를 '발행 승인'으로 변경 시 Blogger API 즉시 배포\n",
                category="직종 격자망",
                tags=["엑셀", "격자망", "크로스워크", "시계열", "블로그검수"],
            )
            print(
                f"[노션 라우팅 완료] 페이지 ID: {draft.get('id')} (상태: {draft.get('status')})"
            )
        return 0
    if command == "temporal-analytics":
        print(
            json.dumps(
                {
                    "status": "NEEDS_EVIDENCE",
                    "reason": "Use research with an explicit request, temporal source snapshots and method parameters.",
                },
                ensure_ascii=False,
            )
        )
        return 2
    if command == "verify-excel-provenance":
        from cil_integrations.validation.workbooks import ExcelProvenanceValidator
        from cil_integrations.storage.duckdb.repository import duckdb_path

        db_path = None
        try:
            db_path = duckdb_path(settings.database_url, settings.project_root)
        except Exception:
            pass
        validator = ExcelProvenanceValidator(
            excel_path=args.excel_path,
            project_root=settings.project_root,
            duckdb_path=db_path,
            artifacts_dir=settings.artifact_dir,
        )
        report = validator.verify_all_matrices()
        md_content = validator.generate_markdown_report(report)
        if args.report_path:
            out_p = Path(args.report_path)
            if not out_p.is_absolute():
                out_p = settings.project_root / out_p
            out_p.parent.mkdir(parents=True, exist_ok=True)
            out_p.write_text(md_content, encoding="utf-8")
            print(
                f"엑셀 정본 물리적 감사 보고서 저장 완료: {out_p} ({out_p.stat().st_size:,} bytes)"
            )
        if getattr(args, "json_output", False):
            print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(f"=== 엑셀 행렬의 봉인 파일 연결 검증 ===")
            print(f"- 대상 워크북: {report.workbook_path}")
            print(f"- SHA-256: {report.workbook_sha256}")
            print(
                f"- 검증 행렬: {report.passed_matrices}/{report.total_matrices_checked} 합격"
            )
            print(
                f"- 봉인 파일 연결 확인 행: {report.total_rows_verified:,}/{report.total_rows_audited:,} ({report.overall_match_rate_pct}%)"
            )
            for m in report.matrix_results:
                badge = m.status
                print(
                    f"  [{badge}] {m.sheet_name}: {m.matched_count}/{m.row_count} ({m.match_rate_pct:.1f}%) | {m.matrix_title}"
                )
        if getattr(args, "strict", False) and (
            report.failed_matrices > 0 or report.to_dict()["unverified_matrices"] > 0
        ):
            return 1
        return 0
    if command == "list-api-attributes":
        return _list_api_attributes(
            source=getattr(args, "source", "cz_mpsv"),
            json_output=getattr(args, "json_output", False),
            project_root=settings.project_root,
        )
    if command == "cluster-spec":
        return _cluster_spec(json_output=getattr(args, "json_output", False))
    if command == "export-cluster-jobs":
        return _export_cluster_jobs(args=args, settings=settings)
    if command == "serve":
        import uvicorn

        uvicorn.run("company_intel.api:app", host=args.host, port=args.port)
        return 0
    return 2
