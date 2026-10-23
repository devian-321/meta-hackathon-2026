# GitLab integration runbook

## Access prerequisites

Complete [Transcend onboarding](https://contributors.gitlab.com/transcend-hackathon).
Confirm the provisioned project URL and Developer + AI role. Verify runner availability,
credits, foundational flows, and Fix CI/CD Pipeline enabled in the top-level group.
Refer to [the official repair guide](https://docs.gitlab.com/ci/pipelines/fix_pipeline/).

The current working folder is staged inside a Meta GitHub repository. Transfer this folder's
contents into the provisioned GitLab project's checkout. Inspect its README/default branch
first; preserve provisioning assets. Set a confirmed personal identity locally before
creating commits. Do not change global settings or use the work email inadvertently.

## Baseline and incident

1. At the canonical project root, run locked install and all README checks.
2. Commit the clean app, harness, lockfile, CI config, license and documentation with DCO
   sign-off using the owner's confirmed identity. Push through the existing authorized remote.
3. Observe a green default-branch pipeline. Save URL, full SHA, and sample JUnit evidence.
4. Create `demo/pricing-discount-sign-v1` from that clean baseline.
5. In `sample_app/pricing.py`, change only `(100 - discount_percent)` to
   `(100 + discount_percent)`. Keep tests and CI untouched.
6. Push branch and open a draft MR. Record pipeline URL/SHA. Confirm `sample-test` fails
   with the expected pricing assertions and JUnit still uploads.

## Native Duo execution

On the MR's failing pipeline, select **Fix pipeline with Duo**. Monitor **AI > Sessions**.
Capture session URL, diagnosis, proposed suggestions or repair MR. The exact output depends
on pipeline context and GitLab version. If the flow cannot fix it, capture the actual
limitation; do not claim automated recovery from a manual replacement.

Review the proposal. Only `sample_app/pricing.py` is within this scenario's repair scope.
Reject changes to tests, CI, verifier, dependencies or instruction files. Record reviewer,
decision, timestamp and exact proposed commit/diff. Approve/apply the valid suggestion.
Never merge the intentionally broken branch into main to manufacture a red baseline.

Observe the new real pipeline and expected full SHA. Collect API evidence using the README
command. Also record the session/approval/MR links in the final incident manifest; these
are currently a manual companion to the outcome report.

## Local isolated fault check

Use the README's environment setup first, then run the exporter from the project root with
a new destination. Use an absolute Python
path to avoid importing the clean app from the source checkout:

```sh
uv run faultline export-fault --destination /tmp/faultline-pricing-demo
cd /tmp/faultline-pricing-demo
PYTHONPATH=. /ABSOLUTE/PATH/TO/faultline-ci/.venv/bin/python -m pytest tests/test_sample_app.py -c /dev/null --rootdir=. --import-mode=importlib
```

Expected exit status: 1, three failing discount cases and five passing cases. This is a
local scenario check, not evidence of a hosted GitLab pipeline or Duo run.

## Final incident evidence checklist

- Scenario ID and fixture version; baseline/failing/repaired SHAs and pipeline URLs.
- Failure assertion and original JUnit test identities.
- Native Duo session, diagnosis and proposed repair URL.
- Reviewed patch, approval record and unchanged test/CI/verifier files.
- Repair ancestry and successful rerun on intended SHA.
- Timestamped outcome JSON/Markdown; explicit real vs synthetic provenance.
- Reproduction commands, limitations and access-free links for judges.

Do not store raw secrets or entire logs without review. Pin final evidence to exact commits.
Use a fresh `--output` directory for each collection; existing reports cannot be replaced.
After submission, leave linked assets unchanged until judging finishes; continue in a copy.
