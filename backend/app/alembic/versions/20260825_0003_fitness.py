"""add independent fitness workout domain

Revision ID: 20260825_0003
Revises: 20260818_0002
Create Date: 2026-08-25
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260825_0003"
down_revision: str | None = "20260818_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "fitness_plan",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_fitness_plan_sort_order", "fitness_plan", ["sort_order"])
    op.create_index("ix_fitness_plan_archived_at", "fitness_plan", ["archived_at"])
    op.create_table(
        "fitness_exercise",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("plan_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("default_weight", sa.Numeric(8, 2), nullable=False),
        sa.Column("default_reps", sa.Integer(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["plan_id"], ["fitness_plan.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("plan_id", "sort_order", name="uq_fitness_exercise_order"),
    )
    op.create_index("ix_fitness_exercise_plan_id", "fitness_exercise", ["plan_id"])
    op.create_index("ix_fitness_exercise_archived_at", "fitness_exercise", ["archived_at"])
    op.create_table(
        "fitness_session",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("plan_id", sa.Uuid(), nullable=False),
        sa.Column("plan_name_snapshot", sa.String(length=120), nullable=False),
        sa.Column("workout_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["plan_id"], ["fitness_plan.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_fitness_session_plan_id", "fitness_session", ["plan_id"])
    op.create_index("ix_fitness_session_workout_date", "fitness_session", ["workout_date"])
    op.create_index("ix_fitness_session_status", "fitness_session", ["status"])
    op.create_index(
        "uq_fitness_single_active_session",
        "fitness_session",
        ["status"],
        unique=True,
        sqlite_where=sa.text("status = 'ACTIVE'"),
        postgresql_where=sa.text("status = 'ACTIVE'"),
    )
    op.create_table(
        "fitness_set",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("exercise_id", sa.Uuid(), nullable=False),
        sa.Column("exercise_name_snapshot", sa.String(length=160), nullable=False),
        sa.Column("weight", sa.Numeric(8, 2), nullable=False),
        sa.Column("reps", sa.Integer(), nullable=False),
        sa.Column("set_order", sa.Integer(), nullable=False),
        sa.Column("client_request_id", sa.String(length=100), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["exercise_id"], ["fitness_exercise.id"]),
        sa.ForeignKeyConstraint(["session_id"], ["fitness_session.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("client_request_id", name="uq_fitness_set_request"),
        sa.UniqueConstraint(
            "session_id", "exercise_id", "set_order", name="uq_fitness_set_order"
        ),
    )
    op.create_index("ix_fitness_set_session_id", "fitness_set", ["session_id"])
    op.create_index("ix_fitness_set_exercise_id", "fitness_set", ["exercise_id"])
    op.create_index(
        "ix_fitness_set_client_request_id", "fitness_set", ["client_request_id"]
    )
    op.create_index(
        "ix_fitness_set_exercise_completed",
        "fitness_set",
        ["exercise_id", "completed_at"],
    )


def downgrade() -> None:
    op.drop_table("fitness_set")
    op.drop_table("fitness_session")
    op.drop_table("fitness_exercise")
    op.drop_table("fitness_plan")
