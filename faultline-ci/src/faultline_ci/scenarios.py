"""Export a controlled fault without changing the checkout or running commands."""

import shutil
from pathlib import Path

SCENARIO_ID = "pricing-discount-sign-v1"
TARGET = Path("sample_app/pricing.py")
GOOD = "return subtotal * (100 - discount_percent) // 100"
BROKEN = "return subtotal * (100 + discount_percent) // 100"
BASELINE_SHA256 = "433a218a278d1454da443b423bb7e4da1a13e6ea7ee0e43851bdd415f7072a78"
FAULT_SHA256 = "f8d71a0e1e960f0f36699154113274c27a69b76ff4b88caa6b5f0956634afb73"


class ScenarioError(ValueError):
    """An actionable local scenario precondition was not met."""


def export_fault(source: Path, destination: Path) -> None:
    """Copy demo app/tests into a new directory, then inject one known regression."""
    source = source.resolve()
    destination = destination.resolve()
    if destination == source or source in destination.parents:
        raise ScenarioError("Export must be outside the source checkout")
    if destination.exists():
        raise ScenarioError("Export destination must not exist")
    original = (source / TARGET).read_text()
    if original.count(GOOD) != 1:
        raise ScenarioError("Scenario precondition failed: expected one known baseline expression")
    destination.mkdir(parents=True)
    for folder in ("sample_app", "tests"):
        shutil.copytree(
            source / folder,
            destination / folder,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
    (destination / TARGET).write_text(original.replace(GOOD, BROKEN))
