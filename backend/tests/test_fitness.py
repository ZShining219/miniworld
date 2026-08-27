from fastapi.testclient import TestClient


def _demo_ids(client: TestClient) -> tuple[str, str, str]:
    plans = client.get("/api/v1/fitness/plans").json()
    chest = next(item for item in plans if item["name"] == "胸")
    exercises = client.get(
        f"/api/v1/fitness/plans/{chest['id']}/exercises"
    ).json()
    return chest["id"], exercises[0]["id"], exercises[1]["id"]


def test_fitness_demo_seed_and_plan_exercise_crud(client: TestClient) -> None:
    plans = client.get("/api/v1/fitness/plans").json()
    assert [item["name"] for item in plans] == ["胸", "背", "肩", "臀腿"]
    chest_id, _, _ = _demo_ids(client)
    chest_exercises = client.get(
        f"/api/v1/fitness/plans/{chest_id}/exercises"
    ).json()
    assert [item["name"] for item in chest_exercises] == [
        "杠铃卧推",
        "上斜哑铃卧推",
    ]
    assert [item["weightStep"] for item in chest_exercises] == [2.5, 2.5]

    plan = client.post("/api/v1/fitness/plans", json={"name": "核心"})
    assert plan.status_code == 201
    exercise = client.post(
        "/api/v1/fitness/exercises",
        json={
            "plan_id": plan.json()["id"],
            "name": "平板支撑",
            "default_weight": 0,
            "default_reps": 1,
        },
    )
    assert exercise.status_code == 201
    updated = client.patch(
        f"/api/v1/fitness/exercises/{exercise.json()['id']}",
        json={"name": "负重平板支撑", "default_weight": 10},
    )
    assert updated.json()["name"] == "负重平板支撑"
    assert updated.json()["defaultWeight"] == 10
    assert updated.json()["weightStep"] == 2.5

    updated_step = client.patch(
        f"/api/v1/fitness/exercises/{exercise.json()['id']}",
        json={"weightStep": 1},
    )
    assert updated_step.status_code == 200
    assert updated_step.json()["weightStep"] == 1
    invalid_step = client.patch(
        f"/api/v1/fitness/exercises/{exercise.json()['id']}",
        json={"weightStep": 3},
    )
    assert invalid_step.status_code == 422

    reordered_plans = client.put(
        "/api/v1/fitness/plans/order",
        json={"ids": [plan.json()["id"], *[item["id"] for item in plans]]},
    )
    assert reordered_plans.status_code == 200
    assert reordered_plans.json()[0]["name"] == "核心"

    second = client.post(
        "/api/v1/fitness/exercises",
        json={
            "planId": plan.json()["id"],
            "name": "卷腹",
            "defaultWeight": 0,
            "defaultReps": 15,
        },
    ).json()
    reordered_exercises = client.put(
        f"/api/v1/fitness/plans/{plan.json()['id']}/exercises/order",
        json={"ids": [second["id"], exercise.json()["id"]]},
    )
    assert reordered_exercises.status_code == 200
    assert [item["name"] for item in reordered_exercises.json()] == [
        "卷腹",
        "负重平板支撑",
    ]


def test_active_session_is_resumed_and_other_plan_is_blocked(
    client: TestClient,
) -> None:
    chest_id, _, _ = _demo_ids(client)
    started = client.post("/api/v1/fitness/sessions", json={"plan_id": chest_id})
    resumed = client.post("/api/v1/fitness/sessions", json={"plan_id": chest_id})
    assert started.status_code == 201
    assert resumed.status_code == 201
    assert resumed.json()["id"] == started.json()["id"]
    assert resumed.json()["resumed"] is True
    assert client.get("/api/v1/fitness/sessions/active").json()["id"] == started.json()["id"]

    back = next(
        item for item in client.get("/api/v1/fitness/plans").json() if item["name"] == "背"
    )
    conflict = client.post("/api/v1/fitness/sessions", json={"plan_id": back["id"]})
    assert conflict.status_code == 409


def test_sets_are_immediate_ordered_and_idempotent(client: TestClient) -> None:
    chest_id, bench_id, _ = _demo_ids(client)
    workout = client.post(
        "/api/v1/fitness/sessions", json={"plan_id": chest_id}
    ).json()
    payloads = [
        {"exercise_id": bench_id, "weight": 80, "reps": 8, "client_request_id": "set-request-0001"},
        {"exercise_id": bench_id, "weight": 80, "reps": 8, "client_request_id": "set-request-0002"},
        {"exercise_id": bench_id, "weight": 75, "reps": 10, "client_request_id": "set-request-0003"},
    ]
    created = [
        client.post(f"/api/v1/fitness/sessions/{workout['id']}/sets", json=item)
        for item in payloads
    ]
    assert [response.status_code for response in created] == [201, 201, 201]
    assert [response.json()["setOrder"] for response in created] == [1, 2, 3]

    retried = client.post(
        f"/api/v1/fitness/sessions/{workout['id']}/sets", json=payloads[0]
    )
    assert retried.status_code == 201
    assert retried.json()["id"] == created[0].json()["id"]
    log = client.get(
        f"/api/v1/fitness/sessions/{workout['id']}/exercises/{bench_id}"
    ).json()
    assert len(log["currentSets"]) == 3
    assert log["exercise"]["weightStep"] == 2.5


