# GitLab live integration — October 27, 2026

This records observed facts, not a claim of completed recovery.

## Actual project and source

- Project: [student-group4903843/fault-cli](https://gitlab.com/student-group4903843/fault-cli)
- Project ID: `88077531` (returned by the authorized merge-request API).
- Existing initial commit `7287be9` is preserved.
- Tested baseline on main: [`883529d`](https://gitlab.com/student-group4903843/fault-cli/-/commit/883529dee4a4aace33144a2709c4ad6d084a86f7).
- Controlled fault: [`17e25fa`](https://gitlab.com/student-group4903843/fault-cli/-/commit/17e25faefcd5894dc2e0adb3f4893bc2e1843181).
- Draft [MR !1](https://gitlab.com/student-group4903843/fault-cli/-/merge_requests/1), source
  `demo/pricing-discount-sign-v1`, target `main`. Do not merge the deliberately broken change.

The baseline was installed in a fresh, project-local virtualenv: Ruff, strict mypy and
all 81 application tests pass. The fault changes only discount subtraction to addition;
local tests show exactly 3 intended failures and 78 passes. Commits use the owner's
personal identity and sign-off. No assistant authorship or signing key was used.

## Hosted observations

| Pipeline | Commit/ref | Observed status | Evidence source |
| --- | --- | --- | --- |
| [2989734790](https://gitlab.com/student-group4903843/fault-cli/-/pipelines/2989734790) | Baseline main, `883529d` | Failed | Authorized commit API `last_pipeline` |
| [2989799426](https://gitlab.com/student-group4903843/fault-cli/-/pipelines/2989799426) | Fault branch, `17e25fa` | Failed | Authorized MR pipeline list |
| [2989799479](https://gitlab.com/student-group4903843/fault-cli/-/pipelines/2989799479) | MR head, `17e25fa` | Failed | Authorized MR head/list |

**The hosted baseline is not green.** The baseline jobs API returns an empty list.
CI lint with a dry-run of main returns HTTP 200, `valid: false`, and the exact error:
`Identity verification is required in order to run CI jobs`. No job has run, so these
failures are not evidence of the injected pricing regression.

## Replacement-token access and account blocker

The replacement owner credential successfully reads project metadata, pipeline details
and jobs, and validates CI configuration. Project updates reach GitLab validation rather
than the earlier permission denial. Another token is not currently required.

GitLab’s official Duo CLI 9.32.1 authenticates the owner and identifies this project, but
reports HTTP 403: `Identity verification is required to use GitLab Duo Agent Platform`.
No native agent session, diagnosis or repair has executed. Feature flags being enabled
are not evidence of account eligibility, credits or successful execution.

The owner must complete GitLab account verification through the pipeline’s **Verify my
account** action. Once complete, repeat CI simulation and start a fresh baseline pipeline.
See [GitLab’s official explanation](https://docs.gitlab.com/ci/debugging/#error-identity-verification-is-required-in-order-to-run-ci-jobs).

## Public visibility blocker

The project is private. Updating it to public returns HTTP 400:
`public is not allowed in a private namespace.` The top-level parent group is private
and also contains an unrelated private project. No parent visibility change was made.
Explicit owner approval is pending to publish the parent group and FaultLine while
keeping the other project private. Anonymous judge access is not yet established.

## Workspace boundaries

The credential stays in ignored `.local/gitlab/token`, mode 0600. It is absent from
source, history and remote URLs. The checkout and Git settings stay in
`.workspaces/fault-cli/`. Global Git, SSH and keychain configuration were not changed.

The official Darwin ARM64 Duo binary was downloaded into ignored `.local/gitlab/bin/`,
with its published package SHA256 verified before execution. Its configuration, storage,
cache, bundled executable extraction and temporary paths were redirected into ignored
`.local/gitlab/duo-runtime/`. The global installer was not run. No agent was allowed to
modify source files. Docker’s daemon is unavailable; no runner or global service was installed.

## Remaining delivery sequence

1. Owner completes account identity verification; assistant observes a fresh green baseline.
2. Run the controlled fault and establish its three actual hosted assertion failures.
3. Execute native Duo, review its proposal, record human approval, and observe a green rerun.
4. Run the independent verifier with `--check-repair` using real pipeline IDs and repair SHA.
5. Establish public repository and CI access after the namespace decision.
6. Record the functioning workflow and complete the video and Devpost submission.

The local rehearsal and false-green guard work. Native recovery, hosted test evidence,
public judge access, the final video and submission receipt remain pending. No recovery
percentage, Duo success or human approval is claimed without observed evidence.
