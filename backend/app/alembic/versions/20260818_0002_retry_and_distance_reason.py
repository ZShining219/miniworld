"""add explicit distance reason and checkpoint retry audit

Revision ID: 20260818_0002
Revises: 20260818_0001
Create Date: 2026-08-18
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260818_0002"
down_revision: str | None = "20260818_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("job_posting", sa.Column("distance_reason", sa.Text(), nullable=True))
    op.add_column(
        "agent_run",
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "agent_run",
        sa.Column("error_history", sa.JSON(), nullable=False, server_default="[]"),
    )


def downgrade() -> None:
    op.drop_column("agent_run", "error_history")
    op.drop_column("agent_run", "retry_count")
    op.drop_column("job_posting", "distance_reason")
