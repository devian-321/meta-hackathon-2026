"""A fail-closed evidence check, separate from the repairing agent.

This checks observed pipeline/test outcomes, not patch safety or Duo provenance.
Those remain separate submission gates.
"""

from dataclasses import dataclass
from re import fullmatch


@dataclass(frozen=True)
class TestCase:
    identity: tuple[str, str]
    status: str


@dataclass(frozen=True)
class Pipeline:
    project_id: int
    pipeline_id: int
    sha: str
    ref: str
    status: str
    url: str
    tests: tuple[TestCase, ...]
    test_job_statuses: tuple[str, ...]


@dataclass(frozen=True)
class Verification:
    passed: bool
    reasons: tuple[str, ...]


def verify_recovery(before: Pipeline, after: Pipeline, expected_sha: str) -> Verification:
    """Require a distinct repaired commit and restoration of every observed test."""
    reasons: list[str] = []
    if before.project_id != after.project_id:
        reasons.append("Pipelines belong to different projects")
    if before.pipeline_id >= after.pipeline_id:
        reasons.append("Recovery must be a newer, distinct pipeline")
    if before.status != "failed":
        reasons.append("Initial pipeline did not fail")
    if after.status != "success":
        reasons.append("Recovery pipeline is not successful")
    if after.sha != expected_sha or not fullmatch(r"[0-9a-f]{40}", expected_sha):
        reasons.append("Recovery SHA does not match the expected full commit SHA")
    if not fullmatch(r"[0-9a-f]{40}", before.sha):
        reasons.append("Initial pipeline does not identify a valid full commit SHA")
    if before.sha == after.sha:
        reasons.append("No new repair commit was observed")
    if not before.test_job_statuses or "failed" not in before.test_job_statuses:
        reasons.append("No failed sample test job was observed before repair")
    if not after.test_job_statuses or any(s != "success" for s in after.test_job_statuses):
        reasons.append("Recovery sample test jobs are missing or not successful")
    if not before.tests or not after.tests:
        reasons.append("Test evidence is missing")
    before_ids = [test.identity for test in before.tests]
    after_ids = [test.identity for test in after.tests]
    if len(set(before_ids)) != len(before_ids) or len(set(after_ids)) != len(after_ids):
        reasons.append("Duplicate test identities make the evidence ambiguous")
    if not any(t.status in {"failed", "error"} for t in before.tests):
        reasons.append("Initial test evidence contains no failing test")
    recovered = {test.identity for test in after.tests if test.status == "success"}
    if not set(before_ids).issubset(recovered):
        reasons.append("Some original tests are absent, skipped, or still failing")
    if any(test.status != "success" for test in after.tests):
        reasons.append("Recovery contains unsuccessful or skipped tests")
    return Verification(passed=not reasons, reasons=tuple(reasons))
