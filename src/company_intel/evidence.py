from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .models import HttpResult, Probe
from .security import redact_body, redact_url, redact_value


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")


class EvidenceStore:
    def __init__(self, root: Path, secret_values: list[str]) -> None:
        self.root = root
        self.raw_dir = root / "raw"
        self.normalized_dir = root / "normalized"
        self.log_dir = root / "logs"
        self.secret_values = [value for value in secret_values if value]
        for directory in (self.raw_dir, self.normalized_dir, self.log_dir):
            directory.mkdir(parents=True, exist_ok=True)

    def append_log(self, name: str, value: dict[str, Any]) -> None:
        path = self.log_dir / f"{name}.jsonl"
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(redact_value(value, self.secret_values), ensure_ascii=False) + "\n")

    def preserve(
        self,
        probe: Probe,
        result: HttpResult,
        normalized: dict[str, Any] | None,
        extension: str,
    ) -> dict[str, Any]:
        content_type = result.headers.get("content-type", "")
        stored_body, was_redacted = redact_body(result.body, self.secret_values, content_type)
        raw_path = self.raw_dir / f"{probe.id}.{extension}"
        raw_path.write_bytes(stored_body)
        normalized_path = self.normalized_dir / f"{probe.id}.json"
        if normalized is not None:
            write_json(normalized_path, {"probe_id": probe.id, "collected_at": utc_now(), "data": normalized})

        record = {
            "probe_id": probe.id,
            "provider": probe.provider,
            "method": probe.method,
            "url": redact_url(probe.url, self.secret_values),
            "http_status": result.status_code,
            "elapsed_ms": result.elapsed_ms,
            "attempts": result.attempts,
            "response_bytes": len(result.body),
            "response_sha256_before_redaction": sha256_bytes(result.body),
            "stored_body_redacted": was_redacted,
            "response_headers": result.headers,
            "raw_file": str(raw_path.relative_to(self.root.parent)),
            "normalized_file": str(normalized_path.relative_to(self.root.parent))
            if normalized is not None
            else None,
            "collected_at": utc_now(),
        }
        self.append_log("api_calls", record)
        self.append_log(
            "quota",
            {
                "collected_at": record["collected_at"],
                "provider": probe.provider,
                "probe_id": probe.id,
                "quota_note": probe.quota_note,
                "headers": {
                    k: v
                    for k, v in result.headers.items()
                    if "rate" in k or "quota" in k or k == "retry-after"
                },
            },
        )
        return record
