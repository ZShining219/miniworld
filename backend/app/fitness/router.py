import uuid
from collections.abc import Callable
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlmodel import Session

from app.core.db import get_session as get_db_session
from app.fitness import service
from app.fitness.schemas import (
    CalendarStats,
    ExerciseCreate,
    ExerciseLog,
    ExerciseProgress,
    ExercisePublic,
    ExerciseUpdate,
    HistoryItem,
    LegacyExerciseProgress,
    PlanCreate,
    PlanPublic,
    PlanUpdate,
    ProgressMode,
    ReorderInput,
    SessionDetail,
    SessionStart,
    SetCreate,
    SetPublic,
    SetUpdate,
)

router = APIRouter(prefix="/fitness", tags=["fitness"])
SessionDep = Depends(get_db_session)


def _run[ResultT](callable_: Callable[..., ResultT], *args: object) -> ResultT:
    try:
        return callable_(*args)
    except service.FitnessServiceError as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail)


@router.get("/plans", response_model=list[PlanPublic])
def get_plans(db: Session = SessionDep) -> list[PlanPublic]:
    return _run(service.list_plans, db)


@router.post("/plans", response_model=PlanPublic, status_code=status.HTTP_201_CREATED)
def post_plan(payload: PlanCreate, db: Session = SessionDep) -> PlanPublic:
    return _run(service.create_plan, db, payload)


@router.put("/plans/order", response_model=list[PlanPublic])
def put_plan_order(payload: ReorderInput, db: Session = SessionDep) -> list[PlanPublic]:
    return _run(service.reorder_plans, db, payload)


@router.patch("/plans/{plan_id}", response_model=PlanPublic)
@router.put("/plans/{plan_id}", response_model=PlanPublic)
def patch_plan(
    plan_id: uuid.UUID, payload: PlanUpdate, db: Session = SessionDep
) -> PlanPublic:
    return _run(service.update_plan, db, plan_id, payload)


@router.delete("/plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plan(plan_id: uuid.UUID, db: Session = SessionDep) -> Response:
    _run(service.archive_plan, db, plan_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/plans/{plan_id}/exercises", response_model=list[ExercisePublic])
def get_exercises(
    plan_id: uuid.UUID, db: Session = SessionDep
) -> list[ExercisePublic]:
    return _run(service.list_exercises, db, plan_id)


@router.post(
    "/exercises", response_model=ExercisePublic, status_code=status.HTTP_201_CREATED
)
def post_exercise(
    payload: ExerciseCreate, db: Session = SessionDep
) -> ExercisePublic:
    return _run(service.create_exercise, db, payload)


@router.patch("/exercises/{exercise_id}", response_model=ExercisePublic)
@router.put("/exercises/{exercise_id}", response_model=ExercisePublic)
def patch_exercise(
    exercise_id: uuid.UUID, payload: ExerciseUpdate, db: Session = SessionDep
) -> ExercisePublic:
    return _run(service.update_exercise, db, exercise_id, payload)


@router.delete("/exercises/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise(exercise_id: uuid.UUID, db: Session = SessionDep) -> Response:
    _run(service.archive_exercise, db, exercise_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put(
    "/plans/{plan_id}/exercises/order", response_model=list[ExercisePublic]
)
def put_exercise_order(
    plan_id: uuid.UUID, payload: ReorderInput, db: Session = SessionDep
) -> list[ExercisePublic]:
    return _run(service.reorder_exercises, db, plan_id, payload)


@router.get("/sessions/active", response_model=SessionDetail | None)
def get_active_session(db: Session = SessionDep) -> SessionDetail | None:
    return _run(service.get_active_session, db)


@router.post(
    "/sessions", response_model=SessionDetail, status_code=status.HTTP_201_CREATED
)
def post_session(payload: SessionStart, db: Session = SessionDep) -> SessionDetail:
    return _run(service.start_session, db, payload.plan_id)


@router.get("/sessions/{session_id}", response_model=SessionDetail)
def get_fitness_session(
    session_id: uuid.UUID, db: Session = SessionDep
) -> SessionDetail:
    return _run(service.get_session, db, session_id)


@router.post("/sessions/{session_id}/finish", response_model=SessionDetail)
def finish_session(
    session_id: uuid.UUID, db: Session = SessionDep
) -> SessionDetail:
    return _run(service.finish_session, db, session_id)


@router.get(
    "/sessions/{session_id}/exercises/{exercise_id}", response_model=ExerciseLog
)
def get_exercise_log(
    session_id: uuid.UUID, exercise_id: uuid.UUID, db: Session = SessionDep
) -> ExerciseLog:
    return _run(service.get_exercise_log, db, session_id, exercise_id)


@router.post(
    "/sessions/{session_id}/sets",
    response_model=SetPublic,
    status_code=status.HTTP_201_CREATED,
)
def post_set(
    session_id: uuid.UUID, payload: SetCreate, db: Session = SessionDep
) -> SetPublic:
    return _run(service.add_set, db, session_id, payload)


@router.patch("/sets/{set_id}", response_model=SetPublic)
@router.put("/sets/{set_id}", response_model=SetPublic)
def patch_set(
    set_id: uuid.UUID, payload: SetUpdate, db: Session = SessionDep
) -> SetPublic:
    return _run(service.update_set, db, set_id, payload)


@router.delete("/sets/{set_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_set(set_id: uuid.UUID, db: Session = SessionDep) -> Response:
    _run(service.delete_set, db, set_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/history", response_model=list[HistoryItem])
def get_history(
    limit: int = Query(default=100, ge=1, le=500), db: Session = SessionDep
) -> list[HistoryItem]:
    return _run(service.history, db, limit)


@router.get("/stats/calendar", response_model=CalendarStats)
def get_calendar_stats(
    start: date,
    end: date,
    db: Session = SessionDep,
) -> CalendarStats:
    if end < start:
        raise HTTPException(status_code=422, detail="end must not be before start")
    return _run(service.calendar_stats, db, start, end)


@router.get(
    "/stats/exercises/{exercise_id}/progress",
    response_model=ExerciseProgress | LegacyExerciseProgress,
)
def get_exercise_progress(
    exercise_id: uuid.UUID,
    mode: ProgressMode | None = Query(default=None),
    db: Session = SessionDep,
) -> ExerciseProgress | LegacyExerciseProgress:
    return _run(service.exercise_progress, db, exercise_id, mode)
