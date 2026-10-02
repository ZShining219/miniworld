"""radar active-fetch loop fields

Adds persisted salary, geocode provenance, first-seen tracking and interview
handoff hints to job postings, plus scheduler source/status write-back columns.

Revision ID: 20261002_0007
Revises: 20260903_0005
Create Date: 2026-10-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20261002_0007"
down_revision: str | None = "20260903_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "job_posting",
        sa.Column("geocode_source", sa.String(length=80), nullable=True),
    )
    op.add_column(
        "job_posting",
        sa.Column("salary_text", sa.String(length=200), nullable=True),
    )
    op.add_column("job_posting", sa.Column("ai_summary", sa.Text(), nullable=True))
    op.add_column(
        "job_posting",
        sa.Column("interview_role_id", sa.String(length=80), nullable=True),
    )
    op.add_column(
        "job_posting",
        sa.Column("interview_level", sa.String(length=40), nullable=True),
    )
    op.add_column(
        "job_posting",
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.execute(
        "UPDATE job_posting SET first_seen_at = observed_at "
        "WHERE first_seen_at IS NULL"
    )
    op.alter_column("job_posting", "first_seen_at", nullable=False)

    op.add_column(
        "schedule_config",
        sa.Column(
            "live_enabled", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
    )
    op.add_column(
        "schedule_config",
        sa.Column(
            "sources",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[\"demo\"]'"),
        ),
    )
    op.add_column(
        "schedule_config",
        sa.Column(
            "query_text",
            sa.String(length=200),
            nullable=False,
            server_default="实习 OR internship",
        ),
    )
    op.add_column(
        "schedule_config",
        sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "schedule_config",
        sa.Column("last_run_status", sa.String(length=40), nullable=True),
    )
    op.add_column(
        "schedule_config", sa.Column("last_run_new", sa.Integer(), nullable=True)
    )
    op.add_column(
        "schedule_config",
        sa.Column("last_run_updated", sa.Integer(), nullable=True),
    )
    op.add_column(
        "schedule_config",
        sa.Column("last_run_failed", sa.Integer(), nullable=True),
    )
    op.add_column(
        "schedule_config",
        sa.Column("last_run_message", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("schedule_config", "last_run_message")
    op.drop_column("schedule_config", "last_run_failed")
    op.drop_column("schedule_config", "last_run_updated")
    op.drop_column("schedule_config", "last_run_new")
    op.drop_column("schedule_config", "last_run_status")
    op.drop_column("schedule_config", "last_run_at")
    op.drop_column("schedule_config", "query_text")
    op.drop_column("schedule_config", "sources")
    op.drop_column("schedule_config", "live_enabled")

    op.drop_column("job_posting", "first_seen_at")
    op.drop_column("job_posting", "interview_level")
    op.drop_column("job_posting", "interview_role_id")
    op.drop_column("job_posting", "ai_summary")
    op.drop_column("job_posting", "salary_text")
    op.drop_column("job_posting", "geocode_source")
