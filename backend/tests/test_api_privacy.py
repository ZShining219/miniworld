from pathlib import Path

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.core.db import engine
from app.models import JobPosting


def test_location_api_never_echoes_exact_values(client: TestClient) -> None:
    exact = "仅用于 API 隐私测试的地址占位符"
    response = client.put(
        "/api/v1/location",
        json={
            "exact_address": exact,
            "latitude": 11.123456,
            "longitude": 99.654321,
            "is_demo": True,
        },
    )
    assert response.status_code == 200
    assert exact not in response.text
    assert "11.123456" not in response.text
    assert "99.654321" not in response.text
    status_response = client.get("/api/v1/location")
    assert status_response.json()["configured"] is True
    assert exact not in status_response.text


def test_location_validation_error_does_not_echo_input(client: TestClient) -> None:
    exact = "不应出现在错误响应中的地址占位符"
    response = client.put(
        "/api/v1/location",
        json={
            "exact_address": exact,
            "latitude": 999,
            "longitude": 999,
            "is_demo": True,
        },
    )
    assert response.status_code == 422
    assert exact not in response.text
    assert '"input"' not in response.text


def test_overview_and_agent_run_api_do_not_expose_artifact_content(
    client: TestClient,
) -> None:
    marker = "PRIVATE-CONTENT-MARKER-FOR-TEST"
    artifact = client.post(
        "/api/v1/imports/text",
        json={
            "source_type": "file",
            "source_label": "测试文本",
            "content": f"项目：{marker}",
        },
    ).json()
    client.post(f"/api/v1/imports/{artifact['id']}/process")
    assert marker not in client.get("/api/v1/overview").text
    assert marker not in client.get("/api/v1/agent-runs").text
    assert marker not in client.get("/api/v1/imports").text


def test_scheduler_trigger_is_a_local_demo_read(client: TestClient) -> None:
    response = client.post("/api/v1/schedule/run-once")
    assert response.status_code == 200
    assert response.json() == {"triggered": True}
    runs = client.get("/api/v1/agent-runs").json()
    assert runs[0]["trigger"] == "scheduler"
    assert runs[0]["execution_mode"] == "demo"


def test_radar_map_supports_local_byte_ranges(
    client: TestClient, tmp_path: Path, monkeypatch
) -> None:
    fixture = bytes(range(256)) * 80
    map_path = tmp_path / "demo.pmtiles"
    map_path.write_bytes(fixture)
    monkeypatch.setattr(settings, "RADAR_MAP_DIR", tmp_path)

    response = client.get(
        "/api/v1/radar/maps/demo.pmtiles",
        headers={"Range": "bytes=100-199"},
    )

    assert response.status_code == 206
    assert response.content == fixture[100:200]
    assert response.headers["accept-ranges"] == "bytes"
    assert response.headers["content-range"] == f"bytes 100-199/{len(fixture)}"
    assert response.headers["cache-control"] == "private, max-age=86400"


def test_radar_map_rejects_non_pmtiles_files(
    client: TestClient, tmp_path: Path, monkeypatch
) -> None:
    (tmp_path / "secret.txt").write_text("not a map")
    monkeypatch.setattr(settings, "RADAR_MAP_DIR", tmp_path)

    response = client.get("/api/v1/radar/maps/secret.txt")

    assert response.status_code == 404
    assert "not a map" not in response.text


def test_radar_demo_scene_is_local_no_store_and_contains_no_address(
    client: TestClient, tmp_path: Path, monkeypatch
) -> None:
    (tmp_path / "demo-firenze.pmtiles").write_bytes(b"demo")
    monkeypatch.setattr(settings, "RADAR_MAP_DIR", tmp_path)

    response = client.get("/api/v1/radar/scene")
    payload = response.json()

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert payload["mode"] == "fictional_demo"
    assert payload["center"] == [11.2543435, 43.7672134]
    assert len(payload["jobs"]["features"]) == 4
    assert payload["map_available"] is True
    assert "虚构演示住址" not in response.text
    assert "exact_address" not in response.text


def test_radar_local_scene_filters_unresolved_jobs_and_minimizes_properties(
    client: TestClient, tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(settings, "EXECUTION_MODE", "live")
    monkeypatch.setattr(settings, "RADAR_MAP_DIR", tmp_path)
    with Session(engine) as session:
        session.add_all(
            [
                JobPosting(
                    source="fixture",
                    external_id="mapped",
                    title="Mapped role",
                    company="Example",
                    location_text="Public office",
                    latitude=43.77,
                    longitude=11.26,
                    distance_km=0.8,
                    distance_status="calculated",
                    url="https://example.com/mapped",
                    fingerprint="a" * 64,
                ),
                JobPosting(
                    source="fixture",
                    external_id="unresolved",
                    title="Unresolved role",
                    company="Example",
                    location_text="Unknown",
                    distance_status="location_unresolved",
                    distance_reason="No reliable public coordinates",
                    url="https://example.com/unresolved",
                    fingerprint="b" * 64,
                ),
            ]
        )
        session.commit()

    response = client.get("/api/v1/radar/scene")
    payload = response.json()
    features = payload["jobs"]["features"]

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert payload["mode"] == "local"
    assert payload["center"] == [121.4737, 31.2304]
    assert payload["total_count"] == 2
    assert payload["unresolved_count"] == 1
    assert len(features) == 1
    assert features[0]["properties"]["title"] == "Mapped role"
    assert "location_text" not in features[0]["properties"]
    assert "Unresolved role" not in response.text
    assert "虚构演示住址" not in response.text


def test_radar_native_origin_has_only_local_cors_read_access(
    client: TestClient,
) -> None:
    response = client.options(
        "/api/v1/radar/scene",
        headers={
            "Origin": "tauri://localhost",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Range",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "tauri://localhost"
    assert "range" in response.headers["access-control-allow-headers"].lower()
    assert "POST" in response.headers["access-control-allow-methods"]
