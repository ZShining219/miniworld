import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Column, DateTime, Index, Numeric, UniqueConstraint, text
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
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    plan_id: uuid.UUID = Field(foreign_key="fitness_plan.id", index=True)
    name: str = Field(max_length=160)
    default_weight: Decimal = Field(
        default=Decimal("0"), sa_column=Column(Numeric(8, 2), nullable=False)
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
