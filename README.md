# FaultLine hackathon workspace

Current priority: **FaultLine CI for GitLab Life After Code**, due October 27, 2026,
18:30 IST. This repository began as a Meta placeholder; its existing GitHub remote is
unchanged. The canonical GitLab submission will use the contributor-provisioned project.

- [Research and three-event delivery plan](docs/HACKATHON_PLAN.md)
- [FaultLine CI implementation and setup](faultline-ci/README.md)
- [GitLab integration runbook](faultline-ci/docs/gitlab-runbook.md)
- [Workspace-local GitLab authentication setup](docs/GITLAB_SETUP.md)
- [Observed GitLab commits, MR and CI status](docs/GITLAB_LIVE_STATUS.md)
- [Local validation results](faultline-ci/docs/validation.md)
- [Review findings and corrections](docs/REVIEW_2026-10-23.md)
- [Submission evidence ledger](faultline-ci/docs/submission-notes.md)
- [Demo recording script](faultline-ci/demo/script.md)
- [Original owner handoff](CODEX_HANDOFF_FAULTLINE.md)

The tested baseline and controlled fault are pushed to the GitLab project, with a draft MR.
Hosted pipelines stop before creating jobs because GitLab requires account identity
verification. The replacement token permits CI evidence reads. Native Duo also reports
that identity verification is required. The local rehearsal and false-green guard work. Native Duo recovery,
a published demo and a video remain pending. Lexsi implementation
follows the GitLab sprint; Meta remains conditional on acceptance and final rules.
