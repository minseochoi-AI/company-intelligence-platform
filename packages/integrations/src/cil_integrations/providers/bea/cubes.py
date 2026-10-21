"""Canonical responsibility owner; migrated from src/company_intel/connectors/keyed.py, src/company_intel/macro_cubes.py."""

from __future__ import annotations
from cil_contracts.macro import MacroObservation
from cil_domain.providers.parsing import json_payload
from cil_domain.providers.parsing import preserve_payload
from cil_domain.providers.parsing import to_number
from typing import Any
from typing import Any, Callable, Mapping


def _bea(body: bytes, _: str) -> dict[str, Any]:
    data = json_payload(body).get("BEAAPI", {})
    results = data.get("Results", {})
    datasets = results.get("Dataset", [])
    return {
        "dataset_count": len(datasets),
        "datasets": [
            {
                "name": row.get("DatasetName"),
                "description": row.get("DatasetDescription"),
            }
            for row in datasets
        ],
        "error": results.get("Error"),
    }


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
            if "Q" in time_period:
                cq = f"CY{time_period[:4]}-Q{time_period[-1]}"
            else:
                cq = f"CY{time_period[:4]}-Q1"
            observations.append(
                MacroObservation(
                    country_code="US",
                    series_id=str(row.get("SeriesCode") or "NIPA_T10106_A191RX"),
                    series_name=str(
                        row.get("LineDescription") or "Real Gross Domestic Product"
                    ),
                    observation_date=time_period,
                    calendar_quarter=cq,
                    value=val,
                    unit=str(row.get("UNIT_MULT") or "Billions of Chained Dollars"),
                    frequency="Q",
                )
            )
        return observations
