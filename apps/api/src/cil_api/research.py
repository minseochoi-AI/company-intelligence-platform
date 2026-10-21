"""HTTP composition root; paths are server-controlled and provider refresh is off."""

from __future__ import annotations
import os
import re
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict
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

router = APIRouter(prefix="/research", tags=["research"])


class ResearchBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    request: dict
    snapshot: dict


class ReportBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    manifest_sha256: str
    narrative: str
    claims: dict


def _store(run_id: str) -> ResearchArtifactStore:
    if not re.fullmatch(r"run-[0-9a-f]{24}", run_id):
        raise ValueError("invalid run identity")
    root = Path(os.environ.get("CIL_RESEARCH_ARTIFACT_ROOT", "artifacts/research"))
    return ResearchArtifactStore(root / run_id)


@router.post("/validate")
def validate(body: ResearchBody):
    try:
        return compile_request(
            ReportRequest.from_dict(body.request),
            body.snapshot,
            CapabilityRegistry.from_source_catalog(load_source_catalog()),
        )
    except (ValueError, TypeError) as error:
        raise HTTPException(422, str(error)) from error


@router.post("/runs")
def run(body: ResearchBody):
    try:
        request = ReportRequest.from_dict(body.request)
        return run_research(
            request,
            body.snapshot,
            CapabilityRegistry.from_source_catalog(load_source_catalog()),
            _store(run_identity(request, body.snapshot)),
            renderer=render_research_workbook,
        )
    except (ValueError, TypeError, KeyError) as error:
        raise HTTPException(422, str(error)) from error
    except FileExistsError as error:
        raise HTTPException(409, "immutable research run already differs") from error


@router.post("/runs/{run_id}/reports")
def report(run_id: str, body: ReportBody):
    try:
        return seal_report(
            _store(run_id), body.manifest_sha256, body.narrative, body.claims
        )
    except FileNotFoundError as error:
        raise HTTPException(404, "research run missing") from error
    except (ValueError, TypeError, KeyError) as error:
        raise HTTPException(422, str(error)) from error
