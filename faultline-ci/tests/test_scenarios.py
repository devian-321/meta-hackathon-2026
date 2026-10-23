from pathlib import Path

import pytest

from faultline_ci.scenarios import BROKEN, GOOD, TARGET, export_fault


@pytest.fixture
def source(tmp_path: Path) -> Path:
    """Exercise the exporter independently of the intentionally faulted application."""
    root = tmp_path / "source"
    (root / "sample_app").mkdir(parents=True)
    (root / "tests").mkdir()
    (root / TARGET).write_text(f"def calculate(subtotal, discount_percent):\n    {GOOD}\n")
    (root / "tests/test_sample_app.py").write_text("# Unchanged test fixture\n")
    return root


def test_export_preserves_baseline(tmp_path: Path, source: Path) -> None:
    destination = tmp_path / "fault"
    export_fault(source, destination)
    assert GOOD in (source / TARGET).read_text()
    assert BROKEN in (destination / TARGET).read_text()
    assert (destination / "tests/test_sample_app.py").read_bytes() == (
        source / "tests/test_sample_app.py"
    ).read_bytes()


def test_existing_destination_is_rejected(tmp_path: Path, source: Path) -> None:
    with pytest.raises(ValueError, match="must not exist"):
        export_fault(source, tmp_path)


def test_export_inside_source_is_rejected(source: Path) -> None:
    with pytest.raises(ValueError, match="outside"):
        export_fault(source, source / "reports/fault")
