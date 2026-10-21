"""Compatibility exports. Canonical implementations live in cil_* packages."""

from typing import Any as Any
from cil_application.jobs.search import EXCLUSION_COLUMNS as EXCLUSION_COLUMNS
from cil_contracts.query import FilterVerdict as FilterVerdict
from html.parser import HTMLParser as HTMLParser
from cil_application.jobs.search import JOB_COLUMNS as JOB_COLUMNS
from cil_application.jobs.search import JobDataFrames as JobDataFrames
from cil_contracts.jobs import JobSearchProfile as JobSearchProfile
from cil_application.jobs.search import LANGUAGES as LANGUAGES
from cil_application.jobs.search import LOCATION_COLUMNS as LOCATION_COLUMNS
from cil_application.jobs.search import NORMALIZERS as NORMALIZERS
from cil_application.jobs.search import OVERLAP_COLUMNS as OVERLAP_COLUMNS
from pathlib import Path as Path
from cil_application.jobs.search import REQUIREMENT_COLUMNS as REQUIREMENT_COLUMNS
from cil_application.jobs.search import SKILLS as SKILLS
from cil_application.jobs.search import SOURCE_COLUMNS as SOURCE_COLUMNS
from datetime import UTC as UTC
from cil_contracts.query import UnknownPolicy as UnknownPolicy
from cil_application.jobs.search import VERDICT_COLUMNS as VERDICT_COLUMNS
from cil_integrations.providers.job_records import _ListTextParser as _ListTextParser
from cil_domain.jobs.filters import _active_at as _active_at
from cil_integrations.providers.job_records import (
    _atomic_requirements as _atomic_requirements,
)
from cil_domain.jobs.filters import _contains as _contains
from cil_domain.jobs.filters import _contains_verdict as _contains_verdict
from cil_integrations.providers.job_records import (
    _country_from_location as _country_from_location,
)
from cil_integrations.providers.job_records import _employment as _employment
from cil_integrations.providers.job_records import _html_parts as _html_parts
from cil_domain.jobs.filters import _language_verdict as _language_verdict
from cil_domain.jobs.filters import _membership_verdict as _membership_verdict
from cil_integrations.providers.job_records import _mpsv_location as _mpsv_location
from cil_integrations.providers.job_records import (
    _mpsv_salary_period as _mpsv_salary_period,
)
from cil_integrations.providers.job_records import _necessity as _necessity
from cil_domain.jobs.filters import _reason_for as _reason_for
from cil_domain.jobs.filters import _record_verdict as _record_verdict
from cil_integrations.providers.job_records import _records as _records
from cil_domain.jobs.filters import _requirement_matches as _requirement_matches
from cil_domain.jobs.filters import _requirement_verdict as _requirement_verdict
from cil_domain.jobs.filters import (
    _salary_signature_verdict as _salary_signature_verdict,
)
from cil_integrations.providers.job_records import _snapshot as _snapshot
from cil_domain.jobs.filters import _validate_profile as _validate_profile
from cil_integrations.providers.job_records import _value as _value
from cil_integrations.providers.job_records import _workplace as _workplace
from cil_domain.jobs.filters import active_as_of as active_as_of
from cil_application.jobs.search import build_denominators as build_denominators
from dataclasses import dataclass as dataclass
from datetime import datetime as datetime
from dataclasses import field as field
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
from cil_domain.taxonomy.facts import resolve_title_to_isco as resolve_title_to_isco
from cil_application.jobs.search import search_job_dataframes as search_job_dataframes
from cil_contracts.query import text_verdict as text_verdict
from urllib.parse import urlparse as urlparse
