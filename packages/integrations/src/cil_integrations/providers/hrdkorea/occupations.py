"""Canonical responsibility owner; migrated from src/company_intel/connectors/keyed.py."""

from __future__ import annotations
from cil_domain.providers.parsing import json_payload
from cil_domain.providers.parsing import preserve_payload
from cil_domain.providers.parsing import to_number
from typing import Any, Callable, Mapping
import xml.etree.ElementTree as ET


def _ncs_duty_normalizer(body: bytes, _: str) -> dict[str, Any]:
    root = ET.fromstring(body)
    items = []
    for item in root.findall(".//item"):
        items.append(
            {
                "ncs_lcls_cd": item.findtext("ncsLclsCd"),
                "ncs_lcls_nm": item.findtext("ncsLclsNm"),
                "ncs_mcls_cd": item.findtext("ncsMclsCd"),
                "ncs_mcls_nm": item.findtext("ncsMclsNm"),
                "ncs_scls_cd": item.findtext("ncsSclsCd"),
                "ncs_scls_nm": item.findtext("ncsSclsNm"),
                "ncs_sub_cd": item.findtext("ncsSubCd"),
                "ncs_sub_nm": item.findtext("ncsSubNm"),
                "duty_cd": item.findtext("dutyCd"),
                "comp_unit_cd": item.findtext("compUnitCd"),
                "ncsSubCd": item.findtext("ncsSubCd"),
                "dutyCd": item.findtext("dutyCd"),
                "compUnitCd": item.findtext("compUnitCd"),
            }
        )
    return {
        "result_code": root.findtext(".//resultCode"),
        "total": to_number(root.findtext(".//totalCount")) or len(items),
        "items": items,
    }
