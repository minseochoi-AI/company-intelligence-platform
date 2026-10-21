"""Composition root: concrete IO adapters are wired here."""

from cil_integrations.transport.job_links import verify_url_live
from cil_reporting.xlsx.job_links import generate_clickable_hyperlink
from cil_application.ports import RuntimePorts, configure_runtime
from cil_integrations.providers.ares.companies import (
    AresDynamicClient as AresDynamicClient,
)
from cil_integrations.publishing.blogger import BloggerPublisher as BloggerPublisher
from cil_integrations.storage.evidence import EvidenceStore as EvidenceStore
from cil_integrations.transport.http import HttpClient as HttpClient
from cil_integrations.publishing.notion import (
    NotionApprovalQueue as NotionApprovalQueue,
)
from cil_integrations.providers.opendart.master import (
    OpenDartMasterIndex as OpenDartMasterIndex,
)
from cil_integrations.providers.worknet.jobs import (
    WorknetJobConnector as WorknetJobConnector,
)
from cil_integrations.providers.mpsv.jobs import (
    aggregate_by_cz_isco as aggregate_by_cz_isco,
)
from cil_integrations.providers.registry import build_probes as build_probes
from cil_integrations.runtime.settings import configured_secrets as configured_secrets
from cil_integrations.catalog.repository import (
    load_source_catalog as load_source_catalog,
)
from cil_integrations.providers.job_records import (
    normalize_greenhouse_jobs as normalize_greenhouse_jobs,
)
from cil_integrations.providers.job_records import (
    normalize_lever_jobs as normalize_lever_jobs,
)
from cil_integrations.providers.job_records import (
    normalize_mpm_jobs as normalize_mpm_jobs,
)
from cil_integrations.providers.job_records import (
    normalize_mpsv_jobs as normalize_mpsv_jobs,
)
from cil_integrations.providers.job_records import (
    normalize_provider_payloads as normalize_provider_payloads,
)
from cil_reporting.csv.tables import write_csv_tables
from cil_reporting.csv.tables import render_csv_bundle as render_csv_bundle
from cil_reporting.xlsx.tables import render_xlsx_workbook as render_xlsx_workbook
from cil_integrations.providers.mpsv.jobs import (
    stream_mpsv_vacancies as stream_mpsv_vacancies,
)
from cil_integrations.storage.evidence import utc_now as utc_now
from cil_integrations.storage.evidence import write_json as write_json


def configure() -> None:
    configure_runtime(
        RuntimePorts(
            write_csv_tables=write_csv_tables,
            probe_job_url=verify_url_live,
            render_job_hyperlink=generate_clickable_hyperlink,
            AresDynamicClient=AresDynamicClient,
            BloggerPublisher=BloggerPublisher,
            EvidenceStore=EvidenceStore,
            HttpClient=HttpClient,
            NotionApprovalQueue=NotionApprovalQueue,
            OpenDartMasterIndex=OpenDartMasterIndex,
            WorknetJobConnector=WorknetJobConnector,
            aggregate_by_cz_isco=aggregate_by_cz_isco,
            build_probes=build_probes,
            configured_secrets=configured_secrets,
            load_source_catalog=load_source_catalog,
            normalize_greenhouse_jobs=normalize_greenhouse_jobs,
            normalize_lever_jobs=normalize_lever_jobs,
            normalize_mpm_jobs=normalize_mpm_jobs,
            normalize_mpsv_jobs=normalize_mpsv_jobs,
            normalize_provider_payloads=normalize_provider_payloads,
            render_csv_bundle=render_csv_bundle,
            render_xlsx_workbook=render_xlsx_workbook,
            stream_mpsv_vacancies=stream_mpsv_vacancies,
            utc_now=utc_now,
            write_json=write_json,
        )
    )
