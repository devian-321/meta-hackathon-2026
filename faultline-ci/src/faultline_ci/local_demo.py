"""A real local test rehearsal with a scripted repair, never a claimed Duo run."""

import os
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from xml.etree import ElementTree

from faultline_ci.gitlab_client import EvidenceError
from faultline_ci.repair import Entry, RepairEvidence, content_hash, verify_repair
from faultline_ci.scenarios import BASELINE_SHA256, BROKEN, GOOD, SCENARIO_ID, TARGET


def _environment() -> dict[str, str]:
    # A caller's GIT_DIR/worktree overrides must never redirect demo writes.
    return {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}


def _git(root: Path, *arguments: str) -> bytes:
    result = _process(
        [
            "git",
            "-c",
            "core.hooksPath=/dev/null",
            "-c",
            "commit.gpgsign=false",
            "-C",
            str(root),
            *arguments,
        ],
        env=_environment(),
        timeout=30,
    )
    if result.returncode:
        raise EvidenceError(
            "Local Git demo step failed; check Git installation and personal identity"
        )
    return result.stdout


def _process(
    arguments: list[str],
    *,
    env: dict[str, str],
    timeout: int,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[bytes]:
    try:
        return subprocess.run(arguments, env=env, cwd=cwd, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise EvidenceError("Local rehearsal command exceeded its time limit") from None


def _sha(root: Path) -> str:
    return _git(root, "rev-parse", "HEAD").decode().strip()


def _commit(root: Path, message: str) -> str:
    _git(root, "add", ".")
    _git(root, "commit", "-m", message)
    return _sha(root)


def _tree(root: Path, sha: str) -> tuple[Entry, ...]:
    entries = []
    for record in _git(root, "ls-tree", "-r", "-t", "-z", sha).split(b"\0"):
        if record:
            metadata, path = record.decode().split("\t", 1)
            mode, kind, object_id = metadata.split(" ")
            entries.append(Entry(path, object_id, mode, kind))
    return tuple(entries)


def _repair_evidence(root: Path, before: str, after: str) -> RepairEvidence:
    before_tree, after_tree = _tree(root, before), _tree(root, after)

    def target_digest(tree: tuple[Entry, ...]) -> str:
        entry = next(entry for entry in tree if entry.path == TARGET.as_posix())
        return content_hash(_git(root, "cat-file", "blob", entry.object_id), entry.object_id)

    return RepairEvidence(
        before,
        after,
        _git(root, "merge-base", before, after).decode().strip(),
        before_tree,
        after_tree,
        target_digest(before_tree),
        target_digest(after_tree),
    )


@dataclass(frozen=True)
class TestRun:
    stage: str
    commit_sha: str
    exit_code: int
    tests: int
    failed: int
    errors: int
    skipped: int
    elapsed_seconds: float


def _run(root: Path, stage: str, junit: Path) -> TestRun:
    started = time.monotonic()
    result = _process(
        [sys.executable, "-m", "pytest", "tests/test_sample_app.py", "-q", f"--junitxml={junit}"],
        cwd=root,
        env={
            **_environment(),
            "PYTHONPATH": str(root),
            "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
            "PYTEST_ADDOPTS": "",
            "PYTHONDONTWRITEBYTECODE": "1",
        },
        timeout=60,
    )
    elapsed = time.monotonic() - started
    try:
        cases = ElementTree.parse(junit).findall(".//testcase")
    except (OSError, ElementTree.ParseError):
        raise EvidenceError("Local tests did not publish a valid JUnit report") from None
    return TestRun(
        stage,
        _sha(root),
        result.returncode,
        len(cases),
        sum(case.find("failure") is not None for case in cases),
        sum(case.find("error") is not None for case in cases),
        sum(case.find("skipped") is not None for case in cases),
        round(elapsed, 4),
    )


def run_local_demo(source: Path) -> tuple[dict[str, Any], str, dict[str, bytes]]:
    """Run green/red/scripted-green and a false-green rejection in a disposable repo."""
    source = source.resolve()
    baseline = (source / TARGET).read_bytes().replace(BROKEN.encode(), GOOD.encode())
    if sha256(baseline).hexdigest() != BASELINE_SHA256:
        raise EvidenceError("Local demo source differs from the pinned pricing fixture")
    name = _git(source, "config", "user.name").decode().strip()
    email = _git(source, "config", "user.email").decode().strip()
    if not name or not email:
        raise EvidenceError("Set your personal Git name and email before running the local demo")
    with TemporaryDirectory(prefix="faultline-rehearsal-") as temporary:
        scratch = Path(temporary)
        root = scratch / "project"
        root.mkdir()
        for relative in (
            "sample_app/__init__.py",
            "sample_app/pricing.py",
            "tests/test_sample_app.py",
            "pyproject.toml",
            ".gitlab-ci.yml",
            ".gitignore",
        ):
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / relative, target)
        (root / TARGET).write_bytes(baseline)
        _git(root, "init", "-b", "main")
        _git(root, "config", "user.name", name)
        _git(root, "config", "user.email", email)
        _commit(root, "demo: healthy pricing baseline")
        green = _run(root, "Healthy baseline", scratch / "baseline.xml")

        _git(root, "switch", "-c", "demo/fault")
        (root / TARGET).write_bytes(baseline.replace(GOOD.encode(), BROKEN.encode()))
        fault_sha = _commit(root, "demo: inject discount sign regression")
        red = _run(root, "Injected fault", scratch / "fault.xml")

        _git(root, "switch", "-c", "demo/repaired")
        (root / TARGET).write_bytes(baseline)
        repair_sha = _commit(root, "demo: restore pinned fixture (scripted, no AI)")
        recovered = _run(root, "Scripted fixture restoration", scratch / "repaired.xml")
        good_evidence = _repair_evidence(root, fault_sha, repair_sha)
        good_result = verify_repair(good_evidence, fault_sha, repair_sha)

        _git(root, "switch", "-c", "demo/tampered", fault_sha)
        tests = root / "tests/test_sample_app.py"
        original_tests = tests.read_text()
        assertion = "assert total_cents(price, quantity, discount) == expected"
        if original_tests.count(assertion) != 1:
            raise EvidenceError("Sample assertion no longer matches the controlled tampering case")
        tests.write_text(original_tests.replace(assertion, "assert True  # dishonest repair"))
        tampered_sha = _commit(root, "demo: fake green by disabling pricing assertions")
        dishonest = _run(root, "Tampered assertions (false green)", scratch / "tampered.xml")
        bad_evidence = _repair_evidence(root, fault_sha, tampered_sha)
        bad_result = verify_repair(bad_evidence, fault_sha, tampered_sha)

        runs = (green, red, recovered, dishonest)
        expected = (
            (green.exit_code, red.exit_code, recovered.exit_code, dishonest.exit_code)
            == (0, 1, 0, 0)
            and all(run.tests == 8 and run.errors == 0 and run.skipped == 0 for run in runs)
            and (green.failed, red.failed, recovered.failed, dishonest.failed) == (0, 3, 0, 0)
            and good_result.passed
            and not bad_result.passed
        )
        if not expected:
            raise EvidenceError("Local rehearsal did not produce the expected measured outcomes")
        bundle = scratch / "demo.bundle"
        _git(root, "bundle", "create", str(bundle), "--all")
        bundle_bytes = bundle.read_bytes()
        report: dict[str, Any] = {
            "schema_version": 1,
            "source": "local_subprocess",
            "observed_at": datetime.now(UTC).isoformat(),
            "scenario_id": SCENARIO_ID,
            "verification_scope": "local_scripted_rehearsal",
            "verification": {"passed": True, "reasons": []},
            "duo_provenance": "not_run",
            "approval": "not_demonstrated",
            "repair_method": "scripted_fixture_restoration",
            "local_runs": [asdict(run) for run in runs],
            "repair_evidence": asdict(good_evidence),
            "repair_verification": asdict(good_result),
            "tampered_evidence": asdict(bad_evidence),
            "tampered_verification": asdict(bad_result),
            "git_bundle_sha256": sha256(bundle_bytes).hexdigest(),
        }
        rows = "\n".join(
            f"| {run.stage} | {run.tests - run.failed} | {run.failed} | `{run.commit_sha}` |"
            for run in runs
        )
        markdown = (
            "# FaultLine CI — local rehearsal\n\n"
            "**Real local Git commits and pytest runs. "
            "Scripted repair; GitLab Duo was not run.**\n\n"
            "| Stage | Passed tests | Failed tests | Commit |\n| --- | --- | --- | --- |\n"
            f"{rows}\n\nRepository guard accepts the exact repair "
            "and rejects the tampered tests.\n\n"
            "Commit ancestry and code scope were checked against real local Git objects. "
            "The bundled Git history preserves the proof. Native Duo, hosted pipelines, "
            "and human approval remain pending.\n\n"
            "Measured durations cover local pytest subprocesses only.\n"
        )
        artifacts = {"demo.bundle": bundle_bytes}
        artifacts.update({path.name: path.read_bytes() for path in scratch.glob("*.xml")})
        return report, markdown, artifacts
