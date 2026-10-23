import json
from pathlib import Path

import httpx
import pytest

from faultline_ci.cli import main


@pytest.fixture
def api(monkeypatch: pytest.MonkeyPatch) -> list[httpx.Request]:
    """Use synthetic API responses; these tests do not establish live GitLab access."""
    requests: list[httpx.Request] = []
    real_client = httpx.Client

    def respond(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        suffix = request.url.path.split("/pipelines/")[-1]
        pipeline_id = int(suffix.split("/")[0])
        status = "failed" if pipeline_id == 10 else "success"
        if suffix.endswith("/jobs"):
            return httpx.Response(200, json=[{"name": "sample-test", "status": status}])
        if suffix.endswith("/test_report"):
            return httpx.Response(
                200,
                json={
                    "total_count": 1,
                    "test_suites": [
                        {
                            "test_cases": [
                                {"classname": "pricing", "name": "discount", "status": status},
                            ]
                        }
                    ],
                },
            )
        return httpx.Response(
            200,
            json={
                "id": pipeline_id,
                "project_id": 1,
                "sha": ("a" if pipeline_id == 10 else "b") * 40,
                "ref": "demo/fault",
                "status": status,
                "web_url": f"https://gitlab.com/group/repo/-/pipelines/{pipeline_id}",
            },
        )

    def client(**kwargs: object) -> httpx.Client:
        return real_client(**kwargs, transport=httpx.MockTransport(respond))

    monkeypatch.setattr(httpx, "Client", client)
    return requests


def arguments(output: Path, *, sha: str = "b" * 40) -> list[str]:
    return [
        "verify",
        "--project",
        "group/repo",
        "--before",
        "10",
        "--after",
        "11",
        "--expected-sha",
        sha,
        "--output",
        str(output),
    ]


def test_successful_outcome_exports_explicit_limits(
    api: list[httpx.Request],
    tmp_path: Path,
) -> None:
    output = tmp_path / "incident"
    assert main(arguments(output)) == 0
    report = json.loads((output / "recovery.json").read_text())
    assert report["verification"]["passed"] is True
    for field in (
        "duo_provenance",
        "scenario_linkage",
        "approval",
        "patch_safety",
        "commit_ancestry",
    ):
        assert report[field] == "not_checked"
    assert "outcome check: PASS" in (output / "recovery.md").read_text()
    assert len(api) == 6


def test_failed_outcome_is_recorded_with_failure_status(
    api: list[httpx.Request],
    tmp_path: Path,
) -> None:
    output = tmp_path / "incident"
    assert main(arguments(output, sha="c" * 40)) == 1
    assert not json.loads((output / "recovery.json").read_text())["verification"]["passed"]


def test_existing_evidence_is_never_overwritten(
    api: list[httpx.Request],
    tmp_path: Path,
) -> None:
    output = tmp_path / "incident"
    output.mkdir()
    previous = output / "recovery.json"
    previous.write_text("previous evidence")
    with pytest.raises(SystemExit) as raised:
        main(arguments(output))
    assert raised.value.code == 2
    assert previous.read_text() == "previous evidence"
    assert not api


def test_api_failure_does_not_publish_a_report(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    real_client = httpx.Client
    monkeypatch.setattr(
        httpx,
        "Client",
        lambda **kwargs: real_client(
            **kwargs,
            transport=httpx.MockTransport(lambda _: httpx.Response(403)),
        ),
    )
    output = tmp_path / "incident"
    with pytest.raises(SystemExit) as raised:
        main(arguments(output))
    assert raised.value.code == 2
    assert not output.exists()


def test_export_command_reports_actionable_input_error(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    with pytest.raises(SystemExit) as raised:
        main(["export-fault", "--source", str(tmp_path), "--destination", str(tmp_path)])
    assert raised.value.code == 2
    assert "outside the source checkout" in capsys.readouterr().err


@pytest.mark.parametrize(
    ("option", "value"),
    [
        ("--before", "0"),
        ("--after", "-1"),
        ("--expected-sha", "z" * 40),
    ],
)
def test_invalid_arguments_fail_before_any_api_request(
    api: list[httpx.Request],
    tmp_path: Path,
    option: str,
    value: str,
) -> None:
    command = arguments(tmp_path / "incident")
    command[command.index(option) + 1] = value
    with pytest.raises(SystemExit) as raised:
        main(command)
    assert raised.value.code == 2
    assert not api
