from dataclasses import replace

import pytest

from faultline_ci.repair import Entry, RepairEvidence, content_hash, verify_repair


def test_exact_repair_of_descendant_is_accepted(repair_evidence: RepairEvidence) -> None:
    result = verify_repair(repair_evidence, "a" * 40, "b" * 40)
    assert result.passed
    assert result.changed_paths == ("sample_app", "sample_app/pricing.py")


@pytest.mark.parametrize(
    "path", ["tests/test_sample_app.py", ".gitlab-ci.yml", "src/faultline_ci/verifier.py"]
)
def test_test_or_ci_tampering_is_rejected_even_with_restored_pricing(
    repair_evidence: RepairEvidence,
    path: str,
) -> None:
    tree = tuple(entry for entry in repair_evidence.after_tree if entry.path != path)
    changed = replace(repair_evidence, after_tree=tree + (Entry(path, "f" * 40, "100644", "blob"),))
    result = verify_repair(changed, "a" * 40, "b" * 40)
    assert not result.passed
    assert result.scenario_passed
    assert not result.scope_passed


@pytest.mark.parametrize("field", ["before_sha", "after_sha", "merge_base_sha"])
def test_unrelated_commit_is_rejected(repair_evidence: RepairEvidence, field: str) -> None:
    assert not verify_repair(
        replace(repair_evidence, **{field: "f" * 40}), "a" * 40, "b" * 40
    ).passed


def test_rewritten_function_with_correct_test_names_is_rejected(
    repair_evidence: RepairEvidence,
) -> None:
    altered = replace(repair_evidence, after_content_sha256="f" * 64)
    assert not verify_repair(altered, "a" * 40, "b" * 40).scenario_passed


def test_ambiguous_repository_inventory_is_rejected(repair_evidence: RepairEvidence) -> None:
    altered = replace(repair_evidence, after_tree=repair_evidence.after_tree * 2)
    assert not verify_repair(altered, "a" * 40, "b" * 40).scope_passed


@pytest.mark.parametrize("mode", ["100755", "120000"])
def test_executable_or_symlink_repair_is_rejected(
    repair_evidence: RepairEvidence, mode: str
) -> None:
    altered = replace(
        repair_evidence,
        after_tree=tuple(
            replace(entry, mode=mode) if entry.path == "sample_app/pricing.py" else entry
            for entry in repair_evidence.after_tree
        ),
    )
    assert not verify_repair(altered, "a" * 40, "b" * 40).scope_passed


def test_raw_bytes_are_bound_to_git_object_id() -> None:
    with pytest.raises(ValueError, match="blob ID"):
        content_hash(b"unrelated code", "f" * 40)
