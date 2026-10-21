"""Canonical responsibility owner; migrated from src/company_intel/classification.py."""

from __future__ import annotations
from typing import Any
from dataclasses import dataclass, field


class KeyAlignmentError(KeyError):
    """Raised when a raw job record from an API lacks required attributes or alias keys."""

    pass


@dataclass
class DynamicAttributeDefinition:
    """Definition of an API return attribute with aliases, type, and optional constraint validator."""

    name: str
    aliases: tuple[str, ...]
    data_type: type = str
    required: bool = False
    default: Any = None
    validator: Any = None
    description: str = ""
