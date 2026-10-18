#!/usr/bin/env python3
"""Verify a CIL run manifest without contacting providers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def verify(path: Path) -> tuple[bool, str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return False, f"unreadable manifest: {exc}"
    if payload.get("schema_version") not in {"1.0", "2.0"}:
        return False, "unsupported CIL run-manifest schema_version"
    for key in ("run_id", "generated_at", "command", "lineage"):
        if key not in payload:
            return False, f"missing field: {key}"
    try:
        from company_intel.run_manifest import verify_manifest
    except ImportError as exc:
        return False, f"CIL package is unavailable: {exc}"
    if not verify_manifest(payload):
        return False, "lineage hash mismatch"
    return True, "manifest lineage is valid"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args(argv)
    valid, detail = verify(args.manifest)
    print(json.dumps({"status": "valid" if valid else "invalid", "detail": detail}, ensure_ascii=False))
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
