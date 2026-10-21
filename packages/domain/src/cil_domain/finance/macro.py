"""Canonical responsibility owner; migrated from src/company_intel/macro_cubes.py."""

from __future__ import annotations
from cil_contracts.macro import MacroObservation


class MacroCubeManager:
    """Manages cross-national macro cubes and provides benchmark rates & GDP trends."""

    def __init__(
        self, initial_observations: list[MacroObservation] | None = None
    ) -> None:
        self._observations: list[MacroObservation] = initial_observations or []

    def add_observations(self, obs: list[MacroObservation]) -> None:
        self._observations.extend(obs)

    def get_latest_base_rate(
        self, country_code: str = "KR", *, series_id: str | None = None
    ) -> float | None:
        """Return an unambiguous latest rate in decimal units, or unknown."""
        country = country_code.upper()
        rates = [
            o
            for o in self._observations
            if o.country_code == country
            and (
                o.series_id == series_id if series_id else "rate" in o.series_id.lower()
            )
        ]
        if not rates or len({o.series_id for o in rates}) != 1:
            return None
        latest_date = max(o.observation_date for o in rates)
        latest = [o for o in rates if o.observation_date == latest_date]
        values = {
            o.value / 100
            if o.unit.lower() in {"percent", "%", "percentage"}
            else o.value
            if o.unit.lower() in {"ratio", "decimal"}
            else None
            for o in latest
        }
        return values.pop() if len(values) == 1 else None

    def get_real_gdp_growth(
        self, country_code: str = "KR", *, series_id: str | None = None
    ) -> float | None:
        """Compute latest YoY or QoQ Real GDP growth rate."""
        country = country_code.upper()
        gdps = [
            o
            for o in self._observations
            if o.country_code == country
            and (
                o.series_id == series_id
                if series_id
                else (
                    "gdp" in (o.series_id + " " + o.series_name).lower()
                    or "gross domestic product" in o.series_name.lower()
                )
                or "10106" in o.series_id
            )
        ]
        if not gdps or len({(o.series_id, o.unit, o.frequency) for o in gdps}) != 1:
            return None
        gdps = sorted(gdps, key=lambda o: o.observation_date)
        if len(gdps) >= 2:
            if (
                gdps[-1].observation_date == gdps[-2].observation_date
                or gdps[-2].value <= 0
            ):
                return None
            return gdps[-1].value / gdps[-2].value - 1.0
        return None
