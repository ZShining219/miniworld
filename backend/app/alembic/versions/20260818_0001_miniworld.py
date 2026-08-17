"""initialize MiniWorld single-user domain

Revision ID: 20260818_0001
Revises:
Create Date: 2026-08-18
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260818_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "private_location",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("exact_address", sa.String(length=500), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("is_demo", sa.Boolean(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "external_landmark",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("query_text", sa.String(length=300), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("rotation_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "job_posting",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("source", sa.String(length=80), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=True),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("company", sa.String(length=300), nullable=False),
        sa.Column("location_text", sa.String(length=500), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("distance_km", sa.Float(), nullable=True),
        sa.Column("distance_status", sa.String(length=40), nullable=False),
        sa.Column("url", sa.String(length=1200), nullable=False),
        sa.Column("job_type", sa.String(length=80), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("fingerprint", sa.String(length=64), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("fingerprint", name="uq_job_fingerprint"),
    )
    for column in ("source", "external_id", "title", "company", "distance_km", "fingerprint"):
        op.create_index(f"ix_job_posting_{column}", "job_posting", [column])
    op.create_table(
        "agent_run",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("graph_name", sa.String(length=80), nullable=False),
        sa.Column("execution_mode", sa.String(length=20), nullable=False),
        sa.Column("trigger", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("checkpoint_thread_id", sa.String(length=100), nullable=False),
        sa.Column("current_node", sa.String(length=100), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("result_json", sa.JSON(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("graph_name", "execution_mode", "status", "checkpoint_thread_id"):
        op.create_index(f"ix_agent_run_{column}", "agent_run", [column])
    op.create_table(
        "import_artifact",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("source_type", sa.String(length=40), nullable=False),
        sa.Column("source_label", sa.String(length=500), nullable=False),
        sa.Column("content_sha256", sa.String(length=64), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("source_type", "content_sha256", "status"):
        op.create_index(f"ix_import_artifact_{column}", "import_artifact", [column])
    op.create_table(
        "profile_fact",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("fact_type", sa.String(length=80), nullable=False),
        sa.Column("value_json", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("evidence_artifact_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["evidence_artifact_id"], ["import_artifact.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_profile_fact_fact_type", "profile_fact", ["fact_type"])
    op.create_index("ix_profile_fact_status", "profile_fact", ["status"])
    op.create_table(
        "resume_draft",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("content_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_resume_draft_version", "resume_draft", ["version"])
    op.create_table(
        "work_entry",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("work_date", sa.Date(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_work_entry_work_date", "work_entry", ["work_date"])
    op.create_table(
        "work_report",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("report_type", sa.String(length=20), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("source_entry_ids", sa.JSON(), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("report_type", "period_start", "period_end"):
        op.create_index(f"ix_work_report_{column}", "work_report", [column])
    op.create_table(
        "model_call_audit",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("run_id", sa.Uuid(), nullable=True),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("model", sa.String(length=120), nullable=False),
        sa.Column("task", sa.String(length=80), nullable=False),
        sa.Column("data_class", sa.String(length=80), nullable=False),
        sa.Column("payload_sha256", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["agent_run.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "approval_request",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("action", sa.String(length=120), nullable=False),
        sa.Column("target", sa.String(length=500), nullable=False),
        sa.Column("data_class", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_approval_request_status", "approval_request", ["status"])
    op.create_table(
        "schedule_config",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("job_discovery_enabled", sa.Boolean(), nullable=False),
        sa.Column("interval_minutes", sa.Integer(), nullable=False),
        sa.Column("last_triggered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    for table in (
        "schedule_config",
        "approval_request",
        "model_call_audit",
        "work_report",
        "work_entry",
        "resume_draft",
        "profile_fact",
        "import_artifact",
        "agent_run",
        "job_posting",
        "external_landmark",
        "private_location",
    ):
        op.drop_table(table)
