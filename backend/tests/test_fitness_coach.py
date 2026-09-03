import json
import uuid
from types import SimpleNamespace
from typing import cast

import pytest
from fastapi.testclient import TestClient
from openai import OpenAI
from pydantic import ValidationError
from sqlmodel import Session, col, func, select

from app.core.config import settings
from app.core.db import engine
from app.fitness.coach import provider as coach_provider
from app.fitness.coach import service as coach_service
from app.fitness.coach.schemas import (
    RecommendationAction,
    RecommendationDraft,
    RecommendationEvidence,
    ToolPlan,
)
from app.fitness.models import FitnessCoachRecommendation, FitnessSession, FitnessSet
from app.models import AgentRun, ModelCallAudit


class ControlledCoachProvider:
    name = "controlled-test-provider"
    model = "controlled-fitness-model"

    def select_tools(self, trigger: dict[str, object]) -> ToolPlan:
        exercise_ids = trigger["exercise_ids"]
        assert isinstance(exercise_ids, list)
        return ToolPlan(
            tools=["completed_session", "exercise_history"],
            focus_exercise_id=uuid.UUID(str(exercise_ids[0])),
            rationale="Use the completed workout and prior performance.",
        )

    def recommend(
        self, trigger: dict[str, object], observations: dict[str, object]
    ) -> RecommendationDraft:
        exercise_ids = trigger["exercise_ids"]
        assert isinstance(exercise_ids, list)
        assert set(observations) == {"completed_session", "exercise_history"}
        return RecommendationDraft(
            recommendation_type="increase_weight",
            target_exercise_id=uuid.UUID(str(exercise_ids[0])),
            title="杠铃卧推下次尝试小幅加重",
            action=RecommendationAction(weight=82.5, reps=8, sets=3),
            reason="本次三个工作组已完成，结合历史记录可在下次训练复核小幅加重。",
            evidence=[
                RecommendationEvidence(
                    source="completed_session",
                    summary="Three working sets were completed.",
                    session_id=uuid.UUID(str(trigger["session_id"])),
                ),
                RecommendationEvidence(
                    source="exercise_history",
                    summary="Available prior sessions were considered.",
                ),
            ],
            confidence=0.78,
            review_after="next_session",
        )


class UnsafeCoachProvider(ControlledCoachProvider):
    def recommend(
        self, trigger: dict[str, object], observations: dict[str, object]
    ) -> RecommendationDraft:
        return RecommendationDraft(
            recommendation_type="increase_weight",
            target_exercise_id=uuid.uuid4(),
            title="Invalid target",
            action=RecommendationAction(weight=100),
            reason="This target is not in the completed session.",
            evidence=[
                RecommendationEvidence(
                    source="exercise_history",
                    summary="Unsafe target test fixture.",
                )
            ],
            confidence=0.5,
            review_after="next_session",
        )


def _complete_chest_workout(client: TestClient) -> tuple[str, int, int]:
    plans = client.get("/api/v1/fitness/plans").json()
    chest = next(item for item in plans if item["name"] == "胸")
    exercises = client.get(
        f"/api/v1/fitness/plans/{chest['id']}/exercises"
    ).json()
    workout = client.post(
        "/api/v1/fitness/sessions", json={"planId": chest["id"]}
    ).json()
    for index, (weight, reps) in enumerate(((80, 8), (80, 8), (80, 9))):
        response = client.post(
            f"/api/v1/fitness/sessions/{workout['id']}/sets",
            json={
                "exerciseId": exercises[0]["id"],
                "weight": weight,
                "reps": reps,
                "clientRequestId": f"coach-test-{index}",
            },
        )
        assert response.status_code == 201
    with Session(engine) as db:
        session_count = int(
            db.exec(select(func.count()).select_from(FitnessSession)).one()
        )
        set_count = int(db.exec(select(func.count()).select_from(FitnessSet)).one())
    finished = client.post(f"/api/v1/fitness/sessions/{workout['id']}/finish")
    assert finished.status_code == 200
    return workout["id"], session_count, set_count


def test_completed_workout_runs_agent_and_persists_read_only_advice(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        coach_service, "get_coach_provider", lambda: ControlledCoachProvider()
    )
    workout_id, session_count, set_count = _complete_chest_workout(client)

    response = client.get("/api/v1/fitness/coach/recommendations")
    assert response.status_code == 200
    recommendations = response.json()
    assert len(recommendations) == 1
    advice = recommendations[0]
    assert advice["sessionId"] == workout_id
    assert advice["recommendationType"] == "increase_weight"
    assert advice["action"] == {"weight": 82.5, "reps": 8, "sets": 3}
    assert advice["provider"] == "controlled-test-provider"

    with Session(engine) as db:
        run = db.get(AgentRun, uuid.UUID(advice["runId"]))
        assert run is not None
        assert run.graph_name == "fitness_coach"
        assert run.trigger == "session_completed"
        assert run.status == "succeeded"
        assert run.result_json is not None
        assert run.result_json["tool_calls"] == [
            "completed_session",
            "exercise_history",
        ]
        audit = db.exec(
            select(ModelCallAudit).where(ModelCallAudit.run_id == run.id)
        ).one()
        assert audit.task == "fitness_coach_recommendation"
        assert audit.payload_sha256 == run.result_json["payload_sha256"]
        assert int(db.exec(select(func.count()).select_from(FitnessSession)).one()) == session_count
        assert int(db.exec(select(func.count()).select_from(FitnessSet)).one()) == set_count


