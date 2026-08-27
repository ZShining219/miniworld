import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field
from pydantic.alias_generators import to_camel


class FitnessModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
    )


def _weight_step(value: object) -> float:
    try:
        normalized = Decimal(str(value))
    except Exception as error:
        raise ValueError("weightStep must be one of 1, 2, 2.5, 5") from error
    if normalized not in {
        Decimal("1"),
        Decimal("2"),
        Decimal("2.5"),
        Decimal("5"),
    }:
        raise ValueError("weightStep must be one of 1, 2, 2.5, 5")
    return float(normalized)


WeightStep = Annotated[float, BeforeValidator(_weight_step)]


class PlanCreate(FitnessModel):
    name: str = Field(min_length=1, max_length=120)
    sort_order: int | None = Field(default=None, ge=0)


class PlanUpdate(FitnessModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    sort_order: int | None = Field(default=None, ge=0)


class ReorderInput(FitnessModel):
    ids: list[uuid.UUID] = Field(min_length=1)


class PlanPublic(FitnessModel):
    id: uuid.UUID
    name: str
    sort_order: int
    exercise_count: int = 0
    created_at: datetime
    updated_at: datetime


class ExerciseCreate(FitnessModel):
    plan_id: uuid.UUID
    name: str = Field(min_length=1, max_length=160)
    default_weight: float = Field(default=0, ge=0, le=9999)
    default_reps: int = Field(default=8, ge=0, le=999)
    weight_step: WeightStep = 2.5
    sort_order: int | None = Field(default=None, ge=0)


class ExerciseUpdate(FitnessModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    default_weight: float | None = Field(default=None, ge=0, le=9999)
    default_reps: int | None = Field(default=None, ge=0, le=999)
    weight_step: WeightStep | None = None
    sort_order: int | None = Field(default=None, ge=0)


class ExercisePublic(FitnessModel):
    id: uuid.UUID
    plan_id: uuid.UUID
    name: str
    default_weight: float
    default_reps: int
    weight_step: WeightStep
    sort_order: int
    created_at: datetime
    updated_at: datetime


class SetCreate(FitnessModel):
    exercise_id: uuid.UUID
    weight: float = Field(ge=0, le=9999)
    reps: int = Field(ge=0, le=999)
    client_request_id: str = Field(min_length=8, max_length=100)


class SetUpdate(FitnessModel):
    weight: float | None = Field(default=None, ge=0, le=9999)
    reps: int | None = Field(default=None, ge=0, le=999)


class SetPublic(FitnessModel):
    id: uuid.UUID
    session_id: uuid.UUID
    exercise_id: uuid.UUID
    exercise_name_snapshot: str
    weight: float
    reps: int
    set_order: int
    completed_at: datetime


class SessionStart(FitnessModel):
    plan_id: uuid.UUID


class SessionPublic(FitnessModel):
    id: uuid.UUID
    plan_id: uuid.UUID
    plan_name_snapshot: str
    workout_date: date
    status: str
    started_at: datetime
    finished_at: datetime | None


class SessionExerciseSummary(FitnessModel):
    exercise: ExercisePublic
    completed_set_count: int


class SessionDetail(SessionPublic):
    resumed: bool = False
    exercises: list[SessionExerciseSummary]
    total_set_count: int


class ExerciseLog(FitnessModel):
    session: SessionPublic
    exercise: ExercisePublic
    current_sets: list[SetPublic]
    previous_sets: list[SetPublic]
    suggested_weight: float
    suggested_reps: int


class HistoryExercise(FitnessModel):
    exercise_id: uuid.UUID
    exercise_name: str
    sets: list[SetPublic]


class HistoryItem(FitnessModel):
    session: SessionPublic
    duration_seconds: int
    exercise_count: int
    set_count: int
    exercises: list[HistoryExercise]


class CalendarStats(FitnessModel):
    dates: list[date]


class ProgressPoint(FitnessModel):
    workout_date: date
    session_id: uuid.UUID
    max_weight: float


class ExerciseProgress(FitnessModel):
    exercise_id: uuid.UUID
    exercise_name: str
    points: list[ProgressPoint]
