import hashlib
import json
import uuid
from datetime import UTC, datetime

from pydantic import ValidationError
from sqlmodel import Session, col, select

from app.agent.checkpoints import checkpoint_saver
from app.core.db import engine
from app.fitness.coach.graph import build_fitness_coach_graph
from app.fitness.coach.provider import CoachProvider, get_coach_provider
from app.fitness.coach.schemas import RecommendationDraft, RecommendationPublic
from app.fitness.models import FitnessCoachRecommendation, FitnessSession
from app.models import AgentRun, ModelCallAudit


def _finish_run(
    run_id: uuid.UUID,
    *,
    status: str,
    message: str,
    result_json: dict[str, object] | None = None,
    error: Exception | None = None,
) -> AgentRun:
    with Session(engine) as db:
        run = db.get(AgentRun, run_id)
        if run is None:
            raise RuntimeError("Fitness Coach run disappeared")
        run.status = status
        run.current_node = "complete" if status == "succeeded" else "stopped"
        run.message = message
        run.result_json = result_json
        run.finished_at = datetime.now(UTC)
        if error is not None:
            run.error_history = [
                *run.error_history,
                {
                    "at": run.finished_at.isoformat(),
                    "status": status,
                    "message": message,
                    "error_type": type(error).__name__,
                },
            ]
        db.add(run)
        db.commit()
        db.refresh(run)
        return run


def _error_status(error: Exception) -> str:
    message = str(error).lower()
    if "not configured" in message or "disabled" in message:
        return "awaiting_configuration"
    return "failed"


def run_fitness_coach(
    session_id: uuid.UUID,
    *,
    trigger: str = "session_completed",
    provider: CoachProvider | None = None,
) -> AgentRun:
    with Session(engine) as db:
        workout = db.get(FitnessSession, session_id)
        if workout is None:
            raise LookupError("Fitness session not found")
        if workout.status != "COMPLETED":
            raise ValueError("Fitness Coach only analyzes completed sessions")
        existing = db.exec(
            select(FitnessCoachRecommendation)
            .where(FitnessCoachRecommendation.session_id == session_id)
            .order_by(col(FitnessCoachRecommendation.created_at).desc())
        ).first()
        if existing is not None:
            run = db.get(AgentRun, existing.run_id)
            if run is not None:
                return run

        run_id = uuid.uuid4()
        run = AgentRun(
            id=run_id,
            graph_name="fitness_coach",
            execution_mode="live",
            trigger=trigger,
            status="queued",
            checkpoint_thread_id=f"fitness-coach:{run_id}",
        )
        db.add(run)
        db.commit()

    try:
        active_provider = provider or get_coach_provider()
        with Session(engine) as db:
            run = db.get(AgentRun, run_id)
            if run is None:
                raise RuntimeError("Fitness Coach run disappeared")
            run.status = "running"
            run.current_node = "graph_start"
            run.message = "Fitness Coach Agent is analyzing the completed workout"
            db.add(run)
            db.commit()

        with checkpoint_saver() as checkpointer:
            graph = build_fitness_coach_graph(
                checkpointer=checkpointer, provider=active_provider
            )
            result = dict(
                graph.invoke(
                    {"run_id": str(run_id), "session_id": str(session_id)},
                    config={"configurable": {"thread_id": f"fitness-coach:{run_id}"}},
                )
            )

        draft = RecommendationDraft.model_validate(result["recommendation"])
        observations = result.get("observations", {})
        payload_text = json.dumps(observations, ensure_ascii=False, sort_keys=True)
        payload_sha256 = hashlib.sha256(payload_text.encode()).hexdigest()
        tool_plan = result.get("tool_plan", {})
        tool_calls = tool_plan.get("tools", []) if isinstance(tool_plan, dict) else []
        with Session(engine) as db:
            recommendation = FitnessCoachRecommendation(
                run_id=run_id,
                session_id=session_id,
                recommendation_type=draft.recommendation_type,
                target_exercise_id=draft.target_exercise_id,
                title=draft.title,
                action=draft.action.model_dump(exclude_none=True),
                reason=draft.reason,
                evidence=[item.model_dump(mode="json") for item in draft.evidence],
                confidence=draft.confidence,
                review_after=draft.review_after,
                provider=active_provider.name,
                model=active_provider.model,
            )
            db.add(recommendation)
            db.flush()
            db.add(
                ModelCallAudit(
                    run_id=run_id,
                    provider=active_provider.name,
                    model=active_provider.model,
                    task="fitness_coach_recommendation",
                    data_class="fitness_training_history",
                    payload_sha256=payload_sha256,
                    status="succeeded",
                )
            )
            db.commit()
            db.refresh(recommendation)
            recommendation_id = recommendation.id
        return _finish_run(
            run_id,
            status="succeeded",
            message="Fitness Coach Agent produced one read-only recommendation",
            result_json={
                "recommendation_id": str(recommendation_id),
                "session_id": str(session_id),
                "provider": active_provider.name,
                "model": active_provider.model,
                "tool_calls": tool_calls,
                "payload_sha256": payload_sha256,
            },
        )
    except Exception as error:
        status = _error_status(error)
        if isinstance(error, ValidationError):
            message = "Fitness Coach output failed structured validation; no recommendation was saved."
        elif status == "awaiting_configuration":
            message = str(error)[:500]
        else:
            message = "Fitness Coach Agent stopped safely; no recommendation was saved."
        return _finish_run(run_id, status=status, message=message, error=error)


def get_recommendation_for_run(run_id: uuid.UUID) -> RecommendationPublic | None:
    with Session(engine) as db:
        value = db.exec(
            select(FitnessCoachRecommendation).where(
                FitnessCoachRecommendation.run_id == run_id
            )
        ).first()
        return None if value is None else RecommendationPublic.model_validate(value)


def list_recommendations(limit: int = 20) -> list[RecommendationPublic]:
    with Session(engine) as db:
        values = list(
            db.exec(
                select(FitnessCoachRecommendation)
                .order_by(col(FitnessCoachRecommendation.created_at).desc())
                .limit(limit)
            ).all()
        )
        return [RecommendationPublic.model_validate(value) for value in values]
