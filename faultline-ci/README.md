# FaultLine CI

Reproduce a CI regression, review a GitLab Duo repair, and independently check the outcome.

**Repository:** [student-group4903843/fault-cli](https://gitlab.com/student-group4903843/fault-cli).

**Status:** tested application baseline. Native Duo execution and hosted GitLab pipeline
outcomes are not yet verified. The local rehearsal is scripted; no final video is published.

The sample application calculates discounted invoice totals in integer cents. A controlled
fault reverses the discount sign. The verifier reads GitLab pipeline/job/test evidence and
rejects missing tests, skipped tests, unchanged repair commits and unsuccessful pipelines.

## Local setup

Install Python 3.12 and uv 0.10.10, then from this folder in zsh/bash:

```sh
export UV_CACHE_DIR="$PWD/.cache/uv"
uv sync --locked
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
```

For fish, use `set -gx UV_CACHE_DIR "$PWD/.cache/uv"` in place of `export`.
The absolute cache path remains valid when changing directories. The committed lockfile
is the dependency source of truth.

## Run the viewable local demo

From this folder after setup:

```sh
uv run faultline local-demo --output reports/local-demo
```

Open `reports/local-demo/recovery.html` in your browser. The command creates a disposable
Git repository using your configured personal identity and runs actual pytest subprocesses:

| Stage | Expected result |
| --- | --- |
| Healthy baseline | 8 passing tests |
| Injected pricing fault | 5 passing, 3 failing tests |
| Scripted fixture restoration | 8 passing; repository guard accepts correction |
| Disabled pricing assertions | 8 passing; repository guard rejects false green |

This is a **scripted local rehearsal**, with no model invocation or hosted GitLab pipeline.
Your working branch and app remain unchanged. Output includes HTML, JSON, Markdown, JUnit
files and a cloneable `demo.bundle` preserving the actual local history. Existing report
directories are never overwritten; use another output name for the next run.
The local demo requires Git and your configured Git name/email; no remote or token is used.

A fresh [checked-in evidence report](demo/evidence/local-rehearsal-2026-10-27/recovery.md),
[HTML view](demo/evidence/local-rehearsal-2026-10-27/recovery.html) and
[walkthrough transcript](demo/local-walkthrough-transcript.txt) are available for review.
Download the HTML file to view it locally. The 99-second narrated walkthrough describes
this measured local evidence; it does not show a native Duo session.

## Reproduce the fault locally

Choose a new temporary path outside this checkout:

```sh
uv run faultline export-fault --destination /tmp/faultline-pricing-demo
cd /tmp/faultline-pricing-demo
PYTHONPATH=. /ABSOLUTE/PATH/TO/faultline-ci/.venv/bin/python -m pytest tests/test_sample_app.py -c /dev/null --rootdir=. --import-mode=importlib
```

Replace the absolute Python path with this project's `.venv/bin/python`. Run pytest
**from the exported folder** so it imports the broken app. See
[the runbook](docs/gitlab-runbook.md). The fault should fail three discount
assertions while the original checkout remains green. This is local simulation only.

## Read real recovery evidence

Once actual before/after pipelines exist:

```sh
uv run faultline verify --project NAMESPACE/PROJECT --before FAILED_PIPELINE_ID --after REPAIRED_PIPELINE_ID --expected-sha FULL_REPAIR_COMMIT_SHA --check-repair --output reports/incident-001
```

Arguments above are placeholders, not real evidence. Set `GITLAB_TOKEN` in your environment
if required for API access; use `read_api`, never a token embedded in the command or URL.
The client reads GitLab.com over HTTPS, does not follow redirects and does not write to GitLab.
Exit status: 0 for passing outcome checks, 1 for failed checks, 2 for unavailable evidence.

HTML, JSON and Markdown reports contain pipeline links, commit IDs and test outcomes. They do
not export raw job logs or authorization headers. Review artifacts before publication.
With `--check-repair`, PASS also requires commit ancestry, unchanged repository objects
outside the pricing correction, and byte-for-byte agreement with the pinned broken and
healthy fixtures. The guard reads complete paginated inventories and validates raw blobs
against Git object IDs. It does not depend on potentially truncated textual diffs.
Without this flag, verification checks only pipeline/test outcomes. Duo session provenance
and approval still require separate review. This is not a general-purpose patch auditor.

Every report uses a new directory. An explicit `--output` directory must not exist; omit
the option to generate a unique directory under `reports/`. Existing evidence is never
overwritten, and all bundle files are staged before publication. The JSON distinguishes
the declared scenario from its checked or unchecked link to the remote pipeline.

## GitLab setup and delivery

The canonical GitLab repository contains the application, MIT license, and CI configuration
at its root. When working from the outer planning workspace, the source is in `faultline-ci/`
and the separate GitLab checkout is in `.workspaces/fault-cli/`; credentials stay outside
the submission in ignored workspace storage. Public visibility and native Duo availability
must be checked in the real project before submission.
Follow [the GitLab runbook](docs/gitlab-runbook.md), [implementation plan](docs/implementation-plan.md),
[current evidence ledger](docs/submission-notes.md) and [demo script](demo/script.md).
The [submission checklist](docs/submission-checklist.md) and
[Devpost description](docs/devpost-submission.md) distinguish delivered behavior from
the live integration still blocked by GitLab account verification. A fresh, inspectable
[local evidence bundle](demo/evidence/local-rehearsal-2026-10-27/recovery.md) is included.

The implementation is MIT licensed; retain upstream dependency licenses. No employer code
or credentials are needed.
