# GitLab setup confined to this workspace

Target: `https://gitlab.com/student-group4903843/fault-cli`.
Authenticated Git access is working. The application and draft fault MR have been pushed.
The replacement token permits project, pipeline and job reads, CI linting, and project
updates. GitLab now explicitly requires account identity verification for both CI jobs
and Duo Agent Platform. See [the live status](GITLAB_LIVE_STATUS.md).

## Account verification required now

Open the [baseline pipeline](https://gitlab.com/student-group4903843/fault-cli/-/pipelines/2989734790),
choose **Verify my account**, and complete GitLab’s requested steps while signed in.
Do not send verification codes or payment information to the assistant. After verification,
create a fresh baseline pipeline; existing zero-job failures cannot establish test results.
[Official troubleshooting](https://docs.gitlab.com/ci/debugging/#error-identity-verification-is-required-in-order-to-run-ci-jobs).

The private parent group also contains another project. Publishing the group requires
the owner’s explicit approval; publishing only FaultLine is currently rejected by GitLab.

## Credential setup reference

For a legacy token, explicitly choose **Generate token → Legacy token**, then select
**read_api** and **write_repository**. These cover evidence reads and Git pushes; API writes are
not required for the initial workflow. Use a project-limited token if your account offers
one with those capabilities. Keep the token out of chat, shell arguments and Git URLs.
[GitLab token documentation](https://docs.gitlab.com/user/profile/personal_access_tokens/)

For a fine-grained token restricted to this project, the workflow needs **Code: Download
and Push**, **Repository: Read**, **Merge Request: Read**, **Project: Read**, **Pipeline:
Read**, and **Job: Read**. Git permissions and API permissions are separate: a successful
push does not prove that CI evidence can be read. CI Config: Validate is useful for server
linting but is not required by the recovery verifier.
[Git permissions](https://docs.gitlab.com/auth/tokens/fine_grained_access_tokens_other/),
[REST permissions](https://docs.gitlab.com/auth/tokens/fine_grained_access_tokens_rest/).

From this workspace's root, run in your own terminal:

```sh
python3 scripts/gitlab_workspace.py setup
```

Paste the token at the hidden prompt. The script checks project metadata when permitted,
saves the token with mode 0600, configures the checkout and fetches the exact repository.
A metadata-only 403 no longer blocks an otherwise permitted Git fetch; it is reported
separately. The default branch can be discovered through Git when metadata access is denied.
It never puts a token in a remote URL. No global Git config, SSH config, or system keychain
settings are changed.

Tell the assistant when setup completes. Do not send the token. If it fails, send only
the safe error message; HTTP 401/403/404 may mean scope, membership or URL issues.

## Local locations and boundaries

| Location | Purpose |
| --- | --- |
| `.local/gitlab/token` | Owner-readable token; ignored by Git |
| `.workspaces/fault-cli/` | Separate GitLab checkout; ignored by the outer GitHub repo |
| `.workspaces/fault-cli/.git/config` | Personal identity and helper settings for this checkout only |
| `scripts/gitlab_workspace.py` | Auditable setup/helper code; contains no credentials |

The helper returns credentials only for HTTPS `gitlab.com` and the exact project path.
It ignores store/erase requests and does not use a shared credential store. The token's
server-side permissions are determined by GitLab; a legacy personal token may cover
other projects the account can access even though this local helper refuses those paths.

To check connectivity without printing secrets:

```sh
python3 scripts/gitlab_workspace.py status
```

After access works, the assistant will inspect existing files and instructions, transfer
the deliverable without replacing unrelated work, test it, push the baseline, and observe
the real CI result. Native Duo access is a separate requirement; a working token alone
does not establish event provisioning, credits, runners, or foundational-flow availability.

## Local verification — October 26

The setup script passes Ruff and strict mypy. Sixteen setup tests cover private file
permissions, token rotation, exact host/project binding, ignored store/erase requests,
symlink refusal, redirect refusal, repository-local configuration, interrupted fetches
preservation of existing owner files, Git-only access when metadata scope is missing,
and default-branch discovery without metadata. Combined with the application suite, 97 tests
pass. Python 3.9 successfully runs the script's help command.

A source-only export is prepared under `.local/gitlab/faultline-ci-source.tar`, with its
commit and SHA256 in `source-manifest.json`. No credentials are included. Live GitLab
commits, the MR and failed pipeline summaries are recorded in `GITLAB_LIVE_STATUS.md`.
