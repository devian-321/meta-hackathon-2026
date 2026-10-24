from hashlib import sha1, sha256
from pathlib import Path

import pytest

from faultline_ci.repair import Entry, RepairEvidence
from faultline_ci.scenarios import BASELINE_SHA256, BROKEN, FAULT_SHA256, GOOD


def blob_id(content: bytes) -> str:
    return sha1(f"blob {len(content)}\0".encode() + content, usedforsecurity=False).hexdigest()


@pytest.fixture
def pricing_bytes() -> tuple[bytes, bytes]:
    # Harness remains valid on both the healthy and intentional fault branches.
    baseline = (Path(__file__).parents[1] / "sample_app/pricing.py").read_bytes()
    baseline = baseline.replace(BROKEN.encode(), GOOD.encode())
    fault = baseline.replace(GOOD.encode(), BROKEN.encode())
    assert sha256(baseline).hexdigest() == BASELINE_SHA256
    assert sha256(fault).hexdigest() == FAULT_SHA256
    return fault, baseline


@pytest.fixture
def repair_evidence(pricing_bytes: tuple[bytes, bytes]) -> RepairEvidence:
    fault, baseline = pricing_bytes
    tests = Entry("tests/test_sample_app.py", "c" * 40, "100644", "blob")
    return RepairEvidence(
        before_sha="a" * 40,
        after_sha="b" * 40,
        merge_base_sha="a" * 40,
        before_tree=(
            Entry("sample_app", "d" * 40, "040000", "tree"),
            Entry("sample_app/pricing.py", blob_id(fault), "100644", "blob"),
            tests,
        ),
        after_tree=(
            Entry("sample_app", "e" * 40, "040000", "tree"),
            Entry("sample_app/pricing.py", blob_id(baseline), "100644", "blob"),
            tests,
        ),
        before_content_sha256=FAULT_SHA256,
        after_content_sha256=BASELINE_SHA256,
    )
