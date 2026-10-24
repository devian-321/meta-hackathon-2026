# Submission evidence ledger

Updated October 24, 2026. All hosted evidence fields remain empty until observed.

| Capability | State | Evidence |
| --- | --- | --- |
| Small invoice app and deterministic regression | Implemented locally | `sample_app/`, scenario exporter |
| Outcome checker and read-only GitLab adapter | Implemented locally | `src/faultline_ci/` |
| Local checks | Passed | 76 tests; Ruff lint/format; strict mypy |
| Commit ancestry, repair scope, scenario guard | Implemented; tested synthetically | `repair.py`, GitLab tree/blob/merge-base adapter; `--check-repair` |
| Isolated regression smoke test | Passed locally | 3 expected failures, 5 passes; original app unchanged |
| Fresh-directory setup and faulted checkout | Passed locally | Separate environment; harness remains green after pricing fault |
| Report integrity | Passed locally | Existing reports preserved; partial file writes do not publish PASS |
| GitLab pipeline configuration | Written; hosted execution pending | `.gitlab-ci.yml` |
| Native execution setup and repair instructions | Written; hosted execution pending | `.gitlab/duo/agent-config.yml`, `AGENTS.md` |
| Native Duo execution | Access unconfirmed | No session observed |
| Real failed/successful pipelines | Pending | No pipeline URLs observed |
| Review/approval and live causal evidence | Pending live run | Guard implemented; no repair MR observed |
| Public demo | Pending | No published demo URL |
| YouTube video under 3 minutes | Planned | `demo/script.md`; no video recorded |
| Final Devpost submission | Pending | No submission receipt observed |

Do not describe this increment as self-healing, autonomous, production-ready, or a measured
reliability improvement. Record what the final system actually demonstrates before writing
the final project story.
