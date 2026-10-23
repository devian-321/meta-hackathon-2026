import httpx
import pytest

from faultline_ci.gitlab_client import EvidenceError, GitLabClient


def pipeline_data(**changes: object) -> dict[str, object]:
    return {
        "id": 11,
        "project_id": 1,
        "sha": "b" * 40,
        "ref": "demo/fault",
        "status": "success",
        "web_url": "https://gitlab.com/group/repo/-/pipelines/11",
        **changes,
    }


def test_reads_encoded_project_and_all_job_pages() -> None:
    requests: list[httpx.Request] = []

    def respond(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        assert "group%2Frepo" in request.url.raw_path.decode()
        if request.url.path.endswith("/jobs"):
            if request.url.params["page"] == "1":
                return httpx.Response(200, json=[], headers={"x-next-page": "2"})
            return httpx.Response(200, json=[{"name": "sample-test", "status": "success"}])
        if request.url.path.endswith("/test_report"):
            return httpx.Response(
                200,
                json={
                    "total_count": 1,
                    "test_suites": [
                        {
                            "test_cases": [
                                {"classname": "pricing", "name": "discount", "status": "success"},
                            ]
                        }
                    ],
                },
            )
        return httpx.Response(
            200,
            json={
                "id": 11,
                "project_id": 1,
                "sha": "b" * 40,
                "ref": "demo/fault",
                "status": "success",
                "web_url": "https://gitlab.com/group/repo/-/pipelines/11",
            },
        )

    with httpx.Client(
        base_url="https://gitlab.com/api/v4/",
        transport=httpx.MockTransport(respond),
    ) as http:
        result = GitLabClient(http, "group/repo").pipeline(11)
    assert result.test_job_statuses == ("success",)
    assert result.tests[0].identity == ("pricing", "discount")
    assert len(requests) == 4


@pytest.mark.parametrize("status", [302, 401, 403, 404, 429, 500])
def test_api_errors_do_not_expose_response_body(status: int) -> None:
    with (
        httpx.Client(
            base_url="https://gitlab.com/api/v4/",
            transport=httpx.MockTransport(lambda _: httpx.Response(status, text="SECRET")),
        ) as http,
        pytest.raises(EvidenceError) as raised,
    ):
        GitLabClient(http, "group/repo").pipeline(11)
    assert "SECRET" not in str(raised.value)


def test_incomplete_test_report_is_rejected() -> None:
    def respond(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/jobs"):
            return httpx.Response(200, json=[])
        if request.url.path.endswith("/test_report"):
            return httpx.Response(200, json={"total_count": 1, "test_suites": []})
        return httpx.Response(200, json=pipeline_data())

    with (
        httpx.Client(
            base_url="https://gitlab.com/api/v4/",
            transport=httpx.MockTransport(respond),
        ) as http,
        pytest.raises(EvidenceError, match="incomplete"),
    ):
        GitLabClient(http, "group/repo").pipeline(11)


def test_test_report_pagination_is_explicitly_rejected() -> None:
    def respond(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/jobs"):
            return httpx.Response(200, json=[])
        if request.url.path.endswith("/test_report"):
            return httpx.Response(200, json={}, headers={"x-next-page": "2"})
        return httpx.Response(200, json=pipeline_data())

    with (
        httpx.Client(
            base_url="https://gitlab.com/api/v4/",
            transport=httpx.MockTransport(respond),
        ) as http,
        pytest.raises(EvidenceError, match="Paginated"),
    ):
        GitLabClient(http, "group/repo").pipeline(11)


@pytest.mark.parametrize(
    "payload",
    [
        None,
        [],
        "bad",
        {"id": True},
        pipeline_data(id=12),
        pipeline_data(project_id="1"),
        pipeline_data(sha="z" * 40),
    ],
)
def test_invalid_pipeline_payload_is_rejected(payload: object) -> None:
    with (
        httpx.Client(
            base_url="https://gitlab.com/api/v4/",
            transport=httpx.MockTransport(lambda _: httpx.Response(200, json=payload)),
        ) as http,
        pytest.raises(EvidenceError),
    ):
        GitLabClient(http, "group/repo").pipeline(11)


@pytest.mark.parametrize(
    "url",
    [
        "http://gitlab.com/group/repo/-/pipelines/11",
        "https://evil.example/group/repo/-/pipelines/11",
        "https://user:password@gitlab.com/group/repo/-/pipelines/11",
        "https://gitlab.com:444/group/repo/-/pipelines/11",
        "https://gitlab.com/group/repo/-/pipelines/12",
        "https://gitlab.com/group/repo/-/pipelines/11?token=secret",
        "https://gitlab.com/group/repo/-/pipelines/11#fragment",
        "https://gitlab.com/group/repo/-/pipelines/11\n",
    ],
)
def test_invalid_evidence_links_are_rejected(url: str) -> None:
    with (
        httpx.Client(
            base_url="https://gitlab.com/api/v4/",
            transport=httpx.MockTransport(
                lambda _: httpx.Response(200, json=pipeline_data(web_url=url)),
            ),
        ) as http,
        pytest.raises(EvidenceError, match="URL"),
    ):
        GitLabClient(http, "group/repo").pipeline(11)


def test_invalid_json_is_rejected_without_raw_body() -> None:
    with (
        httpx.Client(
            base_url="https://gitlab.com/api/v4/",
            transport=httpx.MockTransport(
                lambda _: httpx.Response(200, text="SECRET invalid JSON")
            ),
        ) as http,
        pytest.raises(EvidenceError, match="invalid JSON") as raised,
    ):
        GitLabClient(http, "group/repo").pipeline(11)
    assert "SECRET" not in str(raised.value)


def test_full_job_page_without_pagination_headers_is_not_truncated() -> None:
    def respond(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/jobs"):
            if request.url.params["page"] == "1":
                return httpx.Response(200, json=[{"name": "other"}] * 100)
            return httpx.Response(200, json=[{"name": "sample-test", "status": "success"}])
        if request.url.path.endswith("/test_report"):
            return httpx.Response(200, json={"total_count": 0, "test_suites": []})
        return httpx.Response(200, json=pipeline_data())

    with httpx.Client(
        base_url="https://gitlab.com/api/v4/",
        transport=httpx.MockTransport(respond),
    ) as http:
        assert GitLabClient(http, "group/repo").pipeline(11).test_job_statuses == ("success",)
