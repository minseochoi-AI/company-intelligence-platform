"""Explicit execution paths supplied by the composition root."""

from pathlib import Path
from typing import Protocol


class RunContext(Protocol):
    project_root: Path
    artifact_dir: Path
    database_url: str
    sec_user_agent: str
