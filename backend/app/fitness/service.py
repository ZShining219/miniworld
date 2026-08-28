import uuid
from collections import OrderedDict
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, SQLModel, col, func, select

from app.fitness import repository
from app.fitness.models import (
    FitnessExercise,
    FitnessPlan,
    FitnessSession,
    FitnessSet,
)
from app.fitness.schemas import (
    CalendarStats,
    ExerciseCreate,
    ExerciseLog,
    ExerciseProgress,
    ExercisePublic,
    ExerciseUpdate,
    HistoryExercise,
    HistoryItem,
    LegacyExerciseProgress,
    PlanCreate,
    PlanPublic,
    PlanUpdate,
    ProgressDayPoint,
    ProgressMode,
    ProgressPoint,
    ProgressSetPoint,
    ReorderInput,
    SessionDetail,
    SessionExerciseSummary,
    SessionPublic,
    SetCreate,
    SetPublic,
    SetUpdate,
)


class FitnessServiceError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


def _now() -> datetime:
    return datetime.now(UTC)


def _get[ModelT: SQLModel](
    db: Session, model: type[ModelT], object_id: object
) -> ModelT:
    value = db.get(model, object_id)
    if value is None:
        raise FitnessServiceError(404, "Fitness resource not found")
    return value


def _exercise_public(value: FitnessExercise) -> ExercisePublic:
    return ExercisePublic.model_validate(value)


def list_plans(db: Session) -> list[PlanPublic]:
    result: list[PlanPublic] = []
    for plan in repository.active_plans(db):
        result.append(
            PlanPublic(
                **plan.model_dump(),
                exercise_count=len(repository.active_exercises(db, plan.id)),
            )
        )
    return result


def create_plan(db: Session, payload: PlanCreate) -> PlanPublic:
    sort_order = payload.sort_order
    if sort_order is None:
        current = db.exec(select(func.max(FitnessPlan.sort_order))).one()
        sort_order = int(current or -1) + 1
    plan = FitnessPlan(name=payload.name.strip(), sort_order=sort_order)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return PlanPublic(**plan.model_dump(), exercise_count=0)


