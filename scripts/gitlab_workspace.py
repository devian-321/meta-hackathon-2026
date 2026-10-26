"""Set up this workspace's GitLab checkout without global credential changes.

Run `python3 scripts/gitlab_workspace.py setup` in your own terminal. Secrets are
prompted without echo and are never accepted as command-line arguments.
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
import shlex
import stat
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[1]
PROJECT = "student-group4903843/fault-cli"
REMOTE = f"https://gitlab.com/{PROJECT}.git"


class SetupError(RuntimeError):
    """An actionable error safe to display without credential material."""


class ProjectReadDenied(SetupError):
    """A token may permit Git while lacking project-metadata API access."""


class NoRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args: Any, **kwargs: Any) -> None:
        return None


def _private_directory(path: Path) -> None:
    if path.is_symlink():
        raise SetupError("Local credential directories must not be symlinks")
    path.mkdir(parents=True, exist_ok=True)
    path.chmod(0o700)


def token_path() -> Path:
    return WORKSPACE / ".local/gitlab/token"


def read_token() -> str:
    path = token_path()
    if (
        path.is_symlink()
        or path.parent.is_symlink()
        or path.parent.parent.is_symlink()
        or not path.is_file()
    ):
        raise SetupError("No project-local token; run the setup command first")
    if stat.S_IMODE(path.stat().st_mode) & 0o077:
        raise SetupError("Credential permissions must be 0600; fix the local token file")
    token = path.read_text().strip()
    if not token or any(character.isspace() for character in token):
        raise SetupError("The project-local token is empty or malformed")
    return token


def store_token(token: str) -> None:
    local = WORKSPACE / ".local"
    _private_directory(local)
    _private_directory(local / "gitlab")
    if token_path().is_symlink():
        raise SetupError("The token path must not be a symlink")
    descriptor, temporary = tempfile.mkstemp(prefix=".token-", dir=local / "gitlab")
    try:
        with os.fdopen(descriptor, "w") as stream:
            stream.write(token + "\n")
        os.replace(temporary, token_path())
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def project_details(token: str) -> dict[str, Any]:
    url = f"https://gitlab.com/api/v4/projects/{urllib.parse.quote(PROJECT, safe='')}"
    request = urllib.request.Request(url, headers={"PRIVATE-TOKEN": token})
    opener = urllib.request.build_opener(NoRedirects())
    try:
        with opener.open(request, timeout=25) as response:
            data = json.load(response)
    except urllib.error.HTTPError as error:
        if error.code == 403:
            raise ProjectReadDenied(
                "Project metadata API denied; fine-grained tokens need Project: Read"
            ) from None
        raise SetupError(
            f"GitLab returned HTTP {error.code}; check project membership and read_api scope"
        ) from None
    except (urllib.error.URLError, TimeoutError, ValueError):
        raise SetupError("GitLab API request failed; check network access and retry") from None
    if not isinstance(data, dict) or data.get("path_with_namespace") != PROJECT:
        raise SetupError("The API response does not identify the expected GitLab project")
    return data


def _git(directory: Path, *arguments: str) -> str:
    environment = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    environment.update(
        {
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_TERMINAL_PROMPT": "0",
        }
    )
    try:
        result = subprocess.run(
            ["git", "-C", str(directory), *arguments],
            env=environment,
            capture_output=True,
            text=True,
            timeout=90,
        )
    except subprocess.TimeoutExpired:
        raise SetupError(
            "GitLab Git operation timed out; retry after checking network access"
        ) from None
    if result.returncode:
        raise SetupError("Git operation failed; check repository access and write_repository scope")
    return result.stdout.strip()


def configure_checkout(details: dict[str, Any]) -> Path:
    checkout = WORKSPACE / ".workspaces/fault-cli"
    if checkout.is_symlink() or checkout.parent.is_symlink():
        raise SetupError("GitLab checkout directories must not be symlinks")
    fresh = not checkout.exists()
    if not fresh and ((checkout / ".git").is_symlink() or not (checkout / ".git").is_dir()):
        raise SetupError(
            "Checkout directory already contains unrelated files; preserve it for review"
        )
    if fresh:
        checkout.mkdir(parents=True)
        _git(checkout, "init", "-b", "main")
        _git(checkout, "remote", "add", "origin", REMOTE)
    elif _git(checkout, "remote", "get-url", "origin") != REMOTE:
        raise SetupError("Existing checkout points to another remote; refusing to change it")
    name = _git(WORKSPACE, "config", "--local", "user.name")
    email = _git(WORKSPACE, "config", "--local", "user.email")
    helper = (
        f"!{shlex.quote(sys.executable)} {shlex.quote(str(Path(__file__).resolve()))} credential"
    )
    for key, value in (
        ("user.name", name),
        ("user.email", email),
        ("credential.useHttpPath", "true"),
        ("credential.helper", ""),
    ):
        _git(checkout, "config", "--local", "--replace-all", key, value)
    _git(checkout, "config", "--local", "--add", "credential.helper", helper)
    _git(checkout, "fetch", "origin")
    default = details.get("default_branch")
    if not isinstance(default, str) or not default:
        for line in _git(checkout, "ls-remote", "--symref", "origin", "HEAD").splitlines():
            if line.startswith("ref: refs/heads/") and line.endswith("\tHEAD"):
                default = line.split("\t", 1)[0].removeprefix("ref: refs/heads/")
                break
    local_branches = _git(checkout, "for-each-ref", "--format=%(refname)", "refs/heads")
    has_owner_files = any(path.name != ".git" for path in checkout.iterdir())
    empty_retry = not local_branches and not has_owner_files
    if (fresh or empty_retry) and isinstance(default, str) and default:
        # Fresh checkout or interrupted first fetch: no owner files/branches exist.
        _git(checkout, "checkout", "-B", default, f"origin/{default}")
    return checkout


def credential(action: str) -> None:
    if action != "get":
        return  # Never write to a system helper/keychain on store or erase.
    fields = dict(line.rstrip("\n").split("=", 1) for line in sys.stdin if "=" in line)
    if fields.get("protocol") != "https" or fields.get("host") != "gitlab.com":
        return
    if fields.get("path") not in {PROJECT, f"{PROJECT}.git"}:
        return
    # Git consumes this pipe privately. The interactive setup/status commands never
    # print a token, and this helper refuses every other host and project path.
    sys.stdout.write(f"username=oauth2\npassword={read_token()}\n\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("setup", "status", "credential"))
    parser.add_argument("action", nargs="?")
    args = parser.parse_args()
    try:
        if args.command == "credential":
            credential(args.action or "")
            return 0
        if args.command == "setup":
            if not sys.stdin.isatty():
                raise SetupError(
                    "Run setup in your own interactive terminal; do not paste a token in chat"
                )
            token = getpass.getpass("GitLab token (hidden; repository access required): ").strip()
            if not token or any(character.isspace() for character in token):
                raise SetupError("Empty or malformed token; nothing was saved")
            metadata_error = None
            try:
                details = project_details(token)
            except ProjectReadDenied as error:
                # Git read/write and metadata read are separate fine-grained grants.
                # Do not block a legitimate Git checkout on an unrelated API grant.
                metadata_error = str(error)
                details = {"path_with_namespace": PROJECT}
            store_token(token)
            checkout = configure_checkout(details)
            print(f"Authenticated checkout ready: {checkout}")
            print("Only workspace credential files and checkout-local Git settings were changed.")
            if metadata_error:
                print(metadata_error)
        else:
            details = project_details(read_token())
        print(
            json.dumps(
                {
                    key: details.get(key)
                    for key in (
                        "id",
                        "path_with_namespace",
                        "visibility",
                        "default_branch",
                        "empty_repo",
                        "shared_runners_enabled",
                        "group_runners_enabled",
                        "builds_access_level",
                        "web_url",
                        "permissions",
                    )
                },
                indent=2,
            )
        )
        return 0
    except (SetupError, OSError) as failure:
        # OSError paths and exception bodies are intentionally not printed.
        message = str(failure) if isinstance(failure, SetupError) else "Local file operation failed"
        parser.exit(2, f"Setup incomplete: {message}\n")


if __name__ == "__main__":
    raise SystemExit(main())
