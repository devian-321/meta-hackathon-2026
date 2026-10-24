import json
import shutil
import subprocess
from hashlib import sha256
from pathlib import Path

import pytest

from faultline_ci.cli import main
from faultline_ci.gitlab_client import EvidenceError
from faultline_ci.local_demo import _process


def test_local_demo_runs_real_tests_and_preserves_git_proof(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    root = Path(__file__).parents[1]
    for name in ("sample_app", "tests"):
        (source / name).mkdir()
    for name in (
        "sample_app/__init__.py",
        "sample_app/pricing.py",
        "tests/test_sample_app.py",
        "pyproject.toml",
        ".gitlab-ci.yml",
        ".gitignore",
    ):
        shutil.copyfile(root / name, source / name)
    # This disposable test identity is fixture data, never a submission author.
    for args in (
        ["init", "-b", "main"],
        ["config", "user.name", "Test Fixture"],
        ["config", "user.email", "fixture@example.invalid"],
    ):
        subprocess.run(["git", "-C", str(source), *args], check=True, capture_output=True)
    output = tmp_path / "evidence"
    assert main(["local-demo", "--source", str(source), "--output", str(output)]) == 0
    report = json.loads((output / "recovery.json").read_text())
    assert report["source"] == "local_subprocess"
    assert report["duo_provenance"] == "not_run"
    assert [run["failed"] for run in report["local_runs"]] == [0, 3, 0, 0]
    assert report["repair_verification"]["passed"]
    assert not report["tampered_verification"]["passed"]
    assert sha256((output / "demo.bundle").read_bytes()).hexdigest() == report["git_bundle_sha256"]
    assert "GitLab Duo and hosted pipelines were not run" in (output / "recovery.html").read_text()
    assert "REJECTED" in (output / "recovery.html").read_text()
    clone = tmp_path / "proof"
    subprocess.run(
        ["git", "clone", str(output / "demo.bundle"), str(clone)], check=True, capture_output=True
    )
    result = subprocess.run(
        ["git", "-C", str(clone), "branch", "-a"], check=True, capture_output=True, text=True
    )
    assert "demo/repaired" in result.stdout and "demo/tampered" in result.stdout


def test_rehearsal_timeout_is_an_actionable_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def expired(*args: object, **kwargs: object) -> None:
        raise subprocess.TimeoutExpired("test", 1)

    monkeypatch.setattr(subprocess, "run", expired)
    with pytest.raises(EvidenceError, match="time limit"):
        _process(["test"], env={}, timeout=1)
