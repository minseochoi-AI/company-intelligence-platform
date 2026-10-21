"""Canonical responsibility owner; migrated from src/company_intel/connectors/keyed.py."""

from __future__ import annotations
from cil_domain.providers.parsing import json_payload
from cil_domain.providers.parsing import preserve_payload
from cil_domain.providers.parsing import to_number
from typing import Any, Callable, Mapping
import xml.etree.ElementTree as ET


def _worknet_duty_normalizer(body: bytes, _: str) -> dict[str, Any]:
    root = ET.fromstring(body)
    duties = []
    for item in root.findall(".//jobDuty"):
        duties.append(
            {
                "duty_cd": item.findtext("dutyCd"),
                "duty_nm": item.findtext("dutyNm"),
                "ncs_cl_cd": item.findtext("ncsClCd"),
                "dutyCd": item.findtext("dutyCd"),
                "dutyNm": item.findtext("dutyNm"),
                "ncsClCd": item.findtext("ncsClCd"),
            }
        )
    return {
        "total": to_number(root.findtext(".//total")) or len(duties),
        "duties": duties,
    }
