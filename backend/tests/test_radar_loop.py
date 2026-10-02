"""Coverage for the radar active-fetch loop added for the scheduled agent."""

from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, col, select

import app.agent.adapters as adapters_module
from app.agent.adapters import (
    GreenhouseJobAdapter,
    RawJob,
    default_job_source_names,
    resolve_job_adapters,
)
from app.agent.gazetteer import lookup_city
from app.agent.geocode import resolve_job_location
from app.core.config import settings
from app.core.db import engine
from app.models import JobPosting, PrivateLocation, ScheduleConfig
from app.worker import run_schedule_tick


class _FakeResponse:
    def __init__(self, payload: Any, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self) -> Any:
        return self._payload


class _FakeClient:
    def __init__(self, payload: Any) -> None:
        self._payload = payload

    def __enter__(self) -> _FakeClient:
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def get(self, url: str, params: dict[str, object] | None = None) -> _FakeResponse:
        return _FakeResponse(self._payload)


def _enable_live(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "ALLOW_LIVE_JOB_SEARCH", True)
    monkeypatch.setattr(settings, "EXECUTION_MODE", "live")


def test_gazetteer_resolves_city_and_keeps_remote_unresolved() -> None:
    assert lookup_city("Hong Kong") is not None
    assert lookup_city("上海 · 张江") is not None
    assert lookup_city("Remote - Global") is None
    assert lookup_city("秘密地点") is None


def test_geocode_prefers_configured_landmark() -> None:
    class Landmark:
        name = "香港"
        query_text = "Hong Kong"
        latitude = 22.3193
        longitude = 114.1694

    resolved = resolve_job_location("Hong Kong", [Landmark()])
    assert resolved is not None
    assert resolved.geocode_source == "landmark:香港"
    fallback = resolve_job_location("Singapore", [Landmark()])
    assert fallback is not None
    assert fallback.geocode_source == "gazetteer:新加坡"


def test_greenhouse_adapter_normalizes_board_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_live(monkeypatch)
    monkeypatch.setattr(settings, "GREENHOUSE_BOARDS", "exampleco")
    payload = {
        "jobs": [
            {
                "id": 42,
                "title": "Backend Intern",
                "absolute_url": "https://boards.greenhouse.io/exampleco/jobs/42",
                "updated_at": "2026-09-30T10:00:00+00:00",
                "location": {"name": "Singapore"},
                "content": "<p>Build <b>data</b> pipelines.</p>",
                "pay_input_ranges": [
                    {
                        "min_cents": 9_000_000,
                        "max_cents": 12_000_000,
                        "currency_type": {"code": "SGD"},
                    }
                ],
            }
        ]
    }
    monkeypatch.setattr(
        adapters_module.httpx, "Client", lambda **kwargs: _FakeClient(payload)
    )
    jobs = GreenhouseJobAdapter().search("ignored", "Singapore")
    assert len(jobs) == 1
    job = jobs[0]
    assert job.source == "greenhouse:exampleco"
    assert job.external_id == "42"
    assert job.location_text == "Singapore"
    assert job.salary_text == "SGD 90000–120000/year"
    assert job.summary == "Build data pipelines."


def test_resolve_job_adapters_enforces_mode_boundary() -> None:
    adapters = resolve_job_adapters(["demo", "lever"], live=False)
    assert [adapter.name for adapter in adapters] == ["demo"]
    adapters = resolve_job_adapters(["demo", "lever"], live=True)
    assert [adapter.name for adapter in adapters] == ["lever"]
    with pytest.raises(RuntimeError, match="demo"):
        resolve_job_adapters(["lever"], live=False)
    with pytest.raises(RuntimeError, match="unknown job source"):
        resolve_job_adapters(["nonsense"], live=True)


def test_default_source_names_respect_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "RADAR_FETCH_SOURCES", "demo,lever")
    assert default_job_source_names(live=False) == ["demo"]
    assert default_job_source_names(live=True) == ["lever"]


class _FailingAdapter:
    name = "flaky"

    def search(self, query: str, landmark_query: str) -> list[RawJob]:
        raise RuntimeError("simulated outage")


def _configure_schedule(
    *, sources: list[str], interval: int = 15, live: bool = False
) -> None:
    with Session(engine) as session:
        schedule = session.get(ScheduleConfig, 1)
        assert schedule is not None
        schedule.sources = sources
        schedule.interval_minutes = interval
        schedule.live_enabled = live
        schedule.job_discovery_enabled = True
        schedule.last_triggered_at = None
        session.add(schedule)
        session.commit()


def test_scheduled_tick_runs_demo_sources_and_records_status() -> None:
    _configure_schedule(sources=["demo"])
    assert run_schedule_tick(force=True) is True
    with Session(engine) as session:
        schedule = session.get(ScheduleConfig, 1)
        assert schedule is not None
        assert schedule.last_run_status == "succeeded"
        assert schedule.last_run_new == 3
        assert schedule.last_run_failed == 0
        assert schedule.last_run_at is not None
        jobs = session.exec(select(JobPosting)).all()
        assert len(jobs) == 3
        assert any(job.salary_text for job in jobs)
        assert all(job.first_seen_at is not None for job in jobs)


