import importlib.util
import io
import stat
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[1] / "scripts/gitlab_workspace.py"
spec = importlib.util.spec_from_file_location("gitlab_workspace", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@pytest.fixture
def workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(module, "WORKSPACE", tmp_path)
    return tmp_path


def test_credential_is_private_and_round_trips(workspace: Path) -> None:
    module.store_token("fixture-token")
    assert module.read_token() == "fixture-token"
    for name, expected in (
        (".local", 0o700),
        (".local/gitlab", 0o700),
        (".local/gitlab/token", 0o600),
    ):
        assert stat.S_IMODE((workspace / name).stat().st_mode) == expected


def test_world_readable_token_is_rejected(workspace: Path) -> None:
    module.store_token("fixture-token")
    (workspace / ".local/gitlab/token").chmod(0o644)
    with pytest.raises(module.SetupError, match="permissions"):
        module.read_token()


def test_token_rotation_is_private(workspace: Path) -> None:
    module.store_token("old-fixture")
    module.store_token("new-fixture")
    assert module.read_token() == "new-fixture"
    assert list((workspace / ".local/gitlab").iterdir()) == [workspace / ".local/gitlab/token"]


@pytest.mark.parametrize(
    ("host", "path", "action"),
    [
        ("github.com", module.PROJECT, "get"),
        ("gitlab.com", "another/project.git", "get"),
        ("gitlab.com", module.PROJECT, "store"),
        ("gitlab.com", module.PROJECT, "erase"),
    ],
)
def test_helper_never_returns_token_outside_exact_project(
    workspace: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
    host: str,
    path: str,
    action: str,
) -> None:
    module.store_token("fixture-token")
    monkeypatch.setattr(
        module.sys,
        "stdin",
        io.StringIO(f"protocol=https\nhost={host}\npath={path}\n\n"),
    )
    module.credential(action)
    assert capsys.readouterr().out == ""


def test_helper_serves_only_the_expected_git_request(
    workspace: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
) -> None:
    module.store_token("fixture-token")
    monkeypatch.setattr(
        module.sys,
        "stdin",
        io.StringIO(
            f"protocol=https\nhost=gitlab.com\npath={module.PROJECT}.git\n\n",
        ),
    )
    module.credential("get")
    assert capsys.readouterr().out == "username=oauth2\npassword=fixture-token\n\n"


def test_symlink_directory_cannot_redirect_token_outside_workspace(
    workspace: Path,
) -> None:
    outside = workspace / "outside"
    outside.mkdir()
    (workspace / ".local").symlink_to(outside, target_is_directory=True)
    with pytest.raises(module.SetupError, match="symlinks"):
        module.store_token("fixture-token")
    assert list(outside.iterdir()) == []


def test_token_symlink_is_rejected(workspace: Path) -> None:
    module.store_token("fixture-token")
    token = workspace / ".local/gitlab/token"
    token.unlink()
    outside = workspace / "other"
    outside.write_text("original")
    token.symlink_to(outside)
    with pytest.raises(module.SetupError, match="symlink"):
        module.store_token("fixture-token")
    assert outside.read_text() == "original"


def test_no_cross_host_api_redirects() -> None:
    assert (
        module.NoRedirects().redirect_request(None, None, 302, "", {}, "https://other.example")
        is None
    )


def test_git_configuration_commands_are_repository_local(
    workspace: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    checkout = workspace / ".workspaces/fault-cli"
    calls = []

    def git(directory: Path, *arguments: str) -> str:
        calls.append((directory, arguments))
        if arguments == ("config", "--local", "user.name"):
            return "Owner Fixture"
        if arguments == ("config", "--local", "user.email"):
            return "fixture@example.invalid"
        return ""

    monkeypatch.setattr(module, "_git", git)
    assert module.configure_checkout({"default_branch": None}) == checkout
    configs = [args for _, args in calls if args[0] == "config"]
    assert configs and all("--local" in args for args in configs)
    assert not any("--global" in args or "--system" in args for _, args in calls)
    helpers = [args for args in configs if "credential.helper" in args]
    assert helpers[0][-1] == ""
    assert helpers[1][-1].endswith("credential")


@pytest.mark.parametrize("has_owner_files", [False, True])
def test_interrupted_fetch_can_resume_without_replacing_owner_files(
    workspace: Path,
    monkeypatch: pytest.MonkeyPatch,
    has_owner_files: bool,
) -> None:
    checkout = workspace / ".workspaces/fault-cli"
    (checkout / ".git").mkdir(parents=True)
    if has_owner_files:
        (checkout / "keep.txt").write_text("owner work")
    calls = []

    def git(directory: Path, *arguments: str) -> str:
        calls.append(arguments)
        if arguments == ("remote", "get-url", "origin"):
            return module.REMOTE
        if arguments == ("config", "--local", "user.name"):
            return "Owner Fixture"
        if arguments == ("config", "--local", "user.email"):
            return "fixture@example.invalid"
        return ""

    monkeypatch.setattr(module, "_git", git)
    module.configure_checkout({"default_branch": "main"})
    switched = any(args[0] == "checkout" for args in calls)
    assert switched is not has_owner_files
    if has_owner_files:
        assert (checkout / "keep.txt").read_text() == "owner work"
