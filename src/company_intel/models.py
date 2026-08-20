from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

Normalizer = Callable[[bytes, str], dict[str, Any]]


@dataclass
class Probe:
    id: str
    provider: str
    category: str
    regions: list[str]
    method: str
    url: str
    params: dict[str, Any] = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)
    json_body: dict[str, Any] | None = None
    expected_format: str = "json"
    required_paths: list[str] = field(default_factory=list)
    secret_env: str | None = None
    normalizer: Normalizer | None = None
    capabilities: list[str] = field(default_factory=list)
    quota_note: str | None = None
    limitation: str | None = None


@dataclass
class HttpResult:
    status_code: int | None
    headers: dict[str, str]
    body: bytes
    elapsed_ms: float
    attempts: int
    error: str | None = None
