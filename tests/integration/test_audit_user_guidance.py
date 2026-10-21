import json
import os
from pathlib import Path
import subprocess
import sys


def test_installed_command_help_is_available_outside_checkout(tmp_path):
    executable = Path(sys.executable).parent / "company-intel"
    environment = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    result = subprocess.run(
        [str(executable), "research", "--help"],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
    )
    assert (
        result.returncode == 0
        and "validate" in result.stdout
        and "report" in result.stdout
    )