def test_missing_deepseek_key_records_awaiting_configuration(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "FITNESS_AGENT_PROVIDER", "deepseek")
    monkeypatch.setattr(settings, "FITNESS_AGENT_API_KEY", None)
    workout_id, _, _ = _complete_chest_workout(client)

    with Session(engine) as db:
        run = db.exec(
            select(AgentRun)
            .where(
                AgentRun.graph_name == "fitness_coach",
                AgentRun.trigger == "session_completed",
            )
            .order_by(col(AgentRun.started_at).desc())
        ).first()
        assert run is not None
        assert run.status == "awaiting_configuration"
        assert run.message == "FITNESS_AGENT_API_KEY is not configured"
        assert db.exec(
            select(FitnessCoachRecommendation).where(
                FitnessCoachRecommendation.session_id == uuid.UUID(workout_id)
            )
        ).first() is None


def test_agent_rejects_recommendation_for_exercise_outside_session(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        coach_service, "get_coach_provider", lambda: UnsafeCoachProvider()
    )
    workout_id, _, _ = _complete_chest_workout(client)

    with Session(engine) as db:
        run = db.exec(
            select(AgentRun)
            .where(AgentRun.graph_name == "fitness_coach")
            .order_by(col(AgentRun.started_at).desc())
        ).first()
        assert run is not None
        assert run.status == "failed"
        assert run.message == (
            "Fitness Coach Agent stopped safely; no recommendation was saved."
        )
        assert db.exec(
            select(FitnessCoachRecommendation).where(
                FitnessCoachRecommendation.session_id == uuid.UUID(workout_id)
            )
        ).first() is None


def test_manual_analysis_rejects_active_session_without_creating_run(
    client: TestClient,
) -> None:
    plan = client.get("/api/v1/fitness/plans").json()[0]
    workout = client.post(
        "/api/v1/fitness/sessions", json={"planId": plan["id"]}
    ).json()

    response = client.post(
        "/api/v1/fitness/coach/analyze",
        json={"sessionId": workout["id"]},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Fitness Coach only analyzes completed sessions"
    with Session(engine) as db:
        assert db.exec(
            select(AgentRun).where(AgentRun.graph_name == "fitness_coach")
        ).first() is None


@pytest.mark.parametrize(
    ("recommendation_type", "action"),
    [
        ("increase_weight", RecommendationAction(reps=8)),
        ("increase_reps", RecommendationAction(weight=80)),
    ],
)
def test_actionable_recommendations_require_matching_numeric_target(
    recommendation_type: str, action: RecommendationAction
) -> None:
    with pytest.raises(ValidationError):
        RecommendationDraft.model_validate(
            {
                "recommendationType": recommendation_type,
                "title": "Invalid action",
                "action": action.model_dump(),
                "reason": "The required numeric target is absent.",
                "evidence": [
                    {
                        "source": "completed_session",
                        "summary": "Controlled validation fixture.",
                    }
                ],
                "confidence": 0.5,
            }
        )


def test_deepseek_provider_contract_without_network(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    exercise_id = uuid.uuid4()
    responses = iter(
        [
            {
                "tools": ["completed_session", "exercise_history"],
                "focusExerciseId": str(exercise_id),
                "rationale": "Inspect the completed session and exercise history.",
            },
            {
                "recommendationType": "increase_weight",
                "targetExerciseId": str(exercise_id),
                "title": "Increase the working weight",
                "action": {"weight": 82.5, "reps": 8, "sets": 3},
                "reason": "The controlled observations support a small increase.",
                "evidence": [
                    {
                        "source": "completed_session",
                        "summary": "Three work sets were completed.",
                    }
                ],
                "confidence": 0.75,
                "reviewAfter": "next_session",
            },
        ]
    )
    calls: list[dict[str, object]] = []
    constructor: dict[str, object] = {}

    def create(**kwargs: object) -> object:
        calls.append(kwargs)
        payload = json.dumps(next(responses))
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=payload))]
        )

    fake_client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=create))
    )

    def fake_openai(**kwargs: object) -> OpenAI:
        constructor.update(kwargs)
        return cast(OpenAI, fake_client)

    monkeypatch.setattr(settings, "FITNESS_AGENT_API_KEY", "controlled-placeholder")
    monkeypatch.setattr(settings, "FITNESS_AGENT_BASE_URL", "https://api.deepseek.com")
    monkeypatch.setattr(settings, "FITNESS_AGENT_TIMEOUT_SECONDS", 30)
    monkeypatch.setattr(coach_provider, "OpenAI", fake_openai)

    provider = coach_provider.DeepSeekCoachProvider()
    trigger: dict[str, object] = {
        "session_id": str(uuid.uuid4()),
        "exercise_ids": [str(exercise_id)],
    }
    plan = provider.select_tools(trigger)
    recommendation = provider.recommend(
        trigger,
        {"completed_session": {"sets": 3}, "exercise_history": {"sessions": 2}},
    )

    assert constructor == {
        "api_key": "controlled-placeholder",
        "base_url": "https://api.deepseek.com/v1",
        "timeout": 30,
    }
    assert plan.focus_exercise_id == exercise_id
    assert recommendation.target_exercise_id == exercise_id
    assert len(calls) == 2
    assert all(call["model"] == "deepseek-chat" for call in calls)
    assert all(call["response_format"] == {"type": "json_object"} for call in calls)
