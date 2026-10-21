"""Canonical responsibility owner; migrated from src/company_intel/classification.py."""

from __future__ import annotations
from typing import Any
from cil_contracts.attributes import DynamicAttributeDefinition
from cil_contracts.attributes import KeyAlignmentError


class DynamicJobSchemaRegistry:
    """Dynamic attribute registration and constraint validation engine for API return attributes.

    Allows dynamic registration of new API attributes, aliases, and constraint validators
    at runtime across different industry sectors (IT, Civil, Fire Safety, Energy Risk, etc.)
    without modifying static class definitions.
    """

    _registry: dict[str, DynamicAttributeDefinition] = {}

    @classmethod
    def register_attribute(
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
        cls._registry[name] = DynamicAttributeDefinition(
            name=name,
            aliases=tuple(aliases),
            data_type=data_type,
            required=required,
            default=default,
            validator=validator,
            description=description,
        )

    @classmethod
    def get_attribute(cls, name: str) -> DynamicAttributeDefinition | None:
        return cls._registry.get(name)

    @classmethod
    def list_registered_attributes(cls) -> list[dict[str, Any]]:
        """List all dynamically registered attributes and their alias mappings."""
        return [
            {
                "canonical_name": attr.name,
                "aliases": list(attr.aliases),
                "data_type": attr.data_type.__name__,
                "required": attr.required,
                "default": attr.default,
                "description": attr.description,
                "has_custom_validator": attr.validator is not None,
            }
            for attr in cls._registry.values()
        ]

    @classmethod
    def validate_and_extract(
        cls, raw: dict[str, Any], provider: str = "UNKNOWN"
    ) -> dict[str, Any]:
        """Extract all registered dynamic attributes from raw API payload and enforce constraints."""
        extracted: dict[str, Any] = {}
        missing_errors: list[str] = []
        constraint_errors: list[str] = []
        for name, attr in cls._registry.items():
            matched_val = None
            for alias in attr.aliases:
                val = raw.get(alias)
                if (
                    val is not None
                    and str(val).strip() != ""
                    and (str(val).lower() != "none")
                ):
                    matched_val = val
                    break
            if matched_val is None:
                if attr.required:
                    missing_errors.append(
                        f"Dynamic required field '{name}' missing; checked aliases {attr.aliases}"
                    )
                else:
                    extracted[name] = attr.default
                continue
            try:
                if attr.data_type in (int, float) and isinstance(
                    matched_val, (str, int, float)
                ):
                    matched_val = attr.data_type(
                        str(matched_val).replace(",", "").strip()
                    )
                elif attr.data_type is bool:
                    if type(matched_val) is bool:
                        pass
                    elif isinstance(
                        matched_val, str
                    ) and matched_val.strip().lower() in {
                        "true",
                        "1",
                        "y",
                        "yes",
                        "false",
                        "0",
                        "n",
                        "no",
                    }:
                        matched_val = matched_val.strip().lower() in {
                            "true",
                            "1",
                            "y",
                            "yes",
                        }
                    else:
                        raise ValueError("invalid explicit boolean")
                elif attr.data_type is str and (not isinstance(matched_val, str)):
                    matched_val = str(matched_val).strip()
            except Exception as e:
                constraint_errors.append(
                    f"Type cast error for '{name}'={matched_val} to {attr.data_type.__name__}: {e}"
                )
                continue
            if attr.validator and callable(attr.validator):
                try:
                    if not attr.validator(matched_val):
                        constraint_errors.append(
                            f"Constraint check failed for '{name}' with value '{matched_val}'"
                        )
                        continue
                except Exception as e:
                    constraint_errors.append(f"Validator exception for '{name}': {e}")
                    continue
            extracted[name] = matched_val
        all_errors = missing_errors + constraint_errors
        if all_errors:
            raise KeyAlignmentError(
                f"[{provider}] Dynamic schema contract violation:\n  "
                + "\n  ".join(all_errors)
            )
        return extracted
