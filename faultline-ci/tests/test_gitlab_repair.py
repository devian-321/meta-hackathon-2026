from dataclasses import replace

import httpx
import pytest

from faultline_ci.gitlab_client import EvidenceError, GitLabClient
from faultline_ci.repair import RepairEvidence, verify_repair
from faultline_ci.verifier import Pipeline


def test_collects_pinned_trees_merge_base_and_verified_blobs(
    pricing_bytes: tuple[bytes, bytes],
    repair_evidence: RepairEvidence,
) -> None:
    requests: list[httpx.Request] = []
    fault, baseline = pricing_bytes

    def respond(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path.endswith("/merge_base"):
            assert request.url.params.get_list("refs[]") == ["a" * 40, "b" * 40]
            return httpx.Response(200, json={"id": "a" * 40})
        if request.url.path.endswith("/tree"):
            assert request.url.params["recursive"] == "true"
            entries = (
                repair_evidence.before_tree
                if request.url.params["ref"] == "a" * 40
                else repair_evidence.after_tree
            )
            return httpx.Response(
                200,
                json=[
                    {
                        "path": entry.path,
                        "id": entry.object_id,
                        "mode": entry.mode,
                        "type": entry.kind,
                    }
                    for entry in entries
                ],
            )
        before_blob = repair_evidence.before_tree[1].object_id
        return httpx.Response(200, content=fault if before_blob in request.url.path else baseline)

    before = Pipeline(1, 10, "a" * 40, "demo", "failed", "", (), ())
    after = replace(before, pipeline_id=11, sha="b" * 40, status="success")
    with httpx.Client(
        base_url="https://gitlab.com/api/v4/", transport=httpx.MockTransport(respond)
    ) as http:
        observed = GitLabClient(http, "group/repo").repair(before, after)
    assert observed == repair_evidence
    assert verify_repair(observed, before.sha, after.sha).passed
    assert len(requests) == 5


def test_cross_project_repair_is_not_collected() -> None:
    before = Pipeline(1, 10, "a" * 40, "demo", "failed", "", (), ())
    after = replace(before, project_id=2, sha="b" * 40)
    with (
        httpx.Client(base_url="https://gitlab.com/api/v4/") as http,
        pytest.raises(EvidenceError, match="same project"),
    ):
        GitLabClient(http, "group/repo").repair(before, after)
