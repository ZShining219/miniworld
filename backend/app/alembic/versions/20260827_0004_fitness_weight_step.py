"""add per-exercise fitness weight step

Revision ID: 20260827_0004
Revises: 20260825_0003
Create Date: 2026-08-27
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260827_0004"
down_revision: str | None = "20260825_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("fitness_exercise") as batch_op:
        batch_op.add_column(
            sa.Column(
                "weight_step",
                sa.Numeric(4, 2),
                server_default=sa.text("2.50"),
                nullable=False,
            )
        )
        batch_op.create_check_constraint(
            "ck_fitness_exercise_weight_step",
            "weight_step IN (1.00, 2.00, 2.50, 5.00)",
        )


def downgrade() -> None:
    with op.batch_alter_table("fitness_exercise") as batch_op:
        batch_op.drop_constraint(
            "ck_fitness_exercise_weight_step", type_="check"
        )
        batch_op.drop_column("weight_step")
