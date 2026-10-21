"""Canonical responsibility owner; migrated from src/company_intel/macro_cubes.py."""

from __future__ import annotations
from dataclasses import dataclass


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
