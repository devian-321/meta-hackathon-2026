"""Independent, deliberately narrow policy for the pricing repair scenario."""

from dataclasses import dataclass
from hashlib import sha1, sha256
from pathlib import PurePosixPath

from faultline_ci.scenarios import BASELINE_SHA256, FAULT_SHA256, TARGET


@dataclass(frozen=True)
class Entry:
    path: str
    object_id: str
    mode: str
    kind: str


@dataclass(frozen=True)
class RepairEvidence:
    before_sha: str
    after_sha: str
    merge_base_sha: str
    before_tree: tuple[Entry, ...]
    after_tree: tuple[Entry, ...]
    before_content_sha256: str
    after_content_sha256: str


@dataclass(frozen=True)
class RepairVerification:
    passed: bool
    ancestry_passed: bool
    scope_passed: bool
    scenario_passed: bool
    changed_paths: tuple[str, ...]
    reasons: tuple[str, ...]


def content_hash(content: bytes, object_id: str) -> str:
    """Bind raw bytes to their Git blob ID before computing the scenario digest."""
    header = f"blob {len(content)}\0".encode()
    if sha1(header + content, usedforsecurity=False).hexdigest() != object_id:
        raise ValueError("Raw content does not match the repository blob ID")
    return sha256(content).hexdigest()


def verify_repair(
    evidence: RepairEvidence,
    expected_before: str,
    expected_after: str,
) -> RepairVerification:
    reasons: list[str] = []
    bound = evidence.before_sha == expected_before and evidence.after_sha == expected_after
    ancestry = (
        bound and expected_before != expected_after and evidence.merge_base_sha == expected_before
    )
    if not ancestry:
        reasons.append("Repair is not a descendant of the specified failing commit")
    before = {entry.path: entry for entry in evidence.before_tree}
    after = {entry.path: entry for entry in evidence.after_tree}
    unique = len(before) == len(evidence.before_tree) and len(after) == len(evidence.after_tree)
    target = TARGET.as_posix()
    ancestors = {str(path) for path in PurePosixPath(target).parents if str(path) != "."}
    changed = tuple(
        sorted(path for path in before.keys() | after.keys() if before.get(path) != after.get(path))
    )
    # Ancestor directory tree IDs change with their contents. Their metadata must
    # stay fixed, and all other repository objects must remain byte-identical.
    allowed = {target} | ancestors
    directories_valid = all(
        path in before
        and path in after
        and (before[path].kind, before[path].mode) == ("tree", "040000")
        and (after[path].kind, after[path].mode) == ("tree", "040000")
        for path in ancestors
    )
    target_valid = all(
        target in tree and (tree[target].kind, tree[target].mode) == ("blob", "100644")
        for tree in (before, after)
    )
    scope = (
        bound
        and unique
        and directories_valid
        and target_valid
        and target in changed
        and set(changed).issubset(allowed)
    )
    if not scope:
        reasons.append("Repair changes files or metadata outside the allowed pricing correction")
    scenario = (
        bound
        and evidence.before_content_sha256 == FAULT_SHA256
        and evidence.after_content_sha256 == BASELINE_SHA256
    )
    if not scenario:
        reasons.append("Code does not match the pinned fault and known-good pricing fixtures")
    return RepairVerification(
        passed=ancestry and scope and scenario,
        ancestry_passed=ancestry,
        scope_passed=scope,
        scenario_passed=scenario,
        changed_paths=changed,
        reasons=tuple(reasons),
    )
