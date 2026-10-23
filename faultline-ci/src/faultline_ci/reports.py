"""Publish a complete evidence bundle without replacing earlier reports."""

import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from faultline_ci.gitlab_client import EvidenceError


def write_report(output: Path, report: dict[str, Any], markdown: str) -> None:
    """Stage both files, reserve a new destination, then publish them together."""
    serialized = json.dumps(report, indent=2) + "\n"
    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=f".{output.name}-", dir=output.parent) as temporary:
        staging = Path(temporary)
        (staging / "recovery.json").write_text(serialized, encoding="utf-8")
        (staging / "recovery.md").write_text(markdown, encoding="utf-8")
        try:
            output.mkdir(exist_ok=False)
        except FileExistsError:
            raise EvidenceError(
                "Report destination already exists; choose a new run directory"
            ) from None
        # The reserved directory is empty. A failed write above cannot publish a
        # partial PASS, and a pre-existing evidence directory is never replaced.
        os.replace(staging, output)
