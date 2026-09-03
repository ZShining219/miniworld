"""add fitness coach recommendations

Revision ID: 20260903_0005
Revises: 20260827_0004
Create Date: 2026-09-03
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260903_0005"
down_revision: str | None = "20260827_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "fitness_coach_recommendation",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("run_id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("recommendation_type", sa.String(length=40), nullable=False),
        sa.Column("target_exercise_id", sa.Uuid(), nullable=True),
        sa.Column("title", sa.String(length=240), nullable=False),
        sa.Column("action", sa.JSON(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("review_after", sa.String(length=80), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("model", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["agent_run.id"]),
        sa.ForeignKeyConstraint(["session_id"], ["fitness_session.id"]),
        sa.ForeignKeyConstraint(["target_exercise_id"], ["fitness_exercise.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("run_id", name="uq_fitness_coach_recommendation_run"),
        sa.UniqueConstraint(
            "session_id", name="uq_fitness_coach_recommendation_session"
        ),
    )
    op.create_index(
        "ix_fitness_coach_recommendation_run_id",
        "fitness_coach_recommendation",
        ["run_id"],
    )
    op.create_index(
        "ix_fitness_coach_recommendation_session_id",
        "fitness_coach_recommendation",
        ["session_id"],
    )
    op.create_index(
        "ix_fitness_coach_recommendation_target_exercise_id",
        "fitness_coach_recommendation",
        ["target_exercise_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_fitness_coach_recommendation_target_exercise_id",
        table_name="fitness_coach_recommendation",
    )
    op.drop_index(
        "ix_fitness_coach_recommendation_session_id",
        table_name="fitness_coach_recommendation",
    )
    op.drop_index(
        "ix_fitness_coach_recommendation_run_id",
        table_name="fitness_coach_recommendation",
    )
    op.drop_table("fitness_coach_recommendation")
