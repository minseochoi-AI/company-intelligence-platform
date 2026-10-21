"""Canonical responsibility owner; migrated from src/company_intel/validation.py."""

from __future__ import annotations
from cil_contracts.facts import Probe
from cil_domain.provenance.redaction import redact_url
from cil_domain.providers.contracts import validate_atomic_contract
from cil_domain.providers.parsing import MISSING
from cil_domain.providers.parsing import get_path
from cil_application.ports import load_source_catalog
from cil_application.ports import build_probes
from cil_contracts.runtime import RunContext as Settings
from cil_application.ports import configured_secrets
from cil_application.ports import EvidenceStore
from cil_application.ports import utc_now
from cil_application.ports import write_json
from cil_application.ports import HttpClient
from collections import Counter
from typing import Any
import json
import os
import platform
import sys
import xml.etree.ElementTree as ET


class SemanticFieldCheck:
    """A required path is usable only when it contains a non-empty value."""

    @staticmethod
    def present(value: Any) -> bool:
        return (
            value is not MISSING
            and value not in (None, "")
            and (value != [])
            and (value != {})
        )


def enumerate_paths(
    value: Any, prefix: str = "", depth: int = 0, limit: int = 800
) -> list[str]:
    paths: list[str] = []

    def visit(node: Any, current: str, level: int) -> None:
        if len(paths) >= limit:
            return
        if current:
            paths.append(current)
        if level >= 6:
            return
        if isinstance(node, dict):
            for key, item in list(node.items())[:100]:
                visit(item, f"{current}.{key}" if current else str(key), level + 1)
        elif isinstance(node, list) and node:
            visit(node[0], f"{current}.0" if current else "0", level + 1)

    visit(value, prefix, depth)
    return paths


def _parse_raw(probe: Probe, body: bytes) -> tuple[Any, list[str]]:
    if probe.expected_format == "json":
        parsed = json.loads(body.decode("utf-8-sig"))
        return (parsed, enumerate_paths(parsed))
    if probe.expected_format == "xml":
        root = ET.fromstring(body)
        tags = sorted({element.tag.rsplit("}", 1)[-1] for element in root.iter()})
        return (root, tags)
    raise ValueError(f"Unsupported expected format: {probe.expected_format}")


def _provider_error(
    probe: Probe, parsed: Any, normalized: dict[str, Any] | None
) -> str | None:
    if (
        probe.provider == "opendart"
        and isinstance(parsed, dict)
        and (parsed.get("status") != "000")
    ):
        return f"OpenDART {parsed.get('status')}: {parsed.get('message')}"
    if probe.provider == "bea" and isinstance(parsed, dict):
        error = parsed.get("BEAAPI", {}).get("Results", {}).get("Error")
        if error:
            return (
                f"BEA {error.get('APIErrorCode')}: {error.get('APIErrorDescription')}"
            )
    if (
        probe.provider == "alphavantage"
        and normalized
        and normalized.get("provider_note")
    ):
        return f"Alpha Vantage: {normalized['provider_note']}"
    if (
        probe.provider == "ecos"
        and isinstance(parsed, dict)
        and ("StatisticSearch" not in parsed)
    ):
        return f"ECOS: {parsed.get('RESULT') or parsed}"
    if probe.provider == "mpm_public_employment" and normalized:
        result_code = normalized.get("result_code")
        if result_code and result_code not in {"00", "0", "000"}:
            return f"MPM public employment {result_code}: {normalized.get('result_message')}"
    return None


