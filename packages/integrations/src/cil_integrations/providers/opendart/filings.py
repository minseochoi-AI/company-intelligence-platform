"""Canonical responsibility owner; migrated from src/company_intel/connectors/keyed.py."""

from __future__ import annotations
from cil_domain.providers.parsing import json_payload
from cil_domain.providers.parsing import preserve_payload
from cil_domain.providers.parsing import to_number
from typing import Any, Callable, Mapping


def _dart(body: bytes, _: str) -> dict[str, Any]:
    data = json_payload(body)
    rows = data.get("list", [])
    normalized = []
    for row in rows:
        normalized.append(
            {
                "corp_code": row.get("corp_code"),
                "report_year": row.get("bsns_year"),
                "report_code": row.get("reprt_code"),
                "statement": row.get("sj_div"),
                "account_id": row.get("account_id"),
                "account_name": row.get("account_nm"),
                "account_detail": row.get("account_detail"),
                "order": row.get("ord"),
                "current_amount": to_number(row.get("thstrm_amount")),
                "current_cumulative_amount": to_number(row.get("thstrm_add_amount")),
                "previous_amount": to_number(row.get("frmtrm_amount")),
                "currency": row.get("currency"),
                "receipt_no": row.get("rcept_no"),
            }
        )
    return {
        "status": data.get("status"),
        "message": data.get("message"),
        "row_count": len(rows),
        "financial_facts": normalized,
    }
