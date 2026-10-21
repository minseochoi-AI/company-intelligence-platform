"""Compatibility exports. Canonical implementations live in cil_* packages."""

from cil_api.schemas import AiEventEvidenceRequest as AiEventEvidenceRequest
from typing import Any as Any
from pydantic import BaseModel as BaseModel
from cil_api.schemas import CurrentJobRequest as CurrentJobRequest
from cil_api.schemas import DcfRequest as DcfRequest
from cil_api.schemas import DidRequest as DidRequest
from cil_api.schemas import EventStudyRequest as EventStudyRequest
from cil_api.schemas import EvidenceTimelineRequest as EvidenceTimelineRequest
from cil_api.schemas import ExportRequest as ExportRequest
from fastapi import FastAPI as FastAPI
from pydantic import Field as Field
from cil_api.schemas import FutureScoreRequest as FutureScoreRequest
from fastapi import HTTPException as HTTPException
from cil_contracts.jobs import JobSearchProfile as JobSearchProfile
from cil_api.schemas import JobSearchRequest as JobSearchRequest
from cil_api.schemas import JobTrendRequest as JobTrendRequest
from pathlib import Path as Path
from cil_api.schemas import RankingRequest as RankingRequest
from cil_domain.companies.screening import ScreenerProfile as ScreenerProfile
from cil_api.schemas import ScreenerRequest as ScreenerRequest
from cil_api.schemas import SearchProfileRequest as SearchProfileRequest
from cil_api.schemas import SelectionRunRequest as SelectionRunRequest
from cil_api.schemas import SelectionRunResponse as SelectionRunResponse
from cil_integrations.runtime.settings import Settings as Settings
from datetime import UTC as UTC
from cil_api.schemas import ValuationEvidenceRequest as ValuationEvidenceRequest
from cil_integrations.storage.duckdb.repository import Warehouse as Warehouse
from cil_api.routes.analysis import ai_event_analysis as ai_event_analysis
from cil_api.app import app as app
from cil_domain.provenance.selection import bind_selection_run as bind_selection_run
from cil_application.analysis.service import (
    build_company_timeline as build_company_timeline,
)
from cil_application.reports.build_data import (
    build_export_bundle as build_export_bundle,
)
from cil_domain.queries.facets import build_job_facets as build_job_facets
from cil_domain.provenance.manifests import build_run_manifest as build_run_manifest
from cil_api.routes.analysis import calculate_dcf as calculate_dcf
from cil_api.routes.analysis import calculate_did as calculate_did
from cil_api.routes.analysis import calculate_event_study as calculate_event_study
from cil_api.routes.analysis import calculate_future_score as calculate_future_score
from cil_api.routes.companies import company_capabilities as company_capabilities
from cil_api.routes.companies import company_screener as company_screener
from cil_api.routes.companies import company_search as company_search
from cil_contracts.query import (
    company_search_profile_from_mapping as company_search_profile_from_mapping,
)
from cil_api.routes.companies import company_timeline as company_timeline
from cil_api.routes.reports import create_export as create_export
from cil_api.routes.jobs import current_jobs as current_jobs
from datetime import datetime as datetime
from cil_domain.finance.analytics import dcf_scenarios as dcf_scenarios
from cil_domain.finance.analytics import (
    difference_in_differences as difference_in_differences,
)
from cil_application.analysis.service import evaluate_ai_event as evaluate_ai_event
from cil_application.analysis.service import evaluate_job_trends as evaluate_job_trends
from cil_application.analysis.service import (
    evaluate_valuation_scenarios as evaluate_valuation_scenarios,
)
from cil_domain.finance.analytics import event_study as event_study
from cil_domain.finance.analytics import (
    event_study_prerequisites as event_study_prerequisites,
)
from cil_api.routes.analysis import evidence_timeline as evidence_timeline
from cil_application.jobs.current import (
    execute_current_job_search as execute_current_job_search,
)
from cil_domain.companies.search import (
    explain_company_evaluation as explain_company_evaluation,
)
from cil_api.routes.reports import export_metadata as export_metadata
from cil_domain.finance.analytics import future_value_score as future_value_score
from cil_api.routes.health import health as health
from cil_api.routes.jobs import job_requirements as job_requirements
from cil_api.routes.jobs import job_search as job_search
from cil_api.routes.jobs import job_trends as job_trends
from cil_api.routes.health import latest_validation as latest_validation
from cil_integrations.providers.job_records import (
    normalize_provider_payloads as normalize_provider_payloads,
)
from cil_domain.companies.search import (
    rank_candidate_evaluations as rank_candidate_evaluations,
)
from cil_domain.companies.search import rank_candidates as rank_candidates
from cil_domain.finance.analytics import rank_companies as rank_companies
from cil_api.routes.analysis import rankings as rankings
from cil_api.routes.runs import replay_run as replay_run
from cil_domain.provenance.manifests import result_refs as result_refs
from cil_domain.companies.screening import screen_companies as screen_companies
from cil_application.jobs.search import search_job_dataframes as search_job_dataframes
from cil_api.routes.runs import selection_run as selection_run
from uuid import uuid4 as uuid4
from cil_domain.companies.search import (
    validate_search_profile as validate_search_profile,
)
from cil_domain.finance.analytics import (
    valuation_prerequisites as valuation_prerequisites,
)
from cil_api.routes.analysis import valuation_scenarios as valuation_scenarios
from cil_domain.provenance.selection import verify_run_chain as verify_run_chain
