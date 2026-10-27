# Submission evidence ledger

Updated October 27, 2026. Only observed results are recorded below.

| Capability | State | Evidence |
| --- | --- | --- |
| Small invoice app and deterministic regression | Implemented locally | `sample_app/`, scenario exporter |
| Outcome checker and read-only GitLab adapter | Implemented locally | `src/faultline_ci/` |
| Local checks | Passed | 81 tests; Ruff lint/format; strict mypy |
| Commit ancestry, repair scope, scenario guard | Implemented; tested synthetically | `repair.py`, GitLab tree/blob/merge-base adapter; `--check-repair` |
| Isolated regression smoke test | Passed locally | 3 expected failures, 5 passes; original app unchanged |
| Fresh-directory setup and faulted checkout | Passed locally | Separate environment; harness remains green after pricing fault |
| Report integrity | Passed locally | Existing reports preserved; partial file writes do not publish PASS |
| Viewable local rehearsal | Implemented and executed | `faultline local-demo`; actual Git/pytest, scripted repair, false-green rejection, HTML report and Git bundle |
| GitLab pipeline configuration | Pushed; account verification blocks jobs | Baseline pipeline 2989734790 has zero jobs; CI dry-run returns identity-verification error |
| Native execution setup and repair instructions | Written; hosted execution pending | `.gitlab/duo/agent-config.yml`, `AGENTS.md` |
| Native Duo execution | Blocked by account verification | Official Duo CLI 9.32.1 authenticates but returns identity-verification-required HTTP 403; no session executed |
| Real failed/successful pipelines | Pipelines created; no jobs executed | [Baseline 2989734790](https://gitlab.com/student-group4903843/fault-cli/-/pipelines/2989734790), [fault MR 2989799479](https://gitlab.com/student-group4903843/fault-cli/-/pipelines/2989799479); neither establishes test outcomes |
| Review/approval and live causal evidence | Pending live run | Guard implemented; no repair MR observed |
| Public demo | Pending | No published demo URL |
| YouTube video under 3 minutes | Local narrated evidence walkthrough rendered; not uploaded | 99.37s H.264/AAC MP4; scripted-local scope visible throughout; no hosted agent recording |
| Final Devpost submission | Pending | No submission receipt observed |

The fresh [local evidence bundle](../demo/evidence/local-rehearsal-2026-10-27/recovery.md)
contains four real pytest runs and disposable Git history. Its local commit IDs are not
hosted pipeline SHAs. All eight sample tests pass before injection, exactly three fail
after injection, all eight pass after scripted restoration, and a false green obtained
by disabling assertions is rejected by the independent guard.

Repository: [FaultLine](https://gitlab.com/student-group4903843/fault-cli).
Baseline commit `883529dee4a4aace33144a2709c4ad6d084a86f7`; fault commit
`17e25faefcd5894dc2e0adb3f4893bc2e1843181`; draft
[MR !1](https://gitlab.com/student-group4903843/fault-cli/-/merge_requests/1).
The project is private. Its parent group must allow public visibility first; owner approval
is pending because that group also contains another private project.

Submission copy and the remaining owner actions are in [the checklist](submission-checklist.md).

Do not describe this increment as self-healing, autonomous, production-ready, or a measured
reliability improvement. Record what the final system actually demonstrates before writing
the final project story.
