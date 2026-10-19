"""Macroeconomic Cube Loader and Cross-National Scenario Integrator.
Implements Decision FMD-D02 for decision campaign cil-cross-national-financial-macro-did-20261019.
"""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class MacroObservation:
    country_code: str
    series_id: str
    series_name: str
    observation_date: str
    calendar_quarter: str
    value: float
    unit: str
    frequency: str = "Q"


class BEACubeLoader:
    """Loader for BEA NIPA Real GDP (Table 1.1.6) and fixed investment series."""

    @staticmethod
    def parse_bea_nipa_table(records: list[dict[str, Any]]) -> list[MacroObservation]:
        observations = []
        for row in records:
            time_period = str(row.get("TimePeriod") or row.get("period") or "")
            data_val = row.get("DataValue") or row.get("value")
            if not time_period or data_val is None:
                continue
            try:
                val = float(str(data_val).replace(",", ""))
            except ValueError:
                continue

            # Convert YYYYQ1 or YYYY-MM to Calendar Quarter
            if "Q" in time_period:
                cq = f"CY{time_period[:4]}-Q{time_period[-1]}"
            else:
                cq = f"CY{time_period[:4]}-Q1"

            observations.append(
                MacroObservation(
                    country_code="US",
                    series_id=str(row.get("SeriesCode") or "NIPA_T10106_A191RX"),
                    series_name=str(row.get("LineDescription") or "Real Gross Domestic Product"),
                    observation_date=time_period,
                    calendar_quarter=cq,
                    value=val,
                    unit=str(row.get("UNIT_MULT") or "Billions of Chained Dollars"),
                    frequency="Q",
                )
            )
        return observations


class EurostatCubeLoader:
    """Loader for Eurostat Real GDP (nama_10_gdp) chain linked volume series."""

    @staticmethod
    def parse_eurostat_tsv_or_json(data: list[dict[str, Any]], country_code: str = "CZ") -> list[MacroObservation]:
        observations = []
        for item in data:
            period = str(item.get("time") or item.get("period") or "")
            val_raw = item.get("values") or item.get("value")
            if not period or val_raw is None:
                continue
            try:
                val = float(val_raw)
            except (ValueError, TypeError):
                continue

            cq = f"CY{period[:4]}-Q{period[-1]}" if "-Q" in period or "Q" in period else f"CY{period[:4]}-Q1"
            observations.append(
                MacroObservation(
                    country_code=country_code,
                    series_id="nama_10_gdp_CLV10_MEUR",
                    series_name="Gross domestic product at market prices (chain linked)",
                    observation_date=period,
                    calendar_quarter=cq,
                    value=val,
                    unit="Million EUR",
                    frequency="Q",
                )
            )
        return observations


class MacroCubeManager:
    """Manages cross-national macro cubes and provides benchmark rates & GDP trends."""

    def __init__(self, initial_observations: list[MacroObservation] | None = None) -> None:
        self._observations: list[MacroObservation] = initial_observations or []

    def add_observations(self, obs: list[MacroObservation]) -> None:
        self._observations.extend(obs)

    def get_latest_base_rate(self, country_code: str = "KR") -> float:
        """Return latest available central bank base rate or default baseline."""
        country = country_code.upper()
        # Benchmark fallbacks grounded in 2026/2025 actual rates:
        # KR: BOK 3.25%, US: Fed 4.50%, CZ: CNB 4.00%
        defaults = {"KR": 0.0325, "US": 0.0450, "CZ": 0.0400}
        
        rates = [
            o.value for o in self._observations
            if o.country_code == country and "rate" in o.series_id.lower()
        ]
        return rates[-1] if rates else defaults.get(country, 0.035)

    def get_real_gdp_growth(self, country_code: str = "KR") -> float:
        """Compute latest YoY or QoQ Real GDP growth rate."""
        country = country_code.upper()
        gdps = [
            o.value for o in self._observations
            if o.country_code == country and ("gdp" in o.series_id.lower() or "10106" in o.series_id)
        ]
        if len(gdps) >= 2:
            return (gdps[-1] / gdps[-2]) - 1.0
        # Default baseline growth: KR 2.2%, US 2.5%, CZ 1.8%
        defaults = {"KR": 0.022, "US": 0.025, "CZ": 0.018}
        return defaults.get(country, 0.02)
