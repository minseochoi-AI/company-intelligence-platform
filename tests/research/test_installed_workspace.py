"""Installed distribution behavior independent of checkout working directory."""

import json
import os
import subprocess
import sys


def test_installed_cli_and_packaged_resources_from_another_directory(tmp_path):
    script = """
import json
from importlib.resources import files
from cil_integrations.runtime.settings import Settings
from cil_integrations.catalog.repository import load_source_catalog
from cil_contracts.requests import ReportRequest
assert len(load_source_catalog().operations) > 0
assert files('cil_integrations').joinpath('resources/sql/duckdb_schema.sql').is_file()
assert files('cil_contracts').joinpath('resources/research/evidence-bundle-v2.schema.json').is_file()
print(json.dumps({'status': 'installed-resources-found'}))
"""
    environment = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    result = subprocess.run(
        [sys.executable, "-I", "-c", script],
        cwd=tmp_path,
        env=environment,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["status"] == "installed-resources-found"
