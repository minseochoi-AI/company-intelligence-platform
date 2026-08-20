from __future__ import annotations

import argparse
import json
from pathlib import Path

from .analytics import (
    dcf_scenarios,
    difference_in_differences,
    event_study,
    financial_metrics,
    future_value_score,
    hiring_change,
    macro_sensitivity,
    rank_companies,
)
from .config import Settings
from .evidence import write_json
from .pipeline import actual_analysis
from .reporting import write_validation_report
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
    serve_parser = subparsers.add_parser("serve", help="Run FastAPI")
    serve_parser.add_argument("--host", default="0.0.0.0")
    serve_parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args(argv)
    settings = Settings.from_env(Path.cwd())

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
    if args.command == "serve":
        import uvicorn

        uvicorn.run("company_intel.api:app", host=args.host, port=args.port)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