def test_scheduled_tick_survives_a_partial_source_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(
        adapters_module.JOB_ADAPTER_FACTORIES, "flaky", lambda: _FailingAdapter()
    )
    _configure_schedule(sources=["demo", "flaky"])
    assert run_schedule_tick(force=True) is True
    with Session(engine) as session:
        schedule = session.get(ScheduleConfig, 1)
        assert schedule is not None
        assert schedule.last_run_status == "succeeded"
        assert schedule.last_run_new == 3
        assert schedule.last_run_failed == 1
        jobs = session.exec(select(JobPosting)).all()
        assert len(jobs) == 3
        from app.models import AgentRun

        last_run = session.exec(
            select(AgentRun).order_by(col(AgentRun.started_at).desc())
        ).first()
        assert last_run is not None
        assert last_run.result_json is not None
        assert last_run.result_json["failed_sources"][0]["source"] == "flaky"


def test_second_run_marks_unchanged_not_new() -> None:
    _configure_schedule(sources=["demo"])
    run_schedule_tick(force=True)
    run_schedule_tick(force=True)
    with Session(engine) as session:
        schedule = session.get(ScheduleConfig, 1)
        assert schedule is not None
        assert schedule.last_run_new == 0
        assert schedule.last_run_status == "succeeded"


def test_tick_respects_interval_after_first_run() -> None:
    """SQLite reloads ``last_triggered_at`` as naive — the due check must
    not crash and must suppress a second run inside the interval."""
    _configure_schedule(sources=["demo"], interval=720)
    assert run_schedule_tick() is True
    assert run_schedule_tick() is False
    with Session(engine) as session:
        schedule = session.get(ScheduleConfig, 1)
        assert schedule is not None
        schedule.interval_minutes = -1
        session.add(schedule)
        session.commit()
    assert run_schedule_tick() is True


def test_radar_scene_projects_persisted_jobs(client: TestClient) -> None:
    response = client.post(
        "/api/v1/job-runs", json={"query": "demo", "live": False}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "succeeded"
    scene = client.get("/api/v1/radar/scene").json()
    assert scene["mode"] == "local"
    assert scene["total_count"] == 3
    assert len(scene["jobs"]["features"]) == 3
    assert scene["unresolved_count"] == 0
    assert scene["generated_at"] is not None
    assert scene["last_run"]["status"] == "succeeded"
    assert scene["last_run"]["new_count"] == 3
    assert all(feature["properties"]["is_new"] for feature in scene["jobs"]["features"])
    assert any(
        feature["properties"]["salary_text"] == "CNY 300–400/天"
        for feature in scene["jobs"]["features"]
    )
    assert "虚构演示住址" not in repr(scene)


def test_interview_handoff_export_writes_pending_document(
    client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "INTERVIEW_HANDOFF_DIR", tmp_path)
    client.post("/api/v1/job-runs", json={"query": "demo", "live": False})
    jobs = client.get("/api/v1/jobs").json()
    job_id = jobs[0]["id"]
    response = client.post(
        f"/api/v1/jobs/{job_id}/interview-handoff",
        json={"push": False},
    )
    assert response.status_code == 200
    result = response.json()
    assert result["pushed"] is False
    assert result["push_channel"] == "none"
    path = Path(result["file"])
    assert path.is_file()
    import json

    package = json.loads(path.read_text(encoding="utf-8"))
    record = package["knowledge_import"]["records"][0]
    assert record["source"] == "miniworld_radar"
    assert record["material_type"] == "jd"
    assert record["role_id"] in {
        "python_backend",
        "llm_app",
        "frontend",
        "java_backend",
        "go_backend",
        "data_engineering",
        "qa_automation",
        "platform_sre",
    }
    assert record["content"].startswith("职位：")
    assert package["interview_plan_request"]["resume"] == {}


def test_interview_handoff_rejects_unknown_role(client: TestClient) -> None:
    client.post("/api/v1/job-runs", json={"query": "demo", "live": False})
    jobs = client.get("/api/v1/jobs").json()
    response = client.post(
        f"/api/v1/jobs/{jobs[0]['id']}/interview-handoff",
        json={"push": False, "role_id": "astronaut"},
    )
    assert response.status_code == 422


def test_schedule_update_validates_sources(client: TestClient) -> None:
    response = client.put(
        "/api/v1/schedule",
        json={
            "job_discovery_enabled": True,
            "interval_minutes": 30,
            "live_enabled": False,
            "sources": ["demo", "not-a-source"],
            "query_text": "intern",
        },
    )
    assert response.status_code == 422
    response = client.put(
        "/api/v1/schedule",
        json={
            "job_discovery_enabled": True,
            "interval_minutes": 30,
            "live_enabled": True,
            "sources": ["lever"],
            "query_text": "intern",
        },
    )
    assert response.status_code == 409


def test_scene_never_echoes_home_address(client: TestClient) -> None:
    client.post("/api/v1/job-runs", json={"query": "demo", "live": False})
    scene = client.get("/api/v1/radar/scene")
    payload = scene.text
    with Session(engine) as session:
        home = session.get(PrivateLocation, 1)
    assert home is not None
    assert home.exact_address not in payload
    scene_json = scene.json()
    assert scene_json["center"] == [home.longitude, home.latitude]
    for feature in scene_json["jobs"]["features"]:
        longitude, latitude = feature["geometry"]["coordinates"]
        assert (longitude, latitude) != (home.longitude, home.latitude)
    feature_sources = {
        feature["properties"]["geocode_source"]
        for feature in scene_json["jobs"]["features"]
    }
    assert feature_sources == {"source"}


def test_schedule_run_once_endpoint_reports_trigger(client: TestClient) -> None:
    response = client.post("/api/v1/schedule/run-once")
    assert response.status_code == 200
    assert response.json() == {"triggered": True}
