# GitLab setup confined to this workspace

Target: `https://gitlab.com/student-group4903843/fault-cli`.
The unauthenticated Git check required credentials. This does not establish whether
the project is private, membership is missing, or the URL needs correction.

## One-time owner action

Create a short-lived GitLab personal access token with **read_api** and
**write_repository** scopes. These cover evidence reads and Git pushes; API writes are
not required for the initial workflow. Use a project-limited token if your account offers
one with those capabilities. Keep the token out of chat, shell arguments and Git URLs.
[GitLab token documentation](https://docs.gitlab.com/user/profile/personal_access_tokens/)

From this workspace's root, run in your own terminal:

```sh
python3 scripts/gitlab_workspace.py setup
```

Paste the token at the hidden prompt. The script checks the exact project through the
GitLab API, saves the token with mode 0600, configures the checkout and fetches its contents.
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

The setup script passes Ruff and strict mypy. Fourteen setup tests cover private file
permissions, token rotation, exact host/project binding, ignored store/erase requests,
symlink refusal, redirect refusal, repository-local configuration, interrupted fetches
and preservation of existing owner files. Combined with the application suite, 95 tests
pass. Python 3.9 successfully runs the script's help command.

A source-only export is prepared under `.local/gitlab/faultline-ci-source.tar`, with its
commit and SHA256 in `source-manifest.json`. No credentials are included. No live token,
authenticated checkout, GitLab push or pipeline has been observed yet.
