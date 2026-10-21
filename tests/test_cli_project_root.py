import json
import shutil
from pathlib import Path

from cil_cli.main import main
from cil_integrations.runtime.settings import Settings

REPOSITORY = Path(__file__).resolve().parents[1]


def _project(path: Path, provider_id: str) -> Path:
    (path / "config").mkdir(parents=True)
    shutil.copyfile(REPOSITORY / "config" / "providers.json", path / "config" / "providers.json")
    (path / "root-marker.json").write_text(json.dumps({"provider_id": provider_id}), encoding="utf-8")
    return path


def test_explicit_root_precedes_environment_and_cwd(tmp_path, monkeypatch):
    cwd = _project(tmp_path / "cwd", "cwd")
    env_root = _project(tmp_path / "env", "env")
    explicit = _project(tmp_path / "explicit", "explicit")
    monkeypatch.chdir(cwd)
    monkeypatch.setenv("COMPANY_INTEL_PROJECT_ROOT", str(env_root))
    assert Settings.from_env().project_root == env_root.resolve()
    assert Settings.from_env(explicit).project_root == explicit.resolve()


def test_cli_provider_status_uses_explicit_root_outside_checkout(tmp_path, monkeypatch, capsys):
    project = _project(tmp_path / "project", "local")
    monkeypatch.chdir(tmp_path)
    assert main(["--프로젝트-경로", str(project), "원천-상태"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert isinstance(payload, dict)


def test_cli_root_environment_fallback(tmp_path, monkeypatch, capsys):
    project = _project(tmp_path / "project", "local")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("COMPANY_INTEL_PROJECT_ROOT", str(project))
    assert main(["원천-상태"]) == 0
    assert json.loads(capsys.readouterr().out)
