"""Compatibility exports. Canonical implementations live in cil_* packages."""

from typing import Any as Any
from cil_cli.interactive import ArrowMenu as ArrowMenu
from cil_application.providers.capabilities import (
    BASELINE_API_CATALOG as BASELINE_API_CATALOG,
)
from cil_cli.guides import COMMAND_GUIDES as COMMAND_GUIDES
from cil_contracts.jobs import CanonicalJobRecord as CanonicalJobRecord
from typing import ClassVar as ClassVar
from cil_domain.clusters.signature import ClusterSignature as ClusterSignature
from cil_contracts.reports import DynamicColumnSpec as DynamicColumnSpec
from cil_reporting.schema.compiler import (
    DynamicReportSchemaCompiler as DynamicReportSchemaCompiler,
)
from cil_application.jobs.provenance import (
    JobProvenanceVerifier as JobProvenanceVerifier,
)
from cil_integrations.providers.job_schema import JobSchemaContract as JobSchemaContract
from cil_contracts.jobs import JobSearchProfile as JobSearchProfile
from cil_cli.parser import KoreanArgumentParser as KoreanArgumentParser
from cil_cli.parser import KoreanHelpFormatter as KoreanHelpFormatter
from pathlib import Path as Path
from cil_domain.companies.screening import ScreenerProfile as ScreenerProfile
from cil_contracts.facts import SearchProfile as SearchProfile
from cil_integrations.runtime.settings import Settings as Settings
from cil_integrations.storage.duckdb.repository import Warehouse as Warehouse
from cil_cli.parser import _add_command as _add_command
from cil_cli.parser import _add_help as _add_help
from cil_cli.parser import _add_option as _add_option
from cil_cli.commands.providers import _cluster_spec as _cluster_spec
from cil_cli.main import _demo as _demo
from cil_cli.commands.jobs import _export_cluster_jobs as _export_cluster_jobs
from cil_cli.main import (
    _get_slovak_benchmark_postings as _get_slovak_benchmark_postings,
)
from cil_cli.commands.jobs import _job_verdict_counts as _job_verdict_counts
from cil_cli.commands.providers import _list_api_attributes as _list_api_attributes
from cil_cli.main import _records as _records
from cil_cli.main import _supplied_table_rows as _supplied_table_rows
from cil_application.analysis.pipeline import actual_analysis as actual_analysis
from cil_application.analysis.service import (
    build_company_timeline as build_company_timeline,
)
from cil_application.reports.build_data import (
    build_export_bundle as build_export_bundle,
)
from cil_cli.interactive import build_interactive_request as build_interactive_request
from cil_domain.queries.facets import build_job_facets as build_job_facets
from cil_domain.provenance.manifests import build_run_manifest as build_run_manifest
from cil_cli.guides import command_epilog as command_epilog
from cil_cli.guides import command_key as command_key
from cil_contracts.query import (
    company_search_profile_from_mapping as company_search_profile_from_mapping,
)
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
from cil_application.jobs.current import (
    execute_current_job_search as execute_current_job_search,
)
from cil_domain.companies.search import (
    explain_company_evaluation as explain_company_evaluation,
)
from cil_domain.finance.analytics import financial_metrics as financial_metrics
from cil_integrations.providers.job_records import (
    from_cz_mpsv_job_record as from_cz_mpsv_job_record,
)
from cil_integrations.providers.job_records import (
    from_kr_public_job_record as from_kr_public_job_record,
)
from cil_integrations.providers.job_records import (
    from_sk_upsvar_record as from_sk_upsvar_record,
)
from cil_domain.finance.analytics import future_value_score as future_value_score
from cil_application.providers.capabilities import (
    get_cluster_baseline_spec_text as get_cluster_baseline_spec_text,
)
from cil_cli.guides import guide_payload as guide_payload
from cil_domain.finance.analytics import hiring_change as hiring_change
from cil_cli.guides import korean_option as korean_option
from cil_cli.interactive import load_scripted_selector as load_scripted_selector
from cil_domain.finance.analytics import macro_sensitivity as macro_sensitivity
from cil_cli.main import main as main
from cil_integrations.providers.job_records import (
    normalize_provider_payloads as normalize_provider_payloads,
)
from cil_domain.companies.search import (
    rank_candidate_evaluations as rank_candidate_evaluations,
)
from cil_domain.companies.search import rank_candidates as rank_candidates
from cil_domain.finance.analytics import rank_companies as rank_companies
from cil_application.selection.replay import replay_selection as replay_selection
from cil_application.providers.capabilities import (
    resolve_active_providers as resolve_active_providers,
)
from cil_domain.provenance.manifests import result_refs as result_refs
from cil_domain.companies.screening import screen_companies as screen_companies
from cil_application.jobs.search import search_job_dataframes as search_job_dataframes
from cil_domain.provenance.snapshots import snapshot_freshness as snapshot_freshness
from cil_integrations.providers.registry import source_health as source_health
from cil_application.validation.providers import validate as validate
from cil_domain.companies.search import (
    validate_search_profile as validate_search_profile,
)
from cil_domain.finance.analytics import (
    valuation_prerequisites as valuation_prerequisites,
)
from cil_domain.provenance.selection import verify_run_chain as verify_run_chain
from cil_cli.interactive import write_interactive_profile as write_interactive_profile
from cil_integrations.storage.evidence import write_json as write_json
from cil_integrations.storage.manifests import write_run_manifest as write_run_manifest
from cil_reporting.text.summaries import (
    write_validation_report as write_validation_report,
)

if __name__ == "__main__":
    raise SystemExit(main())
