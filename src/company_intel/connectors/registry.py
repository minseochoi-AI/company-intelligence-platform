from __future__ import annotations

from ..config import Settings
from ..models import Probe
from .keyed import keyed_probes
from .keyless import keyless_probes


def build_probes(settings: Settings, provider_filter: set[str] | None = None) -> list[Probe]:
    probes = keyed_probes() + keyless_probes(settings.sec_user_agent)
    if not provider_filter or "all" in provider_filter:
        return probes
    return [probe for probe in probes if probe.provider in provider_filter or probe.id in provider_filter]
