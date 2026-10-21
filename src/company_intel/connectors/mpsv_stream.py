"""Compatibility exports. Canonical implementations live in cil_* packages."""

from typing import Any as Any
from cil_integrations.providers.mpsv.jobs import (
    CURATED_MPSV_FIXTURE as CURATED_MPSV_FIXTURE,
)
from typing import Iterable as Iterable
from typing import Iterator as Iterator
from pathlib import Path as Path
from cil_integrations.providers.mpsv.jobs import (
    aggregate_by_cz_isco as aggregate_by_cz_isco,
)
from collections import defaultdict as defaultdict
from cil_integrations.providers.job_records import (
    normalize_mpsv_jobs as normalize_mpsv_jobs,
)
from cil_integrations.providers.mpsv.jobs import (
    stream_mpsv_vacancies as stream_mpsv_vacancies,
)