def update_plan(db: Session, plan_id: uuid.UUID, payload: PlanUpdate) -> PlanPublic:
    plan = _get(db, FitnessPlan, plan_id)
    if plan.archived_at is not None:
        raise FitnessServiceError(404, "Fitness plan not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(plan, key, value.strip() if key == "name" else value)
    plan.updated_at = _now()
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return PlanPublic(
        **plan.model_dump(), exercise_count=len(repository.active_exercises(db, plan.id))
    )


def archive_plan(db: Session, plan_id: uuid.UUID) -> None:
    plan = _get(db, FitnessPlan, plan_id)
    active = repository.active_session(db)
    if active is not None and active.plan_id == plan_id:
        raise FitnessServiceError(409, "Finish the active workout before archiving its plan")
    timestamp = _now()
    plan.archived_at = timestamp
    plan.updated_at = timestamp
    for exercise in repository.active_exercises(db, plan_id):
        exercise.archived_at = timestamp
        exercise.updated_at = timestamp
        db.add(exercise)
    db.add(plan)
    db.commit()


def reorder_plans(db: Session, payload: ReorderInput) -> list[PlanPublic]:
    plans = repository.active_plans(db)
    by_id = {item.id: item for item in plans}
    if set(payload.ids) != set(by_id):
        raise FitnessServiceError(409, "Plan order must contain every active plan once")
    for sort_order, plan_id in enumerate(payload.ids):
        plan = by_id[plan_id]
        plan.sort_order = sort_order
        plan.updated_at = _now()
        db.add(plan)
    db.commit()
    return list_plans(db)


def list_exercises(db: Session, plan_id: uuid.UUID) -> list[ExercisePublic]:
    plan = _get(db, FitnessPlan, plan_id)
    if plan.archived_at is not None:
        raise FitnessServiceError(404, "Fitness plan not found")
    return [_exercise_public(item) for item in repository.active_exercises(db, plan_id)]


def create_exercise(db: Session, payload: ExerciseCreate) -> ExercisePublic:
    plan = _get(db, FitnessPlan, payload.plan_id)
    if plan.archived_at is not None:
        raise FitnessServiceError(404, "Fitness plan not found")
    sort_order = payload.sort_order
    if sort_order is None:
        current = db.exec(
            select(func.max(FitnessExercise.sort_order)).where(
                FitnessExercise.plan_id == payload.plan_id
            )
        ).one()
        sort_order = (-1 if current is None else int(current)) + 1
    exercise = FitnessExercise(
        plan_id=payload.plan_id,
        name=payload.name.strip(),
        default_weight=Decimal(str(payload.default_weight)),
        default_reps=payload.default_reps,
        weight_step=Decimal(str(payload.weight_step)),
        sort_order=sort_order,
    )
    db.add(exercise)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise FitnessServiceError(409, "Exercise order already exists")
    db.refresh(exercise)
    return _exercise_public(exercise)


def update_exercise(
    db: Session, exercise_id: uuid.UUID, payload: ExerciseUpdate
) -> ExercisePublic:
    exercise = _get(db, FitnessExercise, exercise_id)
    if exercise.archived_at is not None:
        raise FitnessServiceError(404, "Fitness exercise not found")
    values = payload.model_dump(exclude_unset=True)
    if "name" in values:
        values["name"] = values["name"].strip()
    if "default_weight" in values:
        values["default_weight"] = Decimal(str(values["default_weight"]))
    if "weight_step" in values:
        values["weight_step"] = Decimal(str(values["weight_step"]))
    for key, value in values.items():
        setattr(exercise, key, value)
    exercise.updated_at = _now()
    db.add(exercise)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise FitnessServiceError(409, "Exercise order already exists")
    db.refresh(exercise)
    return _exercise_public(exercise)


def archive_exercise(db: Session, exercise_id: uuid.UUID) -> None:
    exercise = _get(db, FitnessExercise, exercise_id)
    timestamp = _now()
    exercise.archived_at = timestamp
    exercise.updated_at = timestamp
    db.add(exercise)
    db.commit()


def reorder_exercises(
    db: Session, plan_id: uuid.UUID, payload: ReorderInput
) -> list[ExercisePublic]:
    exercises = repository.active_exercises(db, plan_id)
    by_id = {item.id: item for item in exercises}
    if set(payload.ids) != set(by_id):
        raise FitnessServiceError(409, "Exercise order must contain every active exercise once")
    for temporary_order, exercise in enumerate(exercises, start=1):
        exercise.sort_order = -temporary_order
        db.add(exercise)
    db.flush()
    archived_max = db.exec(
        select(func.max(FitnessExercise.sort_order)).where(
            FitnessExercise.plan_id == plan_id,
            col(FitnessExercise.archived_at).is_not(None),
        )
    ).one()
    first_active_order = (-1 if archived_max is None else int(archived_max)) + 1
    for sort_order, exercise_id in enumerate(payload.ids, start=first_active_order):
        exercise = by_id[exercise_id]
        exercise.sort_order = sort_order
        exercise.updated_at = _now()
        db.add(exercise)
    db.commit()
    return list_exercises(db, plan_id)


def _session_public(value: FitnessSession) -> SessionPublic:
    return SessionPublic.model_validate(value)


def session_detail(
    db: Session, value: FitnessSession, *, resumed: bool = False
) -> SessionDetail:
    exercises = repository.active_exercises(db, value.plan_id)
    all_sets = repository.session_sets(db, value.id)
    counts: dict[uuid.UUID, int] = {}
    for item in all_sets:
        counts[item.exercise_id] = counts.get(item.exercise_id, 0) + 1
    return SessionDetail(
        **_session_public(value).model_dump(),
        resumed=resumed,
        exercises=[
            SessionExerciseSummary(
                exercise=_exercise_public(exercise),
                completed_set_count=counts.get(exercise.id, 0),
            )
            for exercise in exercises
        ],
        total_set_count=len(all_sets),
    )


def get_active_session(db: Session) -> SessionDetail | None:
    active = repository.active_session(db)
    return None if active is None else session_detail(db, active, resumed=True)


def start_session(db: Session, plan_id: uuid.UUID) -> SessionDetail:
    plan = _get(db, FitnessPlan, plan_id)
    if plan.archived_at is not None:
        raise FitnessServiceError(404, "Fitness plan not found")
    active = repository.active_session(db)
    if active is not None:
        if active.plan_id == plan_id:
            return session_detail(db, active, resumed=True)
        raise FitnessServiceError(
            409, f"An active {active.plan_name_snapshot} workout must be finished first"
        )
    value = FitnessSession(
        plan_id=plan.id,
        plan_name_snapshot=plan.name,
        workout_date=date.today(),
    )
    db.add(value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        active = repository.active_session(db)
        if active is not None and active.plan_id == plan_id:
            return session_detail(db, active, resumed=True)
        raise FitnessServiceError(409, "Another workout is already active")
    db.refresh(value)
    return session_detail(db, value)


def get_session(db: Session, session_id: uuid.UUID) -> SessionDetail:
    return session_detail(db, _get(db, FitnessSession, session_id))


def finish_session(db: Session, session_id: uuid.UUID) -> SessionDetail:
    value = _get(db, FitnessSession, session_id)
    if value.status == "COMPLETED":
        return session_detail(db, value)
    value.status = "COMPLETED"
    value.finished_at = _now()
    value.updated_at = value.finished_at
    db.add(value)
    db.commit()
    db.refresh(value)
    return session_detail(db, value)


def get_exercise_log(
    db: Session, session_id: uuid.UUID, exercise_id: uuid.UUID
) -> ExerciseLog:
    workout = _get(db, FitnessSession, session_id)
    exercise = _get(db, FitnessExercise, exercise_id)
    if exercise.plan_id != workout.plan_id:
        raise FitnessServiceError(409, "Exercise does not belong to this workout plan")
    current = repository.session_sets(db, session_id, exercise_id)
    previous = repository.previous_session_sets(db, exercise_id, session_id)
    source = previous[-1] if previous else None
    return ExerciseLog(
        session=_session_public(workout),
        exercise=_exercise_public(exercise),
        current_sets=[SetPublic.model_validate(item) for item in current],
        previous_sets=[SetPublic.model_validate(item) for item in previous],
        suggested_weight=float(source.weight if source else exercise.default_weight),
        suggested_reps=source.reps if source else exercise.default_reps,
    )


def add_set(db: Session, session_id: uuid.UUID, payload: SetCreate) -> SetPublic:
    workout = _get(db, FitnessSession, session_id)
    if workout.status != "ACTIVE":
        raise FitnessServiceError(409, "Only an active workout accepts new sets")
    exercise = _get(db, FitnessExercise, payload.exercise_id)
    if exercise.plan_id != workout.plan_id:
        raise FitnessServiceError(409, "Exercise does not belong to this workout plan")
    existing = db.exec(
        select(FitnessSet).where(
            FitnessSet.client_request_id == payload.client_request_id
        )
    ).first()
    if existing is not None:
        if existing.session_id != session_id or existing.exercise_id != payload.exercise_id:
            raise FitnessServiceError(409, "Set request id is already in use")
        return SetPublic.model_validate(existing)
    value = FitnessSet(
        session_id=session_id,
        exercise_id=exercise.id,
        exercise_name_snapshot=exercise.name,
        weight=Decimal(str(payload.weight)),
        reps=payload.reps,
        set_order=repository.next_set_order(db, session_id, exercise.id),
        client_request_id=payload.client_request_id,
    )
    db.add(value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.exec(
            select(FitnessSet).where(
                FitnessSet.client_request_id == payload.client_request_id
            )
        ).first()
        if existing is not None:
            return SetPublic.model_validate(existing)
        raise FitnessServiceError(409, "The set could not be ordered safely; retry")
    db.refresh(value)
    return SetPublic.model_validate(value)


def update_set(db: Session, set_id: uuid.UUID, payload: SetUpdate) -> SetPublic:
    value = _get(db, FitnessSet, set_id)
    updates = payload.model_dump(exclude_unset=True)
    if "weight" in updates:
        updates["weight"] = Decimal(str(updates["weight"]))
    for key, item in updates.items():
        setattr(value, key, item)
    value.updated_at = _now()
    db.add(value)
    db.commit()
    db.refresh(value)
    return SetPublic.model_validate(value)


def delete_set(db: Session, set_id: uuid.UUID) -> None:
    db.delete(_get(db, FitnessSet, set_id))
    db.commit()


def history(db: Session, limit: int = 100) -> list[HistoryItem]:
    items: list[HistoryItem] = []
    for workout in repository.completed_sessions(db, limit=limit):
        sets = repository.session_sets(db, workout.id)
        grouped: OrderedDict[uuid.UUID, list[FitnessSet]] = OrderedDict()
        for item in sets:
            grouped.setdefault(item.exercise_id, []).append(item)
        exercises = [
            HistoryExercise(
                exercise_id=exercise_id,
                exercise_name=exercise_sets[0].exercise_name_snapshot,
                sets=[SetPublic.model_validate(item) for item in exercise_sets],
            )
            for exercise_id, exercise_sets in grouped.items()
        ]
        duration = 0
        if workout.finished_at is not None:
            duration = max(0, int((workout.finished_at - workout.started_at).total_seconds()))
        items.append(
            HistoryItem(
                session=_session_public(workout),
                duration_seconds=duration,
                exercise_count=len(exercises),
                set_count=len(sets),
                exercises=exercises,
            )
        )
    return items


def calendar_stats(db: Session, start: date, end: date) -> CalendarStats:
    dates = sorted(
        {item.workout_date for item in repository.completed_sessions(db, start=start, end=end)}
    )
    return CalendarStats(dates=dates)


def exercise_progress(
    db: Session, exercise_id: uuid.UUID, mode: ProgressMode | None = None
) -> ExerciseProgress | LegacyExerciseProgress:
    exercise = _get(db, FitnessExercise, exercise_id)
    if mode is None:
        legacy_rows = db.exec(
            select(
                col(FitnessSession.workout_date),
                col(FitnessSession.id),
                func.max(FitnessSet.weight),
            )
            .join(FitnessSet, col(FitnessSet.session_id) == col(FitnessSession.id))
            .where(
                FitnessSet.exercise_id == exercise_id,
                FitnessSession.status == "COMPLETED",
            )
            .group_by(col(FitnessSession.workout_date), col(FitnessSession.id))
            .order_by(col(FitnessSession.workout_date), col(FitnessSession.id))
        ).all()
        return LegacyExerciseProgress(
            exercise_id=exercise.id,
            exercise_name=exercise.name,
            points=[
                ProgressPoint(
                    workout_date=workout_date,
                    session_id=session_id,
                    max_weight=float(max_weight),
                )
                for workout_date, session_id, max_weight in legacy_rows
            ],
        )

    set_rows = db.exec(
        select(FitnessSet, col(FitnessSession.workout_date))
        .join(FitnessSession, col(FitnessSet.session_id) == col(FitnessSession.id))
        .where(
            FitnessSet.exercise_id == exercise_id,
            FitnessSession.status == "COMPLETED",
        )
        .order_by(
            col(FitnessSession.workout_date),
            col(FitnessSet.completed_at),
            col(FitnessSet.set_order),
        )
    ).all()
    progress_points: list[ProgressSetPoint | ProgressDayPoint]
    if mode == "set":
        progress_points = [
            ProgressSetPoint(
                workout_date=workout_date,
                session_id=fitness_set.session_id,
                completed_at=fitness_set.completed_at,
                set_order=fitness_set.set_order,
                weight=float(fitness_set.weight),
                reps=fitness_set.reps,
            )
            for fitness_set, workout_date in set_rows
        ]
    else:
        grouped: OrderedDict[date, list[FitnessSet]] = OrderedDict()
        for fitness_set, workout_date in set_rows:
            grouped.setdefault(workout_date, []).append(fitness_set)
        progress_points = []
        for workout_date, day_sets in grouped.items():
            weights = [float(item.weight) for item in day_sets]
            progress_points.append(
                ProgressDayPoint(
                    workout_date=workout_date,
                    average_weight=sum(weights) / len(weights),
                    min_weight=min(weights),
                    max_weight=max(weights),
                    set_count=len(day_sets),
                    session_count=len({item.session_id for item in day_sets}),
                )
            )
    return ExerciseProgress(
        exercise_id=exercise.id,
        exercise_name=exercise.name,
        mode=mode,
        points=progress_points,
    )
