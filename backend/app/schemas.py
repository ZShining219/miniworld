import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


class ApiModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class HealthResponse(ApiModel):
    status: str
    project: str
    execution_mode: str
    database: str
    checkpoint_mode: str


class OverviewResponse(ApiModel):
    execution_mode: str
    provider_mode: str
    live_job_search_enabled: bool
    location_configured: bool
    landmark_count: int
    job_count: int
    fact_count: int
    resume_version: int | None
    work_entry_count: int
    report_count: int
    pending_approvals: int
    recent_runs: list[AgentRunPublic]


class LocationInput(ApiModel):
    exact_address: str = Field(min_length=1, max_length=500)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    is_demo: bool = False


class LocationStatus(ApiModel):
    configured: bool
    masked_address: str | None = None
    is_demo: bool = False
    updated_at: datetime | None = None


class LandmarkInput(ApiModel):
    name: str = Field(min_length=1, max_length=200)
    query_text: str = Field(min_length=1, max_length=300)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    rotation_order: int = 0
    enabled: bool = True


class LandmarkPublic(LandmarkInput):
    id: uuid.UUID
    created_at: datetime


class JobRunRequest(ApiModel):
    query: str = Field(default="实习 OR internship", min_length=1, max_length=200)
    live: bool = False


class JobPublic(ApiModel):
    id: uuid.UUID
    source: str
    external_id: str | None
    title: str
    company: str
    location_text: str
    distance_km: float | None
    distance_status: str
    distance_reason: str | None
    url: str
    job_type: str | None
    summary: str | None
    published_at: datetime | None
    observed_at: datetime


class ImportTextRequest(ApiModel):
    source_type: Literal["file", "github", "gpt_conversation"]
    source_label: str = Field(min_length=1, max_length=500)
    content: str = Field(min_length=1, max_length=200_000)


class ImportPublic(ApiModel):
    id: uuid.UUID
    source_type: str
    source_label: str
    content_sha256: str
    status: str
    created_at: datetime
    processed_at: datetime | None


class ProfileFactPublic(ApiModel):
    id: uuid.UUID
    fact_type: str
    value_json: dict[str, object]
    status: str
    confidence: float
    evidence_artifact_id: uuid.UUID
    created_at: datetime


class FactStatusInput(ApiModel):
    status: Literal["proposed", "confirmed", "rejected"]


class ResumeDraftPublic(ApiModel):
    id: uuid.UUID
    version: int
    content_json: dict[str, object]
    created_at: datetime


class WorkEntryInput(ApiModel):
    work_date: date
    content: str = Field(min_length=1, max_length=20_000)
    tags: list[str] = Field(default_factory=list, max_length=20)


class WorkEntryPublic(WorkEntryInput):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ReportRequest(ApiModel):
    report_type: Literal["daily", "weekly"]
    period_start: date
    period_end: date

    @model_validator(mode="after")
    def validate_period(self) -> ReportRequest:
        if self.period_end < self.period_start:
            raise ValueError("period_end must not be before period_start")
        if self.report_type == "daily" and self.period_end != self.period_start:
            raise ValueError("daily reports must use a single date")
        return self


class WorkReportPublic(ApiModel):
    id: uuid.UUID
    report_type: str
    period_start: date
    period_end: date
    content: str
    source_entry_ids: list[str]
    provider: str
    created_at: datetime


class AgentRunPublic(ApiModel):
    id: uuid.UUID
    graph_name: str
    execution_mode: str
    trigger: str
    status: str
    current_node: str | None
    message: str | None
    result_json: dict[str, object] | None
    retry_count: int
    error_history: list[dict[str, object]]
    started_at: datetime
    finished_at: datetime | None


class ApprovalPublic(ApiModel):
    id: uuid.UUID
    action: str
    target: str
    data_class: str
    status: str
    created_at: datetime
    decided_at: datetime | None


class ApprovalDecision(ApiModel):
    decision: Literal["approved", "rejected"]


class ExternalUrlInput(ApiModel):
    url: HttpUrl


class SchedulePublic(ApiModel):
    job_discovery_enabled: bool
    interval_minutes: int
    last_triggered_at: datetime | None


class ScheduleInput(ApiModel):
    job_discovery_enabled: bool
    interval_minutes: int = Field(ge=15, le=10_080)
