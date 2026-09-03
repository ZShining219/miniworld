import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    JSON,
    CheckConstraint,
    Column,
    DateTime,
    Index,
    Numeric,
    Text,
    UniqueConstraint,
    text,
)
from sqlmodel import Field, SQLModel

from app.models import utc_now


class FitnessPlan(SQLModel, table=True):
    __tablename__ = "fitness_plan"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=120)
    sort_order: int = Field(default=0, index=True)
    archived_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), index=True)
    )
    created_at: datetime = Field(
        default_factory=utc_now, sa_column=Column(DateTime(timezone=True))
    )
    updated_at: datetime = Field(
        default_factory=utc_now, sa_column=Column(DateTime(timezone=True))
    )


class FitnessExercise(SQLModel, table=True):
    __tablename__ = "fitness_exercise"
    __table_args__ = (
        UniqueConstraint("plan_id", "sort_order", name="uq_fitness_exercise_order"),
        CheckConstraint(
            "weight_step IN (1.00, 2.00, 2.50, 5.00)",
            name="ck_fitness_exercise_weight_step",
        ),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    plan_id: uuid.UUID = Field(foreign_key="fitness_plan.id", index=True)
    name: str = Field(max_length=160)
    default_weight: Decimal = Field(
        default=Decimal("0"), sa_column=Column(Numeric(8, 2), nullable=False)
    )
    weight_step: Decimal = Field(
        default=Decimal("2.5"),
        sa_column=Column(
            Numeric(4, 2), nullable=False, server_default=text("2.50")
        ),
    )
    default_reps: int = Field(default=8)
    sort_order: int = Field(default=0)
    archived_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), index=True)
    )
    created_at: datetime = Field(
        default_factory=utc_now, sa_column=Column(DateTime(timezone=True))
    )
    updated_at: datetime = Field(
        default_factory=utc_now, sa_column=Column(DateTime(timezone=True))
    )


class FitnessSession(SQLModel, table=True):
    __tablename__ = "fitness_session"
    __table_args__ = (
        Index(
            "uq_fitness_single_active_session",
            "status",
            unique=True,
            sqlite_where=text("status = 'ACTIVE'"),
            postgresql_where=text("status = 'ACTIVE'"),
        ),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    plan_id: uuid.UUID = Field(foreign_key="fitness_plan.id", index=True)
    plan_name_snapshot: str = Field(max_length=120)
    workout_date: date = Field(index=True)
    status: str = Field(default="ACTIVE", index=True, max_length=20)
    started_at: datetime = Field(
        default_factory=utc_now, sa_column=Column(DateTime(timezone=True))
    )
    finished_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    created_at: datetime = Field(
        default_factory=utc_now, sa_column=Column(DateTime(timezone=True))
    )
    updated_at: datetime = Field(
        default_factory=utc_now, sa_column=Column(DateTime(timezone=True))
    )


class FitnessSet(SQLModel, table=True):
    __tablename__ = "fitness_set"
    __table_args__ = (
        UniqueConstraint("client_request_id", name="uq_fitness_set_request"),
        UniqueConstraint(
            "session_id",
            "exercise_id",
            "set_order",
            name="uq_fitness_set_order",
        ),
        Index("ix_fitness_set_exercise_completed", "exercise_id", "completed_at"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    session_id: uuid.UUID = Field(foreign_key="fitness_session.id", index=True)
    exercise_id: uuid.UUID = Field(foreign_key="fitness_exercise.id", index=True)
    exercise_name_snapshot: str = Field(max_length=160)
    weight: Decimal = Field(sa_column=Column(Numeric(8, 2), nullable=False))
    reps: int
    set_order: int
    client_request_id: str = Field(max_length=100, index=True)
    completed_at: datetime = Field(
        default_factory=utc_now, sa_column=Column(DateTime(timezone=True))
    )
    created_at: datetime = Field(
        default_factory=utc_now, sa_column=Column(DateTime(timezone=True))
    )
    updated_at: datetime = Field(
        default_factory=utc_now, sa_column=Column(DateTime(timezone=True))
    )


class FitnessCoachRecommendation(SQLModel, table=True):
    """Immutable-by-default, read-only advice produced by Fitness Coach."""

    __tablename__ = "fitness_coach_recommendation"
    __table_args__ = (
        UniqueConstraint("run_id", name="uq_fitness_coach_recommendation_run"),
        UniqueConstraint("session_id", name="uq_fitness_coach_recommendation_session"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    run_id: uuid.UUID = Field(foreign_key="agent_run.id", index=True)
    session_id: uuid.UUID = Field(foreign_key="fitness_session.id", index=True)
    recommendation_type: str = Field(max_length=40)
    target_exercise_id: uuid.UUID | None = Field(
        default=None, foreign_key="fitness_exercise.id", index=True
    )
    title: str = Field(max_length=240)
    action: dict[str, object] = Field(sa_column=Column(JSON, nullable=False))
    reason: str = Field(sa_column=Column(Text, nullable=False))
    evidence: list[dict[str, object]] = Field(sa_column=Column(JSON, nullable=False))
    confidence: float = Field(ge=0, le=1)
    review_after: str = Field(max_length=80)
    provider: str = Field(max_length=80)
    model: str = Field(max_length=120)
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True)),
    )
