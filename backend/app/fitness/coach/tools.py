import uuid
from collections.abc import Callable
from typing import TypedDict, cast

from sqlmodel import Session, col, select

from app.fitness.models import FitnessSession, FitnessSet


class CoachToolError(RuntimeError):
    pass


def completed_session(db: Session, session_id: uuid.UUID) -> dict[str, object]:
    workout = db.get(FitnessSession, session_id)
    if workout is None:
        raise CoachToolError("Fitness session not found")
    if workout.status != "COMPLETED":
        raise CoachToolError("Fitness Coach only analyzes completed sessions")
    sets = list(
        db.exec(
            select(FitnessSet)
            .where(FitnessSet.session_id == session_id)
            .order_by(col(FitnessSet.completed_at), col(FitnessSet.set_order))
        ).all()
    )
    return {
        "session_id": str(workout.id),
        "workout_date": workout.workout_date.isoformat(),
        "plan_name": workout.plan_name_snapshot,
        "sets": [
            {
                "exercise_id": str(item.exercise_id),
                "exercise_name": item.exercise_name_snapshot,
                "weight": float(item.weight),
                "reps": item.reps,
                "set_order": item.set_order,
            }
            for item in sets
        ],
    }


def exercise_history(
    db: Session, session_id: uuid.UUID, focus_exercise_id: uuid.UUID | None
) -> dict[str, object]:
    current = completed_session(db, session_id)
    current_sets = current.get("sets")
    if not isinstance(current_sets, list):
        raise CoachToolError("Completed session tool returned invalid sets")
    current_ids: set[uuid.UUID] = set()
    for raw_item in current_sets:
        if isinstance(raw_item, dict) and "exercise_id" in raw_item:
            current_item = cast(dict[str, object], raw_item)
            current_ids.add(uuid.UUID(str(current_item["exercise_id"])))
    if focus_exercise_id is not None:
        if focus_exercise_id not in current_ids:
            raise CoachToolError("Focused exercise is not part of the completed session")
        exercise_ids = {focus_exercise_id}
    else:
        exercise_ids = current_ids
    if not exercise_ids:
        return {"exercises": []}

    rows = list(
        db.exec(
            select(FitnessSet, FitnessSession)
            .join(
                FitnessSession,
                col(FitnessSession.id) == col(FitnessSet.session_id),
            )
            .where(
                col(FitnessSet.exercise_id).in_(exercise_ids),
                FitnessSession.status == "COMPLETED",
            )
            .order_by(col(FitnessSession.workout_date).desc(), col(FitnessSet.completed_at).desc())
            .limit(80)
        ).all()
    )
    class HistoryEntry(TypedDict):
        exercise_id: str
        exercise_name: str
        sets: list[dict[str, object]]

    grouped: dict[str, HistoryEntry] = {}
    for item, workout in rows:
        key = str(item.exercise_id)
        entry = grouped.setdefault(
            key,
            {
                "exercise_id": key,
                "exercise_name": item.exercise_name_snapshot,
                "sets": [],
            },
        )
        entry["sets"].append(
            {
                "session_id": str(workout.id),
                "workout_date": workout.workout_date.isoformat(),
                "weight": float(item.weight),
                "reps": item.reps,
                "set_order": item.set_order,
            }
        )
    return {"exercises": list(grouped.values())}


ToolCallable = Callable[[Session, uuid.UUID, uuid.UUID | None], dict[str, object]]


def run_tool(
    name: str,
    db: Session,
    session_id: uuid.UUID,
    focus_exercise_id: uuid.UUID | None,
) -> dict[str, object]:
    if name == "completed_session":
        return completed_session(db, session_id)
    if name == "exercise_history":
        return exercise_history(db, session_id, focus_exercise_id)
    raise CoachToolError(f"Unsupported Fitness Coach tool: {name}")
