"""Canonical responsibility owner; migrated from src/company_intel/cli.py."""

from __future__ import annotations
from cil_application.providers.capabilities import BASELINE_API_CATALOG
from cil_application.providers.capabilities import get_cluster_baseline_spec_text
from cil_application.providers.capabilities import resolve_active_providers
from cil_contracts.jobs import CanonicalJobRecord
from cil_contracts.reports import DynamicColumnSpec
from cil_domain.clusters.signature import ClusterSignature
from cil_application.jobs.provenance import JobProvenanceVerifier
from cil_integrations.providers.job_records import from_cz_mpsv_job_record
from cil_integrations.providers.job_records import from_kr_public_job_record
from cil_integrations.providers.job_records import from_sk_upsvar_record
from cil_integrations.providers.job_schema import JobSchemaContract
from cil_integrations.runtime.settings import Settings
from cil_reporting.schema.compiler import DynamicReportSchemaCompiler
from pathlib import Path
from typing import Any, ClassVar
import csv
import datetime
import json


def _job_verdict_counts(frames: Any) -> dict[str, int]:
    return {
        "matched": len(frames.jobs),
        "strict_matches": len(frames.strict_matches),
        "unverifiable": len(frames.unverifiable_candidates),
        "no_match": len(frames.no_matches),
        "conflict": len(frames.conflicts),
    }


def _export_cluster_jobs(args: Any, settings: Settings) -> int:
    """Compatibility entrypoint for the common saved-evidence request pipeline."""
    from cil_contracts.requests import ReportRequest, content_hash
    from cil_application.research.report_service import run_identity, run_research
    from cil_integrations.research.capability_registry import CapabilityRegistry
    from cil_integrations.storage.evidence import ResearchArtifactStore
    from cil_reporting.research_workbook import render_research_workbook

    snapshot_path = getattr(args, "snapshot", None)
    as_of = getattr(args, "as_of", None)
    if not snapshot_path or not as_of:
        print(
            json.dumps(
                {
                    "status": "NEEDS_INPUT",
                    "required": ["--snapshot", "--as-of"],
                    "reason": "Historical CSV and demo fixtures are not current evidence.",
                },
                ensure_ascii=False,
            )
        )
        return 2
    if getattr(args, "degree", "all") != "all" or getattr(args, "verify_links", False):
        print(
            json.dumps(
                {
                    "status": "NEEDS_INPUT",
                    "reason": "Use research request requirement_policy/profile_ref for eligibility. Live probing is a separate explicit operation.",
                }
            )
        )
        return 2
    try:
        snapshot_path = Path(snapshot_path)
        if not snapshot_path.is_absolute():
            snapshot_path = settings.project_root / snapshot_path
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
        signature = (
            getattr(args, "signature", None)
            or ClusterSignature(
                region=getattr(args, "country", "ALL") or "ALL",
                sector=getattr(args, "sector", "ALL") or "ALL",
                contract=getattr(args, "contract", "ALL") or "ALL",
            ).key
        )
        ClusterSignature.parse(signature)
        refs = [
            {key: row[key] for key in ("provider_id", "posting_id", "revision")}
            for row in snapshot.get("postings", [])
        ]
        options = {}
        if getattr(args, "dynamic_attributes", None):
            columns = [
                x.strip() for x in args.dynamic_attributes.split(",") if x.strip()
            ]
            options["report_spec"] = {"columns": {"Postings": ["posting_id", *columns]}}
        request = ReportRequest.from_dict(
            {
                "purpose": ["selected-posting"],
                "question": "선택한 저장 스냅샷의 클러스터 공고 비교",
                "subject_refs": refs,
                "cohort_signature": signature,
                "as_of": as_of,
                "argument_origins": [
                    {"json_pointer": "/purpose", "origin": "policy_default"},
                    {"json_pointer": "/question", "origin": "policy_default"},
                    {
                        "json_pointer": "/subject_refs",
                        "origin": "source_derived",
                        "evidence_ref": "snapshot:" + content_hash(snapshot),
                    },
                    {"json_pointer": "/cohort_signature", "origin": "user_explicit"},
                    {"json_pointer": "/as_of", "origin": "user_explicit"},
                    *(
                        [{"json_pointer": "/report_spec", "origin": "user_explicit"}]
                        if options
                        else []
                    ),
                ],
                **options,
            }
        )
        output = Path(getattr(args, "output", "cluster_jobs_export.xlsx"))
        if not output.is_absolute():
            output = settings.project_root / output
        store = ResearchArtifactStore(
            output.parent / (output.stem + ".bundle") / run_identity(request, snapshot)
        )
        result = run_research(
            request,
            snapshot,
            CapabilityRegistry(),
            store,
            renderer=render_research_workbook,
        )
        if result["status"] in {"NEEDS_INPUT", "NEEDS_EVIDENCE"}:
            print(json.dumps(result, ensure_ascii=False))
            return 2
        destination = ResearchArtifactStore(output.parent)
        destination.write(output.name, store.read("research.xlsx"))
        result["total_matched"] = result["dataset_rows"]["Postings"]
        result["output"] = str(output)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (ValueError, TypeError, KeyError, OSError) as error:
        print(json.dumps({"status": "ERROR", "error": str(error)}, ensure_ascii=False))
        return 2