def test_completed_workout_populates_history_calendar_progress_and_last_sets(
    client: TestClient,
) -> None:
    chest_id, bench_id, incline_id = _demo_ids(client)
    workout = client.post(
        "/api/v1/fitness/sessions", json={"plan_id": chest_id}
    ).json()
    sets = [
        (bench_id, 80, 8),
        (bench_id, 80, 8),
        (bench_id, 75, 10),
        (incline_id, 25, 10),
        (incline_id, 25, 10),
    ]
    for index, (exercise_id, weight, reps) in enumerate(sets):
        response = client.post(
            f"/api/v1/fitness/sessions/{workout['id']}/sets",
            json={
                "exercise_id": exercise_id,
                "weight": weight,
                "reps": reps,
                "client_request_id": f"completed-demo-{index}",
            },
        )
        assert response.status_code == 201
    finished = client.post(f"/api/v1/fitness/sessions/{workout['id']}/finish")
    assert finished.json()["status"] == "COMPLETED"
    assert client.get("/api/v1/fitness/sessions/active").json() is None

    history = client.get("/api/v1/fitness/history").json()
    assert history[0]["setCount"] == 5
    assert history[0]["exerciseCount"] == 2
    workout_date = history[0]["session"]["workoutDate"]
    calendar = client.get(
        "/api/v1/fitness/stats/calendar",
        params={"start": workout_date, "end": workout_date},
    ).json()
    assert calendar["dates"] == [workout_date]
    progress = client.get(
        f"/api/v1/fitness/stats/exercises/{bench_id}/progress"
    ).json()
    assert progress["points"] == [
        {
            "workoutDate": workout_date,
            "sessionId": workout["id"],
            "maxWeight": 80,
        }
    ]

    next_workout = client.post(
        "/api/v1/fitness/sessions", json={"plan_id": chest_id}
    ).json()
    log = client.get(
        f"/api/v1/fitness/sessions/{next_workout['id']}/exercises/{bench_id}"
    ).json()
    assert [(item["weight"], item["reps"]) for item in log["previousSets"]] == [
        (80, 8),
        (80, 8),
        (75, 10),
    ]
    assert log["suggestedWeight"] == 75
    assert log["suggestedReps"] == 10


def test_archiving_exercise_preserves_historical_sets(client: TestClient) -> None:
    chest_id, bench_id, _ = _demo_ids(client)
    workout = client.post(
        "/api/v1/fitness/sessions", json={"plan_id": chest_id}
    ).json()
    client.post(
        f"/api/v1/fitness/sessions/{workout['id']}/sets",
        json={
            "exercise_id": bench_id,
            "weight": 80,
            "reps": 8,
            "client_request_id": "archive-history-1",
        },
    )
    client.post(f"/api/v1/fitness/sessions/{workout['id']}/finish")
    assert client.delete(f"/api/v1/fitness/exercises/{bench_id}").status_code == 204
    exercises = client.get(f"/api/v1/fitness/plans/{chest_id}/exercises").json()
    assert bench_id not in [item["id"] for item in exercises]
    history = client.get("/api/v1/fitness/history").json()
    assert history[0]["exercises"][0]["exerciseName"] == "杠铃卧推"
    assert history[0]["exercises"][0]["sets"][0]["weight"] == 80


def test_create_exercise_after_archiving_uses_a_new_order(
    client: TestClient,
) -> None:
    plan = client.post("/api/v1/fitness/plans", json={"name": "灵活训练"})
    assert plan.status_code == 201
    plan_id = plan.json()["id"]

    archived = client.post(
        "/api/v1/fitness/exercises",
        json={
            "plan_id": plan_id,
            "name": "弹力带热身",
            "default_weight": 0,
            "default_reps": 15,
        },
    )
    assert archived.status_code == 201
    assert archived.json()["sortOrder"] == 0
    assert (
        client.delete(f"/api/v1/fitness/exercises/{archived.json()['id']}").status_code
        == 204
    )

    replacement = client.post(
        "/api/v1/fitness/exercises",
        json={
            "plan_id": plan_id,
            "name": "哑铃热身",
            "default_weight": 5,
            "default_reps": 12,
        },
    )

    assert replacement.status_code == 201
    assert replacement.json()["sortOrder"] == 1
    active = client.get(f"/api/v1/fitness/plans/{plan_id}/exercises").json()
    assert [item["name"] for item in active] == ["哑铃热身"]

    reordered = client.put(
        f"/api/v1/fitness/plans/{plan_id}/exercises/order",
        json={"ids": [replacement.json()["id"]]},
    )
    assert reordered.status_code == 200
    assert [item["name"] for item in reordered.json()] == ["哑铃热身"]
    assert reordered.json()[0]["sortOrder"] == 1
