"""Explicit commands for local fault export and read-only live verification."""

import argparse
import os
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from re import fullmatch
from uuid import uuid4

import httpx

from faultline_ci.gitlab_client import EvidenceError, GitLabClient
from faultline_ci.reports import write_report
from faultline_ci.scenarios import SCENARIO_ID, ScenarioError, export_fault
from faultline_ci.verifier import verify_recovery


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    export = commands.add_parser("export-fault", help="Export a broken local demo copy")
    export.add_argument("--source", type=Path, default=Path.cwd())
    export.add_argument("--destination", type=Path, required=True)
    verify = commands.add_parser("verify", help="Read actual evidence from GitLab.com")
    verify.add_argument("--project", required=True, help="GitLab namespace/project or project ID")
    verify.add_argument("--before", type=int, required=True)
    verify.add_argument("--after", type=int, required=True)
    verify.add_argument("--expected-sha", required=True)
    verify.add_argument("--output", type=Path, help="New run directory; never overwritten")
    args = parser.parse_args(argv)
    try:
        if args.command == "export-fault":
            export_fault(args.source, args.destination)
            print(f"Exported {SCENARIO_ID} to {args.destination}; source checkout unchanged")
            return 0
        if args.before <= 0 or args.after <= 0:
            raise EvidenceError("Pipeline IDs must be positive integers")
        if not fullmatch(r"[0-9a-f]{40}", args.expected_sha):
            raise EvidenceError("Expected SHA must be a full lowercase hexadecimal commit SHA")
        output = args.output or Path("reports") / f"verification-{uuid4().hex}"
        if output.exists() or output.is_symlink():
            raise EvidenceError("Report destination already exists; choose a new run directory")
        token = os.environ.get("GITLAB_TOKEN")
        headers = {"PRIVATE-TOKEN": token} if token else {}
        with httpx.Client(
            base_url="https://gitlab.com/api/v4/",
            headers=headers,
            timeout=20,
            follow_redirects=False,
        ) as http:
            client = GitLabClient(http, args.project)
            before = client.pipeline(args.before)
            after = client.pipeline(args.after)
        result = verify_recovery(before, after, args.expected_sha)
        report = {
            "schema_version": 1,
            "declared_scenario_id": SCENARIO_ID,
            "scenario_linkage": "not_checked",
            "source": "gitlab_api",
            "observed_at": datetime.now(UTC).isoformat(),
            "before": asdict(before),
            "after": asdict(after),
            "verification": asdict(result),
            "verification_scope": "pipeline_and_test_outcomes_only",
            "duo_provenance": "not_checked",
            "patch_safety": "not_checked",
            "commit_ancestry": "not_checked",
            "approval": "not_checked",
        }
        outcome = "PASS" if result.passed else "FAIL"
        reasons = "\n".join(f"- {reason}" for reason in result.reasons)
        markdown = (
            f"# Pipeline/test outcome check: {outcome}\n\n"
            f"Observed: {report['observed_at']}\n\n"
            f"Before: {before.url}\n\nAfter: {after.url}\n\n"
            f"Commit: `{after.sha}`\n\n{reasons}\n\n"
            "This checks observed outcomes only. Scenario linkage, commit ancestry, "
            "Duo provenance, approval, and patch safety require separate review.\n"
        )
        write_report(output, report, markdown)
        print(f"Outcome check {outcome}: wrote evidence to {output}")
        return 0 if result.passed else 1
    except (EvidenceError, ValueError, KeyError, TypeError, OSError) as error:
        # Validation messages we own are safe; API parsing/OS details may not be.
        message = (
            str(error)
            if isinstance(error, (EvidenceError, ScenarioError))
            else "Invalid input or evidence"
        )
        parser.exit(2, f"Evidence unavailable: {message}\n")


if __name__ == "__main__":
    raise SystemExit(main())
