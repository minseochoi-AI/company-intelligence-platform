"""Canonical responsibility owner; migrated from src/company_intel/connectors/keyless.py."""

from __future__ import annotations
from cil_domain.providers.parsing import get_path
from cil_domain.providers.parsing import json_payload
from cil_domain.providers.parsing import preserve_payload
from typing import Any, Iterable, Iterator, Mapping


def _lever(body: bytes, _: str) -> dict[str, Any]:
    jobs = json_payload(body)
    return {
        "job_count": len(jobs),
        "jobs": [
            {
                "job_id": job.get("id"),
                "title": job.get("text"),
                "country": job.get("country"),
                "workplace_type": job.get("workplaceType"),
                "team": (job.get("categories") or {}).get("team"),
                "department": (job.get("categories") or {}).get("department"),
                "commitment": (job.get("categories") or {}).get("commitment"),
                "all_locations": job.get("allLocations")
                or (job.get("categories") or {}).get("allLocations")
                or [],
                "location": job.get("location")
                or (job.get("categories") or {}).get("location"),
                "created_at": job.get("createdAt"),
                "hosted_url": job.get("hostedUrl"),
                "apply_url": job.get("applyUrl"),
                "salaryRange": job.get("salaryRange"),
                "salaryDescriptionPlain": job.get("salaryDescriptionPlain"),
                "lists": job.get("lists"),
                "descriptionPlain": job.get("descriptionPlain"),
                "description": job.get("description"),
            }
            for job in jobs
        ],
    }
