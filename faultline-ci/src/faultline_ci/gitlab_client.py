"""Read-only GitLab API adapter. No repair execution and no raw log export."""

from re import fullmatch
from typing import Any, cast
from urllib.parse import quote, urlsplit

import httpx

from faultline_ci.verifier import Pipeline, TestCase


class EvidenceError(RuntimeError):
    """Evidence could not be collected safely and completely."""


def _object(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise EvidenceError("GitLab returned an invalid evidence object")
    return cast(dict[str, Any], value)


def _objects(value: object) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise EvidenceError("GitLab returned an invalid evidence list")
    return [_object(item) for item in value]


def _text(value: object, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str) or (not value and not allow_empty):
        raise EvidenceError("GitLab returned invalid text in evidence")
    return value


def _integer(value: object, *, minimum: int = 1) -> int:
    if type(value) is not int or value < minimum:
        raise EvidenceError("GitLab returned an invalid evidence ID or count")
    return value


class GitLabClient:
    def __init__(self, client: httpx.Client, project: str) -> None:
        if not project or any(character.isspace() for character in project):
            raise EvidenceError("Project must be a GitLab project ID or namespace/path")
        self.client = client
        self.project = quote(project, safe="")

    def _get(self, path: str, **params: str | int) -> httpx.Response:
        try:
            response = self.client.get(path, params=params)
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            # Do not include exception bodies/headers, which may contain secrets.
            raise EvidenceError(
                f"GitLab request failed (HTTP {error.response.status_code}); "
                "check access and pipeline IDs"
            ) from None
        except httpx.RequestError:
            raise EvidenceError("GitLab connection failed; check network access") from None
        return response

    def _json(self, response: httpx.Response) -> object:
        try:
            return response.json()
        except ValueError:
            raise EvidenceError("GitLab returned invalid JSON evidence") from None

    def _pages(self, path: str) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for page in range(1, 101):
            response = self._get(path, per_page=100, page=page)
            payload = _objects(self._json(response))
            items.extend(payload)
            next_page = response.headers.get("x-next-page")
            if next_page and next_page != str(page + 1):
                raise EvidenceError("GitLab returned inconsistent evidence pagination")
            # On GitLab.com pagination headers can be omitted. A full page is not
            # proof of completion, so request the next one even without the header.
            if not next_page and len(payload) < 100:
                return items
        raise EvidenceError("Evidence pagination exceeded the safety limit")

    def pipeline(self, pipeline_id: int) -> Pipeline:
        _integer(pipeline_id)
        path = f"projects/{self.project}/pipelines/{pipeline_id}"
        data = _object(self._json(self._get(path)))
        observed_id = _integer(data.get("id"))
        project_id = _integer(data.get("project_id"))
        if observed_id != pipeline_id or (
            self.project.isdecimal() and project_id != int(self.project)
        ):
            raise EvidenceError("GitLab evidence does not match the requested pipeline/project")
        sha = _text(data.get("sha"))
        if not fullmatch(r"[0-9a-f]{40}", sha):
            raise EvidenceError("GitLab returned an invalid full commit SHA")
        url = _text(data.get("web_url"))
        self._validate_url(url, pipeline_id)
        jobs = self._pages(f"{path}/jobs")
        report = self._get(f"{path}/test_report", per_page=100, page=1)
        if report.headers.get("x-next-page"):
            raise EvidenceError("Paginated test reports are not supported in this MVP")
        payload = _object(self._json(report))
        tests: list[TestCase] = []
        for suite in _objects(payload.get("test_suites")):
            for case in _objects(suite.get("test_cases")):
                tests.append(
                    TestCase(
                        identity=(
                            _text(case.get("classname"), allow_empty=True),
                            _text(case.get("name")),
                        ),
                        status=_text(case.get("status")),
                    )
                )
        if len(tests) != _integer(payload.get("total_count"), minimum=0):
            raise EvidenceError("Test report is incomplete")
        sample_statuses: list[str] = []
        for job in jobs:
            if _text(job.get("name")) == "sample-test":
                sample_statuses.append(_text(job.get("status")))
        return Pipeline(
            project_id=project_id,
            pipeline_id=observed_id,
            sha=sha,
            ref=_text(data.get("ref")),
            status=_text(data.get("status")),
            url=url,
            tests=tuple(tests),
            test_job_statuses=tuple(sample_statuses),
        )

    def _validate_url(self, url: str, pipeline_id: int) -> None:
        try:
            parsed = urlsplit(url)
            valid = (
                parsed.scheme == "https"
                and parsed.hostname == self.client.base_url.host
                and parsed.port in {None, 443}
                and parsed.username is None
                and not parsed.query
                and not parsed.fragment
                and parsed.path.endswith(f"/-/pipelines/{pipeline_id}")
                and all(character.isprintable() and not character.isspace() for character in url)
            )
        except ValueError:
            valid = False
        if not valid:
            raise EvidenceError("GitLab returned an invalid pipeline evidence URL")
