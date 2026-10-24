# FaultLine CI

Reproduce a CI regression, review a GitLab Duo repair, and independently check the outcome.

**Status:** initial local implementation. Native Duo execution and hosted GitLab pipelines
have not yet been demonstrated. No public project/demo/video URL exists in this checkout.

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

JSON and Markdown reports contain pipeline links, commit IDs and test outcomes. They do
not export raw job logs or authorization headers. Review artifacts before publication.
With `--check-repair`, PASS also requires commit ancestry, unchanged repository objects
outside the pricing correction, and byte-for-byte agreement with the pinned broken and
healthy fixtures. The guard reads complete paginated inventories and validates raw blobs
against Git object IDs. It does not depend on potentially truncated textual diffs.
Without this flag, verification checks only pipeline/test outcomes. Duo session provenance
and approval still require separate review. This is not a general-purpose patch auditor.

Every report uses a new directory. An explicit `--output` directory must not exist; omit
the option to generate a unique directory under `reports/`. Existing evidence is never
overwritten, and both report files are staged before publication. The JSON distinguishes
the declared scenario from its checked or unchecked link to the remote pipeline.

## GitLab setup and delivery

Copy the **contents of this folder** to the canonical public GitLab project root so the
MIT license and `.gitlab-ci.yml` are detected. Do not push the outer Meta planning workspace.
Follow [the GitLab runbook](docs/gitlab-runbook.md), [implementation plan](docs/implementation-plan.md),
[current evidence ledger](docs/submission-notes.md) and [demo script](demo/script.md).

The implementation is MIT licensed; retain upstream dependency licenses. No employer code
or credentials are needed.
