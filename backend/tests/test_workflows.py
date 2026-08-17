from datetime import date

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.agent.adapters import DemoJobAdapter, JobSpyAdapter, LeverJobAdapter
from app.agent.graphs import haversine_km
from app.agent.providers import ProfileExtraction
from app.core.config import settings


def test_haversine_is_zero_for_same_point() -> None:
    assert haversine_km(31.23, 121.47, 31.23, 121.47) == 0


def test_job_graph_is_idempotent_and_distance_is_local(client: TestClient) -> None:
    first = client.post("/api/v1/job-runs", json={"query": "internship", "live": False})
    second = client.post(
        "/api/v1/job-runs", json={"query": "internship", "live": False}
    )
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["status"] == "succeeded"
    jobs = client.get("/api/v1/jobs").json()
    assert len(jobs) == 3
    assert all(job["distance_status"] == "calculated" for job in jobs)
    assert all(job["distance_km"] is not None for job in jobs)
    assert all(job["distance_reason"] is None for job in jobs)
    run_payload = first.text
    assert "31.2304" not in run_payload
    assert "121.4737" not in run_payload


def test_live_job_run_pauses_when_live_mode_is_not_enabled(client: TestClient) -> None:
    response = client.post(
        "/api/v1/job-runs", json={"query": "internship", "live": True}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "awaiting_configuration"


def test_jobspy_adapter_uses_a_source_supported_by_pinned_version(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def fake_scrape_jobs(**kwargs: object) -> pd.DataFrame:
        captured.update(kwargs)
        return pd.DataFrame(
            [
                {
                    "site": "indeed",
                    "id": "public-demo-id",
                    "title": "Software Intern",
                    "company": "Public Demo Company",
                    "location": "Shanghai",
                    "job_url": "https://example.com/public-demo-job",
                    "job_type": "internship",
                    "description": "Public test fixture",
                    "date_posted": date(2026, 8, 18),
                }
            ]
        )

    monkeypatch.setattr("jobspy.scrape_jobs", fake_scrape_jobs)
    monkeypatch.setattr(settings, "ALLOW_LIVE_JOB_SEARCH", True)
    jobs = JobSpyAdapter().search("software internship", "public landmark")

    assert captured["site_name"] == ["indeed"]
    assert captured["country_indeed"] == "China"
    assert jobs[0].source == "indeed"


def test_lever_adapter_is_read_only_and_uses_public_landmark(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> list[dict[str, object]]:
            return [
                {
                    "id": "public-lever-id",
                    "text": "AI Engineering Intern",
                    "hostedUrl": "https://jobs.lever.co/example/public-lever-id",
                    "createdAt": 1_776_000_000_000,
                    "descriptionPlain": "Public posting fixture",
                    "categories": {
                        "location": "Hong Kong",
                        "commitment": "Internship",
                    },
                }
            ]

    class FakeClient:
        def __init__(self, **kwargs: object) -> None:
            captured["client"] = kwargs

        def __enter__(self) -> FakeClient:
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def get(self, url: str, *, params: dict[str, object]) -> FakeResponse:
            captured["url"] = url
            captured["params"] = params
            return FakeResponse()

    monkeypatch.setattr("app.agent.adapters.httpx.Client", FakeClient)
    monkeypatch.setattr(settings, "ALLOW_LIVE_JOB_SEARCH", True)
    monkeypatch.setattr(settings, "LEVER_SITES", "example")
    jobs = LeverJobAdapter().search("AI internship", "Hong Kong")

    assert captured["url"] == "https://api.lever.co/v0/postings/example"
    assert captured["params"] == {
        "mode": "json",
        "limit": settings.JOB_RESULTS_LIMIT,
        "location": "Hong Kong",
    }
    assert jobs[0].source == "lever:example"
    assert jobs[0].latitude is None
    assert jobs[0].longitude is None


def test_profile_graph_creates_traceable_facts_and_resume(client: TestClient) -> None:
    artifact = client.post(
        "/api/v1/imports/text",
        json={
            "source_type": "github",
            "source_label": "公开仓库说明",
            "content": "项目：MiniWorld Agent\n技能：Python 和 LangGraph\n成果：完成本地演示",
        },
    ).json()
    run = client.post(f"/api/v1/imports/{artifact['id']}/process").json()
    assert run["status"] == "succeeded"
    facts = client.get("/api/v1/profile-facts").json()
    resumes = client.get("/api/v1/resume-drafts").json()
    assert len(facts) == 3
    assert all(item["evidence_artifact_id"] == artifact["id"] for item in facts)
    assert resumes[0]["version"] == 1
    assert len(resumes[0]["content_json"]["projects"]) == 1


def test_profile_graph_blocks_exact_location_before_provider(
    client: TestClient,
) -> None:
    client.put(
        "/api/v1/location",
        json={
            "exact_address": "仅用于隐私测试的精确地址占位符",
            "latitude": 12.345678,
            "longitude": 98.765432,
            "is_demo": True,
        },
    )
    artifact = client.post(
        "/api/v1/imports/text",
        json={
            "source_type": "gpt_conversation",
            "source_label": "隐私阻断测试",
            "content": "项目发生在仅用于隐私测试的精确地址占位符",
        },
    ).json()
    run = client.post(f"/api/v1/imports/{artifact['id']}/process").json()
    assert run["status"] == "blocked_by_policy"
    assert client.get("/api/v1/profile-facts").json() == []


def test_profile_graph_pauses_when_openai_is_not_configured(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "MODEL_PROVIDER_MODE", "openai")
    monkeypatch.setattr(settings, "OPENAI_API_KEY", None)
    artifact = client.post(
        "/api/v1/imports/text",
        json={
            "source_type": "file",
            "source_label": "provider-gate.txt",
            "content": "项目：Provider 配置门验证",
        },
    ).json()

    run = client.post(f"/api/v1/imports/{artifact['id']}/process").json()

    assert run["status"] == "awaiting_configuration"
    assert "not configured" in run["message"]
    assert client.get("/api/v1/profile-facts").json() == []
    assert client.get("/api/v1/resume-drafts").json() == []


def test_invalid_provider_schema_never_writes_profile(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    class InvalidSchemaProvider:
        name = "invalid-schema-test"

        def extract_profile(self, payload: object) -> ProfileExtraction:
            del payload
            return ProfileExtraction.model_validate(
                {
                    "facts": [
                        {
                            "fact_type": "project",
                            "value": {"text": "must not persist"},
                            "confidence": 2,
                        }
                    ],
                    "resume_summary": "must not persist",
                }
            )

    monkeypatch.setattr(
        "app.agent.graphs.get_model_provider", lambda: InvalidSchemaProvider()
    )
    artifact = client.post(
        "/api/v1/imports/text",
        json={
            "source_type": "gpt_conversation",
            "source_label": "invalid-schema.txt",
            "content": "项目：结构化校验负测试",
        },
    ).json()

    run = client.post(f"/api/v1/imports/{artifact['id']}/process").json()

    assert run["status"] == "failed"
    assert "schema" in run["message"]
    assert run["result_json"] == {"error_type": "ValidationError"}
    assert client.get("/api/v1/profile-facts").json() == []
    assert client.get("/api/v1/resume-drafts").json() == []
    assert "must not persist" not in client.get("/api/v1/agent-runs").text


def test_failed_graph_resumes_from_checkpoint_without_duplicate_jobs(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    original_search = DemoJobAdapter.search

    def fail_once(self: DemoJobAdapter, query: str, landmark_query: str):
        del self, query, landmark_query
        raise RuntimeError("fixture source unavailable")

    monkeypatch.setattr(DemoJobAdapter, "search", fail_once)
    failed = client.post(
        "/api/v1/job-runs", json={"query": "internship", "live": False}
    ).json()
    assert failed["status"] == "failed"
    assert failed["current_node"] == "stopped"
    assert failed["error_history"]
    assert client.get("/api/v1/jobs").json() == []

    monkeypatch.setattr(DemoJobAdapter, "search", original_search)
    recovered = client.post(
        f"/api/v1/agent-runs/{failed['id']}/retry"
    ).json()

    assert recovered["status"] == "succeeded"
    assert recovered["retry_count"] == 1
    assert len(recovered["error_history"]) == 1
    assert len(client.get("/api/v1/jobs").json()) == 3
    assert client.post(f"/api/v1/agent-runs/{failed['id']}/retry").status_code == 409


def test_work_graph_generates_daily_and_weekly_reports(client: TestClient) -> None:
    for work_date, content in (
        ("2026-08-17", "完成 API 骨架"),
        ("2026-08-18", "完成前端看板；下一步补齐容器测试"),
    ):
        assert (
            client.post(
                "/api/v1/work-entries",
                json={"work_date": work_date, "content": content, "tags": ["demo"]},
            ).status_code
            == 201
        )

    daily = client.post(
        "/api/v1/reports",
        json={
            "report_type": "daily",
            "period_start": "2026-08-18",
            "period_end": "2026-08-18",
        },
    ).json()
    weekly = client.post(
        "/api/v1/reports",
        json={
            "report_type": "weekly",
            "period_start": "2026-08-17",
            "period_end": "2026-08-18",
        },
    ).json()
    assert daily["status"] == "succeeded"
    assert weekly["status"] == "succeeded"
    reports = client.get("/api/v1/reports").json()
    assert {item["report_type"] for item in reports} == {"daily", "weekly"}
    assert all(item["source_entry_ids"] for item in reports)
    assert client.get("/api/v1/profile-facts").json() == []
