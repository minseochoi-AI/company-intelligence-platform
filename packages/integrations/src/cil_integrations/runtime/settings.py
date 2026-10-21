"""Canonical responsibility owner; migrated from src/company_intel/config.py."""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import os


def load_dotenv(path: Path | str = ".env") -> None:
    """Load a minimal dotenv file without overwriting process environment."""
    env_path = Path(path)
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = (key.strip(), value.strip().strip('"').strip("'"))
        if key:
            os.environ.setdefault(key, value)


@dataclass(frozen=True)
class Settings:
    project_root: Path
    artifact_dir: Path
    database_url: str
    sec_user_agent: str

    @classmethod
    def from_env(cls, project_root: Path | None = None) -> Settings:
        configured_root = os.getenv("COMPANY_INTEL_PROJECT_ROOT")
        root = (
            project_root or (Path(configured_root) if configured_root else Path.cwd())
        ).resolve()
        load_dotenv(root / ".env")
        configured_artifacts = Path(os.getenv("ARTIFACT_DIR", "artifacts"))
        artifact_dir = (
            configured_artifacts
            if configured_artifacts.is_absolute()
            else root / configured_artifacts
        ).resolve()
        return cls(
            project_root=root.resolve(),
            artifact_dir=artifact_dir,
            database_url=os.getenv(
                "DATABASE_URL",
                f"duckdb:///{(root / 'data/company_intelligence.duckdb').resolve()}",
            ),
            sec_user_agent=os.getenv(
                "SEC_USER_AGENT",
                "company-intelligence/0.1 contact=replace-with-your-email@example.com",
            ),
        )


SECRET_ENV_NAMES = (
    "FRED_API_KEY",
    "BEA_API_KEY",
    "OPENDART_API_KEY",
    "ECOS_API_KEY",
    "ALIO_PLUS_FACILITY_API_KEY",
    "ALIO_PLUS_EVENT_API_KEY",
    "ALIO_PLUS_BUSINESS_API_KEY",
    "ALIO_PLUS_ORGANIZATION_API_KEY",
    "MPM_PUBLIC_EMPLOYMENT_API_KEY",
    "ALPHAVANTAGE_API_KEY",
)


def configured_secrets() -> dict[str, str]:
    return {name: value for name in SECRET_ENV_NAMES if (value := os.getenv(name))}
