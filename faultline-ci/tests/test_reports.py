from pathlib import Path

import pytest

from faultline_ci.gitlab_client import EvidenceError
from faultline_ci.reports import write_report


def test_partial_write_cannot_publish_pass(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_write = Path.write_text

    def write(path: Path, text: str, **kwargs: object) -> int:
        if path.name.endswith(".md"):
            raise OSError("Disk failure during second file")
        return real_write(path, text, **kwargs)

    monkeypatch.setattr(Path, "write_text", write)
    destination = tmp_path / "run"
    with pytest.raises(OSError):
        write_report(destination, {"passed": True}, "PASS")
    assert not destination.exists()
    assert list(tmp_path.iterdir()) == []


def test_existing_report_directory_is_not_replaced(tmp_path: Path) -> None:
    with pytest.raises(EvidenceError, match="already exists"):
        write_report(tmp_path, {}, "PASS")
