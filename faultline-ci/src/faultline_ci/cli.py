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
from faultline_ci.local_demo import run_local_demo
from faultline_ci.repair import verify_repair
from faultline_ci.reports import write_report
from faultline_ci.scenarios import SCENARIO_ID, ScenarioError, export_fault
from faultline_ci.verifier import verify_recovery


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    export = commands.add_parser("export-fault", help="Export a broken local demo copy")
    export.add_argument("--source", type=Path, default=Path.cwd())
    export.add_argument("--destination", type=Path, required=True)
    demo = commands.add_parser(
        "local-demo", help="Run real local tests with a scripted repair; no Duo"
    )
    demo.add_argument("--source", type=Path, default=Path.cwd())
    demo.add_argument("--output", type=Path, default=Path("reports/local-demo"))
    verify = commands.add_parser("verify", help="Read actual evidence from GitLab.com")
    verify.add_argument("--project", required=True, help="GitLab namespace/project or project ID")
    verify.add_argument("--before", type=int, required=True)
    verify.add_argument("--after", type=int, required=True)
    verify.add_argument("--expected-sha", required=True)
    verify.add_argument(
        "--check-repair",
        action="store_true",
        help="Also verify ancestry, file scope and pinned scenario bytes",
    )
    verify.add_argument("--output", type=Path, help="New run directory; never overwritten")
    args = parser.parse_args(argv)
    try:
        if args.command == "local-demo":
            if args.output.exists() or args.output.is_symlink():
                raise EvidenceError("Report destination already exists; choose a new run directory")
            demo_report, demo_markdown, artifacts = run_local_demo(args.source)
            write_report(args.output, demo_report, demo_markdown, artifacts)
            print(
                "Local rehearsal passed. Scripted repair; no Duo run. "
                f"Open {args.output / 'recovery.html'}"
            )
            return 0
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
            repair_evidence = client.repair(before, after) if args.check_repair else None
        result = verify_recovery(before, after, args.expected_sha)
        repair_result = (
            verify_repair(repair_evidence, before.sha, after.sha) if repair_evidence else None
        )
        passed = result.passed and (repair_result is None or repair_result.passed)
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
        if repair_result and repair_evidence:
            report.update(
                {
                    "repair_evidence": asdict(repair_evidence),
                    "repair_verification": asdict(repair_result),
                    "scenario_linkage": "passed" if repair_result.scenario_passed else "failed",
                    "patch_safety": "scope_passed"
                    if repair_result.scope_passed
                    else "scope_failed",
                    "commit_ancestry": "passed" if repair_result.ancestry_passed else "failed",
                    "verification_scope": "pipeline_tests_ancestry_scope_and_pinned_scenario",
                    "verification": {
                        "passed": passed,
                        "reasons": result.reasons + repair_result.reasons,
                    },
                    "outcome_verification": asdict(result),
                }
            )
        outcome = "PASS" if passed else "FAIL"
        reasons = "\n".join(
            f"- {reason}"
            for reason in result.reasons + (repair_result.reasons if repair_result else ())
        )
        repair_summary = (
            f"Repository guard: {'PASS' if repair_result.passed else 'FAIL'}\n\n"
            f"Changed paths: {', '.join(repair_result.changed_paths)}\n\n"
            if repair_result
            else "Repository guard: not requested.\n\n"
        )
        markdown = (
            f"# Pipeline/test outcome check: {outcome}\n\n"
            f"Observed: {report['observed_at']}\n\n"
            f"Before: {before.url}\n\nAfter: {after.url}\n\n"
            f"Commit: `{after.sha}`\n\n{reasons}\n\n"
            f"{repair_summary}"
            "Duo provenance and human approval require separate review. "
            "The repository guard is restricted to the pinned pricing scenario.\n"
        )
        write_report(output, report, markdown)
        print(f"Outcome check {outcome}: wrote evidence to {output}")
        return 0 if passed else 1
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
