# Submission checklist — October 27, 2026

Deadline: **13:00 UTC / 18:30 IST**. Aim to submit by **18:00 IST** and use the remaining
time to check the receipt and anonymous links. Requirements and deadline:
[event overview](https://gitlab-transcend.devpost.com/),
[official rules](https://gitlab-transcend.devpost.com/rules).

## Owner actions that remain necessary

- Complete GitLab's **Verify my account** action on the baseline pipeline page. The
  credential works; verification blocks hosted jobs and native Duo.
- Decide whether to publish the private parent group and FaultLine while keeping the
  other project private. No group setting will be changed without that decision.
- Upload the reviewed video to YouTube and supply its URL. Check that judges can watch
  without signing in; use the visibility required by the submission form and rules.
- Sign in to Devpost, enter the project description and real links, select the actual
  path/autonomy level, complete declarations and press the final submit button.
- Confirm the submission appears as submitted to this hackathon, rather than only saved
  as a portfolio draft. Retain its project URL and confirmation screenshot privately.

## Engineering work and evidence

- [x] Healthy local application: 81 tests, Ruff and strict mypy.
- [x] Workspace authentication/setup: 16 further tests; credentials outside submission.
- [x] Baseline and controlled fault pushed; draft MR !1 preserves the broken scenario.
- [x] Fresh real local rehearsal: JUnit, HTML/JSON/Markdown and cloneable Git history.
- [x] Independent guard accepts the correction and rejects disabled assertions.
- [x] Root MIT license and reproducible dependency lockfile in the GitLab application.
- [x] Narrated local evidence walkthrough rendered: 99.37 seconds, 1280×720 MP4, captions.
  This is a local fallback and does not demonstrate native Duo execution.
- [ ] Fresh hosted baseline succeeds after account verification.
- [ ] Hosted fault fails for the intended three pricing assertions.
- [ ] Native Duo actually diagnoses/proposes the correction; session evidence retained.
- [ ] Human reviews/approves the proposal; actual repaired pipeline succeeds.
- [ ] Live independent verifier passes on real pipeline IDs and the expected repair SHA.
- [ ] Repository, source, MIT license and CI history visible while signed out.
- [ ] Video under three minutes, uploaded and watchable by judges.
- [ ] Devpost submission completed and receipt checked.

Configured Duo integration and scripted local repairs do not replace actual Duo use.
The event requires Duo Agent Platform, visible automation history and a demo video.
Submit an accurate prototype description if any live evidence remains missing; do not
present planned behavior as a completed demonstration or assume it meets eligibility.

## Material ready to use

- [Copy-ready description](devpost-submission.md).
- [Evidence ledger](submission-notes.md).
- [Recording sequence and fallback](../demo/script.md).
- [Fresh local report](../demo/evidence/local-rehearsal-2026-10-27/recovery.html).
- [Machine-readable evidence](../demo/evidence/local-rehearsal-2026-10-27/recovery.json).

The local evidence commits live in the bundled disposable Git history, not in the hosted
MR. To inspect them, clone `demo/evidence/local-rehearsal-2026-10-27/demo.bundle` into a
new directory. Do not use those local SHAs as GitLab pipeline commit IDs.

## Freeze and continue safely

Immediately before submission, record the exact GitLab main SHA, video URL and Devpost
project URL in a private receipt. Preserve a local Git bundle and a lightweight submission
tag for that commit. Do not label a commit submitted before the actual submission occurs.

After the deadline, preserve submitted source, links, video and evidence during judging.
Continue development in a separate copy/branch without changing what judges evaluate.
The rules prohibit changes to the hackathon submission after the submission period;
later development does not retroactively complete the submitted entry. See section 5 of
the official rules. Do not merge the deliberately broken fault branch into main.