def validate(
    settings: Settings,
    providers: set[str] | None = None,
    timeout: float = 45.0,
    retries: int = 2,
) -> dict[str, Any]:
    settings.artifact_dir.mkdir(parents=True, exist_ok=True)
    secrets = configured_secrets()
    store = EvidenceStore(settings.artifact_dir, list(secrets.values()))
    client = HttpClient(timeout=timeout, retries=retries)
    probes = build_probes(settings, providers)
    catalog_errors = validate_atomic_contract(
        load_source_catalog(settings.project_root / "config/providers.json"),
        {probe.id for probe in build_probes(settings)},
    )
    if catalog_errors:
        raise ValueError(
            "source catalog contract invalid: " + "; ".join(catalog_errors)
        )
    started_at = utc_now()
    results: list[dict[str, Any]] = []
    catalogs: dict[str, Any] = {}
    for index, probe in enumerate(probes, 1):
        print(f"[{index:02d}/{len(probes):02d}] {probe.id}", flush=True)
        if probe.secret_env and (not os.getenv(probe.secret_env)):
            record = {
                "id": probe.id,
                "provider": probe.provider,
                "regions": probe.regions,
                "category": probe.category,
                "status": "missing_secret",
                "http_status": None,
                "required_fields": probe.required_paths,
                "missing_fields": probe.required_paths,
                "capabilities": probe.capabilities,
                "quota_note": probe.quota_note,
                "limitation": probe.limitation,
                "secret_env": probe.secret_env,
                "message": f"Environment variable {probe.secret_env} is not configured.",
            }
            results.append(record)
            store.append_log("errors", {"collected_at": utc_now(), **record})
            continue
        response = client.execute(probe)
        normalized: dict[str, Any] | None = None
        parsed: Any = None
        parse_error = None
        field_checks: dict[str, bool] = {}
        paths: list[str] = []
        try:
            parsed, paths = _parse_raw(probe, response.body)
            if probe.normalizer:
                normalized = probe.normalizer(
                    response.body, response.headers.get("content-type", "")
                )
            validation_root = parsed if probe.expected_format == "json" else normalized
            for path in probe.required_paths:
                field_checks[path] = SemanticFieldCheck.present(
                    get_path(validation_root, path)
                )
        except (
            ValueError,
            TypeError,
            KeyError,
            IndexError,
            UnicodeError,
            ET.ParseError,
        ) as error:
            parse_error = f"{type(error).__name__}: {error}"
        provider_error = _provider_error(probe, parsed, normalized)
        missing_fields = [path for path, exists in field_checks.items() if not exists]
        http_ok = response.status_code is not None and 200 <= response.status_code < 300
        if not http_ok:
            status = "http_error"
        elif parse_error:
            status = "parse_error"
        elif provider_error:
            status = "provider_error"
        elif missing_fields:
            status = "field_mismatch"
        else:
            status = "passed"
        extension = "xml" if probe.expected_format == "xml" else "json"
        evidence = store.preserve(probe, response, normalized, extension)
        record = {
            "id": probe.id,
            "provider": probe.provider,
            "regions": probe.regions,
            "category": probe.category,
            "status": status,
            "http_status": response.status_code,
            "elapsed_ms": response.elapsed_ms,
            "attempts": response.attempts,
            "url": redact_url(probe.url, list(secrets.values())),
            "expected_format": probe.expected_format,
            "parse_error": parse_error,
            "provider_error": provider_error,
            "transport_error": response.error,
            "required_fields": probe.required_paths,
            "field_checks": field_checks,
            "missing_fields": missing_fields,
            "field_count": len(paths),
            "capabilities": probe.capabilities,
            "quota_note": probe.quota_note,
            "limitation": probe.limitation,
            **evidence,
        }
        results.append(record)
        catalogs[probe.id] = {"paths": paths, "required_checks": field_checks}
        if status != "passed":
            store.append_log("errors", {"collected_at": utc_now(), **record})
    finished_at = utc_now()
    status_counts = Counter((item["status"] for item in results))
    payload = {
        "schema_version": "1.0",
        "started_at": started_at,
        "finished_at": finished_at,
        "environment": {"python": sys.version, "platform": platform.platform()},
        "summary": {
            "probe_count": len(results),
            "passed": status_counts.get("passed", 0),
            "not_passed": len(results) - status_counts.get("passed", 0),
            "status_counts": dict(status_counts),
            "configured_keyed_providers": sorted((name for name in secrets)),
            "source_catalog": "validated",
        },
        "results": results,
    }
    write_json(settings.artifact_dir / "validation_results.json", payload)
    write_json(settings.artifact_dir / "field_catalog.json", catalogs)
    write_json(
        settings.artifact_dir / "plan_alignment.json",
        {
            "schema_version": "1.0",
            "generated_at": finished_at,
            "items": [
                {
                    "probe_id": item["id"],
                    "provider": item["provider"],
                    "status": item["status"],
                    "planned_capabilities": item["capabilities"],
                    "verified": item["status"] == "passed",
                    "missing_fields": item["missing_fields"],
                    "limitation": item["limitation"],
                }
                for item in results
            ],
        },
    )
    return payload
