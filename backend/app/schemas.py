import uuid
from datetime import UTC, date, datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator
from pydantic.functional_validators import AfterValidator


def _as_utc(value: datetime | None) -> datetime | None:
    # SQLite reloads datetimes as naive; stored values are UTC.
    if value is not None and value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value


UtcDatetime = Annotated[datetime, AfterValidator(_as_utc)]
UtcDatetimeOrNone = Annotated[datetime | None, AfterValidator(_as_utc)]


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
    updated_at: UtcDatetimeOrNone = None


class LandmarkInput(ApiModel):
    name: str = Field(min_length=1, max_length=200)
    query_text: str = Field(min_length=1, max_length=300)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    rotation_order: int = 0
    enabled: bool = True


class LandmarkPublic(LandmarkInput):
    id: uuid.UUID
    created_at: UtcDatetime


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
    salary_text: str | None
    job_type: str | None
    summary: str | None
    ai_summary: str | None
    geocode_source: str | None
    interview_role_id: str | None
    interview_level: str | None
    fingerprint: str
    published_at: UtcDatetimeOrNone
    first_seen_at: UtcDatetime
    observed_at: UtcDatetime


class RadarPointGeometry(ApiModel):
    type: Literal["Point"] = "Point"
    coordinates: tuple[float, float]


class RadarJobProperties(ApiModel):
    id: str
    title: str
    company: str
    distance_km: float | None
    source: str
    url: str
    location_text: str = ""
    salary_text: str | None = None
    job_type: str | None = None
    summary: str | None = None
    ai_summary: str | None = None
    geocode_source: str | None = None
    interview_role_id: str | None = None
    interview_level: str | None = None
    is_new: bool = False
    published_at: UtcDatetimeOrNone = None
    observed_at: UtcDatetimeOrNone = None


class RadarJobFeature(ApiModel):
    type: Literal["Feature"] = "Feature"
    id: str
    geometry: RadarPointGeometry
    properties: RadarJobProperties


class RadarFeatureCollection(ApiModel):
    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: list[RadarJobFeature]


class RadarPendingJob(ApiModel):
    id: str
    title: str
    company: str
    location_text: str
    source: str


class RadarRunStatus(ApiModel):
    finished_at: UtcDatetimeOrNone
    status: str
    trigger: str
    execution_mode: str
    new_count: int
    updated_count: int
    failed_count: int


class RadarSceneResponse(ApiModel):
    mode: Literal["fictional_demo", "local"]
    center: tuple[float, float] | None
    jobs: RadarFeatureCollection
    unresolved_count: int
    total_count: int
    pending_jobs: list[RadarPendingJob] = []
    generated_at: UtcDatetimeOrNone = None
    last_run: RadarRunStatus | None = None
    map_name: str
    map_available: bool


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
    created_at: UtcDatetime
    processed_at: UtcDatetimeOrNone


class ProfileFactPublic(ApiModel):
    id: uuid.UUID
    fact_type: str
    value_json: dict[str, object]
    status: str
    confidence: float
    evidence_artifact_id: uuid.UUID
    created_at: UtcDatetime


class FactStatusInput(ApiModel):
    status: Literal["proposed", "confirmed", "rejected"]


class ResumeDraftPublic(ApiModel):
    id: uuid.UUID
    version: int
    content_json: dict[str, object]
    created_at: UtcDatetime


class WorkEntryInput(ApiModel):
    work_date: date
    content: str = Field(min_length=1, max_length=20_000)
    tags: list[str] = Field(default_factory=list, max_length=20)


class WorkEntryPublic(WorkEntryInput):
    id: uuid.UUID
    created_at: UtcDatetime
    updated_at: UtcDatetime


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
    created_at: UtcDatetime


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
    started_at: UtcDatetime
    finished_at: UtcDatetimeOrNone


class ApprovalPublic(ApiModel):
    id: uuid.UUID
    action: str
    target: str
    data_class: str
    status: str
    created_at: UtcDatetime
    decided_at: UtcDatetimeOrNone


class ApprovalDecision(ApiModel):
    decision: Literal["approved", "rejected"]


class ExternalUrlInput(ApiModel):
    url: HttpUrl


class SchedulePublic(ApiModel):
    job_discovery_enabled: bool
    interval_minutes: int
    live_enabled: bool = False
    sources: list[str] = ["demo"]
    query_text: str = "实习 OR internship"
    last_triggered_at: UtcDatetimeOrNone
    last_run_at: UtcDatetimeOrNone = None
    last_run_status: str | None = None
    last_run_new: int | None = None
    last_run_updated: int | None = None
    last_run_failed: int | None = None
    last_run_message: str | None = None


class ScheduleInput(ApiModel):
    job_discovery_enabled: bool
    interval_minutes: int = Field(ge=15, le=10_080)
    live_enabled: bool = False
    sources: list[str] = Field(default_factory=lambda: ["demo"], min_length=1, max_length=6)
    query_text: str = Field(default="实习 OR internship", min_length=1, max_length=200)


class InterviewHandoffInput(ApiModel):
    push: bool = True
    role_id: str | None = Field(default=None, max_length=80)
    level: str | None = Field(default=None, max_length=40)


class InterviewHandoffResult(ApiModel):
    job_id: uuid.UUID
    role_id: str | None
    level: str | None
    pushed: bool
    push_channel: str
    file: str
    document_external_id: str
    detail: str | None
    push_response: dict[str, object] | None = None