def _get_slovak_benchmark_postings() -> list[dict[str, Any]]:
    return [
        {
            "id": "SK-UPSVAR-2026-001",
            "employer": "Železnice Slovenskej republiky (ŽSR)",
            "ico": "31364501",
            "legal_form": "Štátny podnik",
            "entity_type": "국영 철도공기업",
            "title": "Správca IT infraštruktúry a počítačových sietí",
            "isco": "25220",
            "edu": "bakal",
            "sal_min": 1600,
            "sal_max": 2200,
            "curr": "EUR",
            "korean_role": "공기업 전산직 ICT 인프라·전산망 운영",
            "loc": "Bratislava (SK010)",
            "url": "https://sluzbyzamestnanosti.gov.sk/pozicia/SK-UPSVAR-2026-001",
            "desc": "Železničná IT infraštruktúra, správa LAN/WAN sietí.",
            "grad": False,
            "closing_at": "2026-11-30",
        },
        {
            "id": "SK-UPSVAR-2026-002",
            "employer": "Slovenská pošta, a.s.",
            "ico": "36631124",
            "legal_form": "Akciová spoločnosť",
            "entity_type": "국영 우정공기업",
            "title": "Systémový administrátor Linux/Windows",
            "isco": "25220",
            "edu": "usoSMat",
            "sal_min": 1500,
            "sal_max": 1950,
            "curr": "EUR",
            "korean_role": "공기업 시스템 엔지니어링 및 서버 운영",
            "loc": "Bratislava (SK010)",
            "url": "https://sluzbyzamestnanosti.gov.sk/pozicia/SK-UPSVAR-2026-002",
            "desc": "Správa a monitoring poštových IT systémov.",
            "grad": False,
            "closing_at": "2026-11-20",
        },
        {
            "id": "SK-UPSVAR-2026-003",
            "employer": "Národná agentúra pre sieťové a elektronické služby (NASES)",
            "ico": "42156424",
            "legal_form": "Príspevková organizácia",
            "entity_type": "국가전자서비스청",
            "title": "DevOps špecialista pre vládny cloud",
            "isco": "25140",
            "edu": "bakal",
            "sal_min": 1900,
            "sal_max": 2600,
            "curr": "EUR",
            "korean_role": "공공 클라우드 인프라 운영 및 CI/CD 자동화",
            "loc": "Bratislava (SK010)",
            "url": "https://sluzbyzamestnanosti.gov.sk/pozicia/SK-UPSVAR-2026-003",
            "desc": "Správa vládneho cloudu a portálu slovensko.sk.",
            "grad": False,
            "closing_at": "2026-12-15",
        },
        {
            "id": "SK-UPSVAR-2026-005",
            "employer": "Slovenský plynárenský priemysel, a.s. (SPP)",
            "ico": "35815256",
            "legal_form": "Akciová spoločnosť",
            "entity_type": "국영 에너지공기업",
            "title": "Dátový analytik pre trh s energiami",
            "isco": "24130",
            "edu": "bakal",
            "sal_min": 1800,
            "sal_max": 2500,
            "curr": "EUR",
            "korean_role": "공기업 에너지 시장 데이터 분석",
            "loc": "Bratislava (SK010)",
            "url": "https://sluzbyzamestnanosti.gov.sk/pozicia/SK-UPSVAR-2026-005",
            "desc": "Analýza dát o spotrebe plynu, modelovanie trhových rizík.",
            "grad": False,
            "closing_at": "2026-12-31",
        },
        {
            "id": "SK-UPSVAR-RD-001",
            "employer": "Slovenská akadémia vied - Ústav informatiky (SAV)",
            "ico": "00166651",
            "legal_form": "Verejná výskumná inštitúcia",
            "entity_type": "국립 과학원 연구기관",
            "title": "Vedecký pracovník v oblasti umelej inteligencie a dátovej vedy",
            "isco": "12231",
            "edu": "doktor",
            "sal_min": 2200,
            "sal_max": 3200,
            "curr": "EUR",
            "korean_role": "국립연구소 인공지능/빅데이터 선임연구원",
            "loc": "Bratislava (SK010)",
            "url": "https://sluzbyzamestnanosti.gov.sk/pozicia/SK-UPSVAR-RD-001",
            "desc": "Výskum v oblasti strojového učenia, analýzy veľkých dát.",
            "grad": True,
            "closing_at": "2026-12-31",
        },
    ]
