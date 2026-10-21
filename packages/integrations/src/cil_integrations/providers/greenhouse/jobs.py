"""Canonical responsibility owner; migrated from src/company_intel/connectors/keyless.py."""

from __future__ import annotations
from cil_domain.providers.parsing import get_path
from cil_domain.providers.parsing import json_payload
from cil_domain.providers.parsing import preserve_payload
from typing import Any, Iterable, Iterator, Mapping


def _greenhouse(body: bytes, _: str) -> dict[str, Any]:
    data = json_payload(body)
    jobs = data.get("jobs", [])
    return {
        "job_count": len(jobs),
        "jobs": [
            {
                "job_id": str(job.get("id")),
                "company_name": job.get("company_name"),
                "title": job.get("title"),
                "location": (job.get("location") or {}).get("name"),
                "departments": [
                    department.get("name") for department in job.get("departments", [])
                ],
                "offices": [
                    {"name": office.get("name"), "location": office.get("location")}
                    for office in job.get("offices", [])
                ],
                "language": job.get("language"),
                "first_published": job.get("first_published"),
                "updated_at": job.get("updated_at"),
                "application_deadline": job.get("application_deadline"),
                "absolute_url": job.get("absolute_url"),
                "pay_input_ranges": job.get("pay_input_ranges"),
                "metadata": job.get("metadata"),
                "content": job.get("content"),
            }
            for job in jobs
        ],
    }
