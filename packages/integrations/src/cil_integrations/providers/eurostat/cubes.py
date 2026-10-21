"""Canonical responsibility owner; migrated from src/company_intel/macro_cubes.py."""

from __future__ import annotations
from cil_contracts.macro import MacroObservation
from typing import Any


class EurostatCubeLoader:
    """Loader for Eurostat Real GDP (nama_10_gdp) chain linked volume series."""

    @staticmethod
    def parse_eurostat_tsv_or_json(
        data: list[dict[str, Any]], country_code: str = "CZ"
    ) -> list[MacroObservation]:
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
            cq = (
                f"CY{period[:4]}-Q{period[-1]}"
                if "-Q" in period or "Q" in period
                else f"CY{period[:4]}-Q1"
            )
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
