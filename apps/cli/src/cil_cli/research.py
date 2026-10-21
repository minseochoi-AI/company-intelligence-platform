"""Saved-evidence research and separately sealed AI narrative commands."""

from __future__ import annotations
import argparse
import json
from pathlib import Path
from cil_contracts.requests import ReportRequest
from cil_application.research.request_compiler import compile_request
from cil_application.research.report_service import (
    run_identity,
    run_research,
    seal_report,
    verify_sealed_bundle,
)
from cil_integrations.research.capability_registry import CapabilityRegistry
from cil_integrations.storage.evidence import ResearchArtifactStore
from cil_reporting.research_workbook import render_research_workbook
from cil_integrations.catalog.repository import load_source_catalog


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="company-intel research",
        description="저장한 원천·확정 요청으로 조사 Excel을 만들고 별도 AI 보고서의 근거를 검증합니다.",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "run"):
        command = commands.add_parser(name)
        command.add_argument("--request", type=Path, required=True)
        command.add_argument("--snapshot", type=Path, required=True)
        command.add_argument("--catalog", type=Path)
        if name == "run":
            command.add_argument("--output", type=Path, required=True)
    for name in ("verify", "report"):
        command = commands.add_parser(name)
        command.add_argument("--bundle", type=Path, required=True)
        command.add_argument("--manifest-sha256", required=True)
        if name == "report":
            command.add_argument("--narrative", type=Path, required=True)
            command.add_argument("--claims", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command in {"validate", "run"}:
            request = ReportRequest.from_dict(
                json.loads(args.request.read_text(encoding="utf-8"))
            )
            snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))
            registry = (
                CapabilityRegistry.from_catalog(
                    json.loads(args.catalog.read_text(encoding="utf-8"))
                )
                if args.catalog
                else CapabilityRegistry.from_source_catalog(load_source_catalog())
            )
            if args.command == "validate":
                result = compile_request(request, snapshot, registry)
            else:
                result = run_research(
                    request,
                    snapshot,
                    registry,
                    ResearchArtifactStore(
                        args.output / run_identity(request, snapshot)
                    ),
                    renderer=render_research_workbook,
                )
        else:
            store = ResearchArtifactStore(args.bundle)
            result = (
                verify_sealed_bundle(store, args.manifest_sha256)
                if args.command == "verify"
                else seal_report(
                    store,
                    args.manifest_sha256,
                    args.narrative.read_text(encoding="utf-8"),
                    json.loads(args.claims.read_text(encoding="utf-8")),
                )
            )
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 2 if result.get("status") in {"NEEDS_INPUT", "NEEDS_EVIDENCE"} else 0
    except (ValueError, OSError, TypeError, KeyError) as error:
        print(json.dumps({"status": "ERROR", "error": str(error)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
