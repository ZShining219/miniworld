import uuid
from datetime import UTC, date, datetime

from sqlalchemy import JSON, Column, DateTime, Text, UniqueConstraint
from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(UTC)


class PrivateLocation(SQLModel, table=True):
    __tablename__ = "private_location"

    id: int = Field(default=1, primary_key=True)
    exact_address: str = Field(max_length=500)
    latitude: float
    longitude: float
    is_demo: bool = False
    updated_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True)),
    )


class ExternalLandmark(SQLModel, table=True):
    __tablename__ = "external_landmark"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=200)
    query_text: str = Field(max_length=300)
    latitude: float | None = None
    longitude: float | None = None
    enabled: bool = True
    rotation_order: int = 0
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True)),
    )


class JobPosting(SQLModel, table=True):
    __tablename__ = "job_posting"
    __table_args__ = (UniqueConstraint("fingerprint", name="uq_job_fingerprint"),)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    source: str = Field(index=True, max_length=80)
    external_id: str | None = Field(default=None, index=True, max_length=255)
    title: str = Field(index=True, max_length=300)
    company: str = Field(index=True, max_length=300)
    location_text: str = Field(max_length=500)
    latitude: float | None = None
    longitude: float | None = None
    distance_km: float | None = Field(default=None, index=True)
    distance_status: str = Field(default="location_unresolved", max_length=40)
    url: str = Field(max_length=1200)
    job_type: str | None = Field(default=None, max_length=80)
    summary: str | None = Field(default=None, sa_column=Column(Text))
    fingerprint: str = Field(index=True, max_length=64)
    published_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    observed_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True)),
    )


class AgentRun(SQLModel, table=True):
    __tablename__ = "agent_run"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    graph_name: str = Field(index=True, max_length=80)
    execution_mode: str = Field(default="demo", index=True, max_length=20)
    trigger: str = Field(default="manual", max_length=40)
    status: str = Field(default="queued", index=True, max_length=40)
    checkpoint_thread_id: str = Field(index=True, max_length=100)
    current_node: str | None = Field(default=None, max_length=100)
    message: str | None = Field(default=None, sa_column=Column(Text))
    result_json: dict[str, object] | None = Field(default=None, sa_column=Column(JSON))
    started_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True)),
    )
    finished_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )


class ImportArtifact(SQLModel, table=True):
    __tablename__ = "import_artifact"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    source_type: str = Field(index=True, max_length=40)
    source_label: str = Field(max_length=500)
    content_sha256: str = Field(index=True, max_length=64)
    content: str = Field(sa_column=Column(Text))
    status: str = Field(default="parsed", index=True, max_length=40)
    processed_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True)),
    )


class ProfileFact(SQLModel, table=True):
    __tablename__ = "profile_fact"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    fact_type: str = Field(index=True, max_length=80)
    value_json: dict[str, object] = Field(sa_column=Column(JSON))
    status: str = Field(default="proposed", index=True, max_length=40)
    confidence: float = 0.5
    evidence_artifact_id: uuid.UUID = Field(foreign_key="import_artifact.id")
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True)),
    )


class ResumeDraft(SQLModel, table=True):
    __tablename__ = "resume_draft"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    version: int = Field(index=True)
    content_json: dict[str, object] = Field(sa_column=Column(JSON))
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True)),
    )


class WorkEntry(SQLModel, table=True):
    __tablename__ = "work_entry"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    work_date: date = Field(index=True)
    content: str = Field(sa_column=Column(Text))
    tags: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True)),
    )
    updated_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True)),
    )


class WorkReport(SQLModel, table=True):
    __tablename__ = "work_report"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    report_type: str = Field(index=True, max_length=20)
    period_start: date = Field(index=True)
    period_end: date = Field(index=True)
    content: str = Field(sa_column=Column(Text))
    source_entry_ids: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    provider: str = Field(default="demo", max_length=80)
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True)),
    )


class ModelCallAudit(SQLModel, table=True):
    __tablename__ = "model_call_audit"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    run_id: uuid.UUID | None = Field(default=None, foreign_key="agent_run.id")
    provider: str = Field(max_length=80)
    model: str = Field(max_length=120)
    task: str = Field(max_length=80)
    data_class: str = Field(max_length=80)
    payload_sha256: str = Field(max_length=64)
    status: str = Field(max_length=40)
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True)),
    )


class ApprovalRequest(SQLModel, table=True):
    __tablename__ = "approval_request"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    action: str = Field(max_length=120)
    target: str = Field(max_length=500)
    data_class: str = Field(max_length=120)
    status: str = Field(default="pending", index=True, max_length=40)
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True)),
    )
    decided_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )


class ScheduleConfig(SQLModel, table=True):
    __tablename__ = "schedule_config"

    id: int = Field(default=1, primary_key=True)
    job_discovery_enabled: bool = True
    interval_minutes: int = 720
    last_triggered_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
    )
    updated_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True)),
    )
