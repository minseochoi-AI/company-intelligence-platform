"""Compatibility exports. Canonical implementations live in cil_* packages."""

from typing import Any as Any
from typing import Iterable as Iterable
from typing import Mapping as Mapping
from cil_domain.jobs.trends import PostingLifecycle as PostingLifecycle
from cil_domain.jobs.trends import TrendEligibility as TrendEligibility
from cil_domain.jobs.trends import _signature as _signature
from cil_domain.jobs.trends import aggregate_job_trends as aggregate_job_trends
from dataclasses import asdict as asdict
from cil_domain.jobs.trends import build_posting_lifecycle as build_posting_lifecycle
from dataclasses import dataclass as dataclass
from cil_domain.jobs.trends import (
    evaluate_trend_eligibility as evaluate_trend_eligibility,
)
