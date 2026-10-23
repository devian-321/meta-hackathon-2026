# Local validation — October 23, 2026

Environment: macOS ARM64, Python 3.12.13, uv 0.10.10, pytest 8.4.2.

Commands executed from the deliverable folder:

```sh
UV_CACHE_DIR=../.cache/uv uv sync --locked --offline
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy
.venv/bin/pytest -W error
.venv/bin/faultline --help
```

Observed after review: locked environment current; lint/format passed; mypy reported no
issues in eight source files; **60 tests passed without warnings**; CLI help listed export
and verify. Pytest now treats warnings as errors by default.

An isolated temporary copy exported through `export_fault` was tested using this
environment's Python with `PYTHONPATH` pointing to the exported directory. The injected
regression produced **3 failed, 5 passed**, as expected. The source discount expression
remained unchanged. The runbook uses an explicit temporary root to keep pytest cache
writes in the exported folder.

The review also installed a fresh copy of the deliverable from `uv.lock` using cached
dependencies, without reusing the original virtualenv. Baseline quality checks and tests
passed. With only the pricing expression faulted, the harness stayed green and the full
suite failed only the three intended discount cases. This is a fresh-directory check,
not a clone of a published GitLab project.

API tests use httpx's synthetic transport. They exercise encoded project paths, missing
pagination headers, unsupported test-report pagination, incomplete/invalid payloads,
incorrect pipeline IDs/SHAs/links and safe HTTP errors. CLI tests exercise actual argument
parsing, success/failure reports, refusal to overwrite evidence, and unavailable API data.
Report tests simulate a failed second-file write and confirm no partial PASS is published.
Verifier tests cover valid outcomes and false-green cases including absent/skipped tests,
wrong commits, duplicate test identities and unsuccessful jobs/pipelines.

Both GitLab YAML files parsed as mappings with Ruby's YAML parser. Workflow suppression
is limited to duplicate push pipelines; manual/triggered branch runs are not suppressed
just because an MR is open. This was checked against the official workflow documentation,
not GitLab's authenticated CI lint service.

These results establish local behavior only. No Linux container, GitLab CI lint service,
hosted pipeline, native Duo session, clean remote clone, or published demo was tested.
