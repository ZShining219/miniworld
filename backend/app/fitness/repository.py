import uuid
from datetime import date

from sqlmodel import Session, col, func, select

from app.fitness.models import (
    FitnessExercise,
    FitnessPlan,
    FitnessSession,
    FitnessSet,
)


def active_plans(db: Session) -> list[FitnessPlan]:
    return list(
        db.exec(
            select(FitnessPlan)
            .where(col(FitnessPlan.archived_at).is_(None))
            .order_by(col(FitnessPlan.sort_order), col(FitnessPlan.created_at))
        ).all()
    )


def active_exercises(db: Session, plan_id: uuid.UUID) -> list[FitnessExercise]:
    return list(
        db.exec(
            select(FitnessExercise)
            .where(
                FitnessExercise.plan_id == plan_id,
                col(FitnessExercise.archived_at).is_(None),
            )
            .order_by(col(FitnessExercise.sort_order), col(FitnessExercise.created_at))
        ).all()
    )


def active_session(db: Session) -> FitnessSession | None:
    return db.exec(
        select(FitnessSession).where(FitnessSession.status == "ACTIVE")
    ).first()


def session_sets(
    db: Session, session_id: uuid.UUID, exercise_id: uuid.UUID | None = None
) -> list[FitnessSet]:
    statement = select(FitnessSet).where(FitnessSet.session_id == session_id)
    if exercise_id is not None:
        statement = statement.where(FitnessSet.exercise_id == exercise_id)
    return list(
        db.exec(statement.order_by(col(FitnessSet.completed_at), col(FitnessSet.id))).all()
    )


def next_set_order(db: Session, session_id: uuid.UUID, exercise_id: uuid.UUID) -> int:
    value = db.exec(
        select(func.max(FitnessSet.set_order)).where(
            FitnessSet.session_id == session_id,
            FitnessSet.exercise_id == exercise_id,
        )
    ).one()
    return int(value or 0) + 1


def previous_session_sets(
    db: Session,
    exercise_id: uuid.UUID,
    current_session_id: uuid.UUID,
) -> list[FitnessSet]:
    previous_id = db.exec(
        select(FitnessSet.session_id)
        .join(
            FitnessSession,
            col(FitnessSet.session_id) == col(FitnessSession.id),
        )
        .where(
            FitnessSet.exercise_id == exercise_id,
            FitnessSet.session_id != current_session_id,
            FitnessSession.status == "COMPLETED",
        )
        .order_by(col(FitnessSession.finished_at).desc())
        .limit(1)
    ).first()
    return [] if previous_id is None else session_sets(db, previous_id, exercise_id)


def completed_sessions(
    db: Session,
    *,
    start: date | None = None,
    end: date | None = None,
    limit: int = 100,
) -> list[FitnessSession]:
    statement = select(FitnessSession).where(FitnessSession.status == "COMPLETED")
    if start is not None:
        statement = statement.where(FitnessSession.workout_date >= start)
    if end is not None:
        statement = statement.where(FitnessSession.workout_date <= end)
    return list(
        db.exec(
            statement.order_by(col(FitnessSession.workout_date).desc()).limit(limit)
        ).all()
    )
