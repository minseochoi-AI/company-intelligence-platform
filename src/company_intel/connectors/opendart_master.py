"""Compatibility exports. Canonical implementations live in cil_* packages."""

from typing import Any as Any
from cil_integrations.providers.opendart.master import (
    DEFAULT_CURATED_COMPANIES as DEFAULT_CURATED_COMPANIES,
)
from cil_integrations.providers.opendart.master import (
    OpenDartMasterIndex as OpenDartMasterIndex,
)
from pathlib import Path as Path
from cil_integrations.providers.opendart.master import _global_index as _global_index
from dataclasses import dataclass as dataclass
from cil_integrations.providers.opendart.master import (
    get_master_index as get_master_index,
)
from cil_integrations.providers.opendart.master import (
    resolve_corp_code as resolve_corp_code,
)
from cil_integrations.providers.opendart.master import (
    search_kr_companies as search_kr_companies,
)
