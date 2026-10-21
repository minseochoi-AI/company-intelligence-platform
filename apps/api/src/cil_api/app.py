"""Canonical responsibility owner; migrated from src/company_intel/api.py."""

from __future__ import annotations
from cil_api.bootstrap import configure as _configure

_configure()
from fastapi import FastAPI, HTTPException

app = FastAPI(title="Company Intelligence API", version="0.1.0")

from cil_api.routes import health, analysis, companies, jobs, reports, runs  # noqa: E402,F401
from cil_api.research import router as research_router

app.include_router(research_router)
