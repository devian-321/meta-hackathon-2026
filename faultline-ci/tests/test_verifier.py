from dataclasses import replace

import pytest

from faultline_ci.verifier import Pipeline, verify_recovery
from faultline_ci.verifier import TestCase as Case


@pytest.fixture
def before() -> Pipeline:
    return Pipeline(
        1,
        10,
        "a" * 40,
        "demo/fault",
        "failed",
        "https://gitlab.com/pipelines/10",
        (Case(("pricing", "discount"), "failed"), Case(("pricing", "zero"), "success")),
        ("failed",),
    )


@pytest.fixture
def after(before: Pipeline) -> Pipeline:
    return replace(
        before,
        pipeline_id=11,
        sha="b" * 40,
        status="success",
        tests=tuple(replace(t, status="success") for t in before.tests),
        test_job_statuses=("success",),
    )


def test_verified_recovery(before: Pipeline, after: Pipeline) -> None:
    assert verify_recovery(before, after, after.sha).passed


@pytest.mark.parametrize(
    "change",
    [
        {"status": "running"},
        {"project_id": 2},
        {"pipeline_id": 10},
        {"sha": "a" * 40},
        {"tests": ()},
        {"test_job_statuses": ()},
        {"test_job_statuses": ("skipped",)},
        {"tests": (Case(("pricing", "unrelated"), "success"),)},
        {"tests": (Case(("pricing", "discount"), "skipped"),)},
        {"tests": (Case(("pricing", "discount"), "success"),) * 2},
    ],
)
def test_false_green_is_rejected(before: Pipeline, after: Pipeline, change: dict) -> None:
    assert not verify_recovery(before, replace(after, **change), after.sha).passed


def test_wrong_expected_commit(before: Pipeline, after: Pipeline) -> None:
    assert not verify_recovery(before, after, "c" * 40).passed


def test_missing_failure_evidence(before: Pipeline, after: Pipeline) -> None:
    assert not verify_recovery(replace(before, tests=after.tests), after, after.sha).passed
