# GitLab live integration — October 26, 2026

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

**The hosted baseline is not green.** Its failure cause has not been established. We
cannot attribute the hosted fault-pipeline failure to the pricing assertions until actual
job/test evidence is available. The MR head reports `yaml_errors: null`, but that does not
prove the jobs ran or that the entire runner/account configuration is valid.

## Access that works and access denied by GitLab

- Git fetch and push: succeeded using the owner-provided token.
- Repository tree, commit and merge-request reads: HTTP 200.
- Project metadata: HTTP 403, requires **Project: Read**.
- Pipeline details/test reports: HTTP 403, requires **Pipeline: Read**.
- Job details/logs: HTTP 403, requires **Job: Read**.
- Optional CI lint request: HTTP 403, requires **CI Config: Validate**.
- Public visibility update: HTTP 403, requires **Project: Update**; no setting was changed.
- Anonymous project metadata: HTTP 404. Public judge access is not established.

These are server-reported fine-grained permission restrictions. The credential is stored
only in ignored `.local/gitlab/token` with mode 0600; it is not in source, history,
remote URLs or a shared credential store. The checkout and its settings are confined to
`.workspaces/fault-cli/`. Global Git, SSH and keychain configuration were not changed.

## Next required evidence/actions

1. Read the baseline pipeline's actual error banner and job results. Add the missing read
   permissions using project-scoped fine-grained grants, or supply a legacy token with
   `read_api` and `write_repository` through the existing hidden setup prompt.
2. Fix any genuine baseline setup problem and observe green CI before recording a recovery.
   If no jobs run because the account/runner needs activation, complete that prerequisite;
   do not classify it as the injected pricing bug.
3. Establish public project/source/CI access for judges.
4. Confirm the native **Fix pipeline with Duo** action is available on MR !1. No native
   session or AI-generated repair has been observed yet. The flow is invoked in GitLab UI.
5. Review the native proposal, record human approval, observe actual green rerun, and run
   the independent verifier with `--check-repair` on the observed pipeline IDs/repair SHA.
6. Record the final functioning workflow and submit the video/repository/Devpost materials.

No recovery percentage, hosted test count, Duo success, approval or final submission is
claimed from these observations.
