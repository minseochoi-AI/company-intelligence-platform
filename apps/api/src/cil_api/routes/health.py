"""Canonical responsibility owner; migrated from src/company_intel/api.py."""

from __future__ import annotations
from cil_api.app import app
from cil_integrations.runtime.settings import Settings
from fastapi import FastAPI, HTTPException
from pathlib import Path
from typing import Any
import json


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/validation/latest")
def latest_validation() -> dict[str, Any]:
    settings = Settings.from_env(Path.cwd())
    path = settings.artifact_dir / "validation_results.json"
    if not path.exists():
        raise HTTPException(404, "Run company-intel validate first")
    return json.loads(path.read_text(encoding="utf-8"))
