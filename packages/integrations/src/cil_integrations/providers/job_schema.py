"""Canonical responsibility owner; migrated from src/company_intel/classification.py."""

from __future__ import annotations
from typing import Any
from cil_contracts.attributes import KeyAlignmentError
from cil_domain.attributes.registry import DynamicJobSchemaRegistry


class JobSchemaContract:
    """Enforces attribute key alignment and defends against silent None omissions across APIs."""

    REQUIRED_CANONICAL_FIELDS: dict[str, tuple[str, ...]] = {
        "job_id": (
            "job_id",
            "portal_id",
            "idx",
            "pblJobId",
            "PositionID",
            "MatchedObjectId",
            "id",
            "wantedAuthNo",
        ),
        "job_url": (
            "posting_url",
            "job_url",
            "url",
            "pbancUrl",
            "srcUrl",
            "PositionURI",
            "wantedInfoUrl",
        ),
        "employer_name": (
            "employer_name",
            "employer",
            "institution_name",
            "insttNm",
            "insttname",
            "OrganizationName",
            "company",
        ),
        "job_title": (
            "job_title",
            "job_title_cz",
            "title",
            "PositionTitle",
            "pblJobNm",
        ),
    }

    @classmethod
    def register_dynamic_attribute(
        cls,
        name: str,
        aliases: tuple[str, ...] | list[str],
        data_type: type = str,
        required: bool = False,
        default: Any = None,
        validator: Any = None,
        description: str = "",
    ) -> None:
        """Register a new API return attribute dynamically into the schema contract."""
        DynamicJobSchemaRegistry.register_attribute(
            name=name,
            aliases=aliases,
            data_type=data_type,
            required=required,
            default=default,
            validator=validator,
            description=description,
        )

    @classmethod
    def list_dynamic_attributes(cls) -> list[dict[str, Any]]:
        return DynamicJobSchemaRegistry.list_registered_attributes()

    @classmethod
    def validate_and_normalize(
        cls, raw_job: dict[str, Any], provider: str
    ) -> dict[str, Any]:
        """Validate presence of required canonical keys and resolve aliases."""
        normalized = dict(raw_job)
        missing_errors: list[str] = []
        for canonical_key, aliases in cls.REQUIRED_CANONICAL_FIELDS.items():
            matched_val = None
            matched_alias = None
            for alias in aliases:
                val = raw_job.get(alias)
                if (
                    val is not None
                    and str(val).strip() != ""
                    and (str(val).lower() != "none")
                ):
                    matched_val = str(val).strip()
                    matched_alias = alias
                    break
            if canonical_key == "job_url":
                if matched_val is not None:
                    if matched_val.startswith("www.") or (
                        not matched_val.startswith("http://")
                        and (not matched_val.startswith("https://"))
                        and ("." in matched_val)
                    ):
                        matched_val = f"https://{matched_val}"
                elif provider in ("CZ_MPSV", "MPSV"):
                    portal_id = raw_job.get("portal_id") or raw_job.get("job_id")
                    if portal_id:
                        matched_val = f"https://www.uradprace.cz/web/cz/volna-mista-v-cr#/volna-mista-detail/{str(portal_id).strip()}"
                        matched_alias = "synthesized:portal_id"
            if matched_val is None:
                missing_errors.append(
                    f"Field '{canonical_key}' missing; checked aliases {aliases}"
                )
            else:
                normalized[canonical_key] = matched_val
                normalized[f"_{canonical_key}_source_alias"] = matched_alias
        if missing_errors:
            raise KeyAlignmentError(
                f"[{provider}] Job schema contract violation:\n  "
                + "\n  ".join(missing_errors)
            )
        if DynamicJobSchemaRegistry._registry:
            dynamic_vals = DynamicJobSchemaRegistry.validate_and_extract(
                raw_job, provider=provider
            )
            normalized.update(dynamic_vals)
        return normalized
