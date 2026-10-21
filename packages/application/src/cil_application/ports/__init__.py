"""Injected IO operations. Applications configure these at their boundary."""

from dataclasses import dataclass
from contextvars import ContextVar
from typing import Any, Callable


@dataclass(frozen=True)
class RuntimePorts:
    AresDynamicClient: Callable[..., Any]
    BloggerPublisher: Callable[..., Any]
    EvidenceStore: Callable[..., Any]
    HttpClient: Callable[..., Any]
    NotionApprovalQueue: Callable[..., Any]
    OpenDartMasterIndex: Callable[..., Any]
    WorknetJobConnector: Callable[..., Any]
    aggregate_by_cz_isco: Callable[..., Any]
    build_probes: Callable[..., Any]
    configured_secrets: Callable[..., Any]
    load_source_catalog: Callable[..., Any]
    normalize_greenhouse_jobs: Callable[..., Any]
    normalize_lever_jobs: Callable[..., Any]
    normalize_mpm_jobs: Callable[..., Any]
    normalize_mpsv_jobs: Callable[..., Any]
    normalize_provider_payloads: Callable[..., Any]
    render_csv_bundle: Callable[..., Any]
    render_xlsx_workbook: Callable[..., Any]
    stream_mpsv_vacancies: Callable[..., Any]
    utc_now: Callable[..., Any]
    write_json: Callable[..., Any]

    write_csv_tables: Callable[..., Any] | None = None
    probe_job_url: Callable[..., Any] | None = None
    render_job_hyperlink: Callable[..., Any] | None = None


_active: ContextVar[RuntimePorts | None] = ContextVar("cil_runtime_ports", default=None)


def configure_runtime(ports: RuntimePorts) -> None:
    _active.set(ports)


def current_runtime() -> RuntimePorts:
    value = _active.get()
    if value is None:
        raise RuntimeError(
            "RuntimePorts must be supplied by the application composition root"
        )
    return value


def AresDynamicClient(*args: Any, **kwargs: Any) -> Any:
    return current_runtime().AresDynamicClient(*args, **kwargs)


def BloggerPublisher(*args: Any, **kwargs: Any) -> Any:
    return current_runtime().BloggerPublisher(*args, **kwargs)


def EvidenceStore(*args: Any, **kwargs: Any) -> Any:
    return current_runtime().EvidenceStore(*args, **kwargs)


def HttpClient(*args: Any, **kwargs: Any) -> Any:
    return current_runtime().HttpClient(*args, **kwargs)


def NotionApprovalQueue(*args: Any, **kwargs: Any) -> Any:
    return current_runtime().NotionApprovalQueue(*args, **kwargs)


def OpenDartMasterIndex(*args: Any, **kwargs: Any) -> Any:
    return current_runtime().OpenDartMasterIndex(*args, **kwargs)


def WorknetJobConnector(*args: Any, **kwargs: Any) -> Any:
    return current_runtime().WorknetJobConnector(*args, **kwargs)


def aggregate_by_cz_isco(*args: Any, **kwargs: Any) -> Any:
    return current_runtime().aggregate_by_cz_isco(*args, **kwargs)


def build_probes(*args: Any, **kwargs: Any) -> Any:
    return current_runtime().build_probes(*args, **kwargs)


def configured_secrets(*args: Any, **kwargs: Any) -> Any:
    return current_runtime().configured_secrets(*args, **kwargs)


def load_source_catalog(*args: Any, **kwargs: Any) -> Any:
    return current_runtime().load_source_catalog(*args, **kwargs)


def normalize_greenhouse_jobs(*args: Any, **kwargs: Any) -> Any:
    return current_runtime().normalize_greenhouse_jobs(*args, **kwargs)


def normalize_lever_jobs(*args: Any, **kwargs: Any) -> Any:
    return current_runtime().normalize_lever_jobs(*args, **kwargs)


def normalize_mpm_jobs(*args: Any, **kwargs: Any) -> Any:
    return current_runtime().normalize_mpm_jobs(*args, **kwargs)


def normalize_mpsv_jobs(*args: Any, **kwargs: Any) -> Any:
    return current_runtime().normalize_mpsv_jobs(*args, **kwargs)


def normalize_provider_payloads(*args: Any, **kwargs: Any) -> Any:
    return current_runtime().normalize_provider_payloads(*args, **kwargs)


def render_csv_bundle(*args: Any, **kwargs: Any) -> Any:
    return current_runtime().render_csv_bundle(*args, **kwargs)


def render_xlsx_workbook(*args: Any, **kwargs: Any) -> Any:
    return current_runtime().render_xlsx_workbook(*args, **kwargs)


def stream_mpsv_vacancies(*args: Any, **kwargs: Any) -> Any:
    return current_runtime().stream_mpsv_vacancies(*args, **kwargs)


def utc_now(*args: Any, **kwargs: Any) -> Any:
    return current_runtime().utc_now(*args, **kwargs)


def write_json(*args: Any, **kwargs: Any) -> Any:
    return current_runtime().write_json(*args, **kwargs)


def probe_job_url(*args: Any, **kwargs: Any) -> Any:
    operation = current_runtime().probe_job_url
    if operation is None:
        raise RuntimeError("Live URL probe was not configured")
    return operation(*args, **kwargs)


def render_job_hyperlink(*args: Any, **kwargs: Any) -> Any:
    operation = current_runtime().render_job_hyperlink
    if operation is None:
        raise RuntimeError("Job hyperlink renderer was not configured")
    return operation(*args, **kwargs)


def write_csv_tables(*args: Any, **kwargs: Any) -> Any:
    operation = current_runtime().write_csv_tables
    if operation is None:
        raise RuntimeError("CSV writer was not configured")
    return operation(*args, **kwargs)
