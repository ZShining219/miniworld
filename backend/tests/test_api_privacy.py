from fastapi.testclient import TestClient


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
