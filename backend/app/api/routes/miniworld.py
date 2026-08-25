import hashlib
import uuid
from datetime import UTC, datetime
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    Response,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from sqlmodel import Session, col, func, select

from app.agent.artifacts import convert_uploaded_bytes
from app.agent.runner import (
    retry_agent_run,
    run_job_discovery,
    run_profile_import,
    run_work_report,
)
from app.core.config import settings
from app.core.db import get_session
from app.models import (
    AgentRun,
    ApprovalRequest,
    ExternalLandmark,
    ImportArtifact,
    JobPosting,
    PrivateLocation,
    ProfileFact,
    ResumeDraft,
    ScheduleConfig,
    WorkEntry,
    WorkReport,
)
from app.schemas import (
    AgentRunPublic,
    ApprovalDecision,
    ApprovalPublic,
    FactStatusInput,
    ImportPublic,
    ImportTextRequest,
    JobPublic,
    JobRunRequest,
    LandmarkInput,
    LandmarkPublic,
    LocationInput,
    LocationStatus,
    OverviewResponse,
    ProfileFactPublic,
    RadarFeatureCollection,
    RadarJobFeature,
    RadarJobProperties,
    RadarPointGeometry,
    RadarSceneResponse,
    ReportRequest,
    ResumeDraftPublic,
    ScheduleInput,
    SchedulePublic,
    WorkEntryInput,
    WorkEntryPublic,
    WorkReportPublic,
)
from app.worker import run_schedule_tick

router = APIRouter()
SessionDep = Depends(get_session)

RADAR_MAP_NAME = "demo-firenze.pmtiles"
DEMO_RADAR_CENTER = (11.2543435, 43.7672134)
DEMO_RADAR_JOBS = (
    ("signal-01", "AI 产品实习生", "Arno Research", 0.7, 11.2604, 43.7708),
    ("signal-02", "前端工程实习生", "Studio Nodo", 1.1, 11.2478, 43.7639),
    ("signal-03", "数据分析助理", "Campo Labs", 1.4, 11.2659, 43.7631),
    ("signal-04", "研究工程师", "Forma Systems", 1.8, 11.242, 43.7752),
)


def _get_or_404(session: Session, model, object_id):
    value = session.get(model, object_id)
    if value is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    return value


@router.get("/radar/maps/{map_name}", tags=["radar"])
def get_radar_map(map_name: str) -> FileResponse:
    if map_name != Path(map_name).name or not map_name.endswith(".pmtiles"):
        raise HTTPException(status_code=404, detail="Radar map not found")

    map_root = settings.RADAR_MAP_DIR.resolve()
    map_path = (map_root / map_name).resolve()
    if map_path.parent != map_root or not map_path.is_file():
        raise HTTPException(status_code=404, detail="Radar map not found")

    return FileResponse(
        map_path,
        media_type="application/vnd.pmtiles",
        headers={
            "Cache-Control": "private, max-age=86400",
            "X-Content-Type-Options": "nosniff",
        },
    )


def _radar_feature(
    *,
    job_id: str,
    title: str,
    company: str,
    distance_km: float | None,
    source: str,
    url: str,
    longitude: float,
    latitude: float,
) -> RadarJobFeature:
    return RadarJobFeature(
        id=job_id,
        geometry=RadarPointGeometry(coordinates=(longitude, latitude)),
        properties=RadarJobProperties(
            id=job_id,
            title=title,
            company=company,
            distance_km=distance_km,
            source=source,
            url=url,
        ),
    )


@router.get("/radar/scene", response_model=RadarSceneResponse, tags=["radar"])
def get_radar_scene(
    response: Response, session: Session = SessionDep
) -> RadarSceneResponse:
    response.headers["Cache-Control"] = "no-store"
    map_available = (settings.RADAR_MAP_DIR.resolve() / RADAR_MAP_NAME).is_file()

    if settings.EXECUTION_MODE == "demo":
        features = [
            _radar_feature(
                job_id=job_id,
                title=title,
                company=company,
                distance_km=distance_km,
                source="fictional-demo",
                url="",
                longitude=longitude,
                latitude=latitude,
            )
            for job_id, title, company, distance_km, longitude, latitude in DEMO_RADAR_JOBS
        ]
        return RadarSceneResponse(
            mode="fictional_demo",
            center=DEMO_RADAR_CENTER,
            jobs=RadarFeatureCollection(features=features),
            unresolved_count=0,
            total_count=len(features),
            map_name=RADAR_MAP_NAME,
            map_available=map_available,
        )

    location = session.get(PrivateLocation, 1)
    jobs = list(session.exec(select(JobPosting)).all())
    mapped_jobs = [
        job
        for job in jobs
        if job.distance_status == "calculated"
        and job.latitude is not None
        and job.longitude is not None
    ]
    features = [
        _radar_feature(
            job_id=str(job.id),
            title=job.title,
            company=job.company,
            distance_km=job.distance_km,
            source=job.source,
            url=job.url,
            longitude=job.longitude,
            latitude=job.latitude,
        )
        for job in mapped_jobs
        if job.longitude is not None and job.latitude is not None
    ]
    center = None if location is None else (location.longitude, location.latitude)
    return RadarSceneResponse(
        mode="local",
        center=center,
        jobs=RadarFeatureCollection(features=features),
        unresolved_count=len(jobs) - len(features),
        total_count=len(jobs),
        map_name=RADAR_MAP_NAME,
        map_available=map_available,
    )


@router.get("/overview", response_model=OverviewResponse, tags=["overview"])
def get_overview(session: Session = SessionDep) -> OverviewResponse:
    resume_version = session.exec(select(func.max(ResumeDraft.version))).one()
    recent_runs = list(
        session.exec(
            select(AgentRun).order_by(col(AgentRun.started_at).desc()).limit(6)
        ).all()
    )
    return OverviewResponse(
        execution_mode=settings.EXECUTION_MODE,
        provider_mode=settings.MODEL_PROVIDER_MODE,
        live_job_search_enabled=settings.ALLOW_LIVE_JOB_SEARCH,
        location_configured=session.get(PrivateLocation, 1) is not None,
        landmark_count=int(
            session.exec(select(func.count("*")).select_from(ExternalLandmark)).one()
        ),
        job_count=len(session.exec(select(JobPosting.id)).all()),
        fact_count=len(session.exec(select(ProfileFact.id)).all()),
        resume_version=int(resume_version) if resume_version is not None else None,
        work_entry_count=len(session.exec(select(WorkEntry.id)).all()),
        report_count=len(session.exec(select(WorkReport.id)).all()),
        pending_approvals=int(
            session.exec(
                select(func.count("*"))
                .select_from(ApprovalRequest)
                .where(ApprovalRequest.status == "pending")
            ).one()
        ),
        recent_runs=[AgentRunPublic.model_validate(item) for item in recent_runs],
    )


@router.get("/location", response_model=LocationStatus, tags=["settings"])
def get_location(session: Session = SessionDep) -> LocationStatus:
    location = session.get(PrivateLocation, 1)
    if location is None:
        return LocationStatus(configured=False)
    return LocationStatus(
        configured=True,
        masked_address="••••••（仅保存在本机）",
        is_demo=location.is_demo,
        updated_at=location.updated_at,
    )


@router.put("/location", response_model=LocationStatus, tags=["settings"])
def put_location(
    payload: LocationInput, session: Session = SessionDep
) -> LocationStatus:
    location = session.get(PrivateLocation, 1)
    if location is None:
        location = PrivateLocation(**payload.model_dump())
    else:
        for key, value in payload.model_dump().items():
            setattr(location, key, value)
        location.updated_at = datetime.now(UTC)
    session.add(location)
    session.commit()
    session.refresh(location)
    return LocationStatus(
        configured=True,
        masked_address="••••••（仅保存在本机）",
        is_demo=location.is_demo,
        updated_at=location.updated_at,
    )


@router.get("/landmarks", response_model=list[LandmarkPublic], tags=["settings"])
def list_landmarks(session: Session = SessionDep) -> list[ExternalLandmark]:
    return list(
        session.exec(
            select(ExternalLandmark).order_by(
                col(ExternalLandmark.rotation_order), col(ExternalLandmark.name)
            )
        ).all()
    )


@router.post(
    "/landmarks",
    response_model=LandmarkPublic,
    status_code=status.HTTP_201_CREATED,
    tags=["settings"],
)
def create_landmark(
    payload: LandmarkInput, session: Session = SessionDep
) -> ExternalLandmark:
    landmark = ExternalLandmark(**payload.model_dump())
    session.add(landmark)
    session.commit()
    session.refresh(landmark)
    return landmark


@router.put(
    "/landmarks/{landmark_id}", response_model=LandmarkPublic, tags=["settings"]
)
def update_landmark(
    landmark_id: uuid.UUID,
    payload: LandmarkInput,
    session: Session = SessionDep,
) -> ExternalLandmark:
    landmark = _get_or_404(session, ExternalLandmark, landmark_id)
    for key, value in payload.model_dump().items():
        setattr(landmark, key, value)
    session.add(landmark)
    session.commit()
    session.refresh(landmark)
    return landmark


@router.delete("/landmarks/{landmark_id}", status_code=204, tags=["settings"])
def delete_landmark(landmark_id: uuid.UUID, session: Session = SessionDep) -> None:
    landmark = _get_or_404(session, ExternalLandmark, landmark_id)
    session.delete(landmark)
    session.commit()


@router.get("/jobs", response_model=list[JobPublic], tags=["jobs"])
def list_jobs(
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = SessionDep,
) -> list[JobPosting]:
    return list(
        session.exec(
            select(JobPosting)
            .order_by(col(JobPosting.distance_km), col(JobPosting.observed_at).desc())
            .limit(limit)
        ).all()
    )


@router.post("/job-runs", response_model=AgentRunPublic, tags=["jobs", "agents"])
def create_job_run(payload: JobRunRequest) -> AgentRun:
    return run_job_discovery(query=payload.query, live=payload.live)


def _store_artifact(payload: ImportTextRequest, session: Session) -> ImportArtifact:
    content = payload.content.strip()
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    artifact = ImportArtifact(
        source_type=payload.source_type,
        source_label=payload.source_label,
        content_sha256=digest,
        content=content,
    )
    session.add(artifact)
    session.commit()
    session.refresh(artifact)
    return artifact


@router.get("/imports", response_model=list[ImportPublic], tags=["profile"])
def list_imports(session: Session = SessionDep) -> list[ImportArtifact]:
    return list(
        session.exec(
            select(ImportArtifact).order_by(col(ImportArtifact.created_at).desc())
        ).all()
    )


@router.post(
    "/imports/text",
    response_model=ImportPublic,
    status_code=status.HTTP_201_CREATED,
    tags=["profile"],
)
def create_text_import(
    payload: ImportTextRequest, session: Session = SessionDep
) -> ImportArtifact:
    return _store_artifact(payload, session)


@router.post(
    "/imports/file",
    response_model=ImportPublic,
    status_code=status.HTTP_201_CREATED,
    tags=["profile"],
)
async def create_file_import(
    file: UploadFile = File(...), session: Session = SessionDep
) -> ImportArtifact:
    content = await file.read(settings.MAX_UPLOAD_BYTES + 1)
    if len(content) > settings.MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413, detail="File is larger than the configured limit"
        )
    if not file.filename:
        raise HTTPException(status_code=422, detail="A filename is required")
    try:
        converted = convert_uploaded_bytes(file.filename, content)
    except RuntimeError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return _store_artifact(
        ImportTextRequest(
            source_type="file", source_label=file.filename, content=converted
        ),
        session,
    )


@router.post(
    "/imports/{artifact_id}/process",
    response_model=AgentRunPublic,
    tags=["profile", "agents"],
)
def process_import(artifact_id: uuid.UUID) -> AgentRun:
    return run_profile_import(artifact_id)


@router.get("/profile-facts", response_model=list[ProfileFactPublic], tags=["profile"])
def list_profile_facts(session: Session = SessionDep) -> list[ProfileFact]:
    return list(
        session.exec(
            select(ProfileFact).order_by(col(ProfileFact.created_at).desc())
        ).all()
    )


@router.patch(
    "/profile-facts/{fact_id}", response_model=ProfileFactPublic, tags=["profile"]
)
def set_fact_status(
    fact_id: uuid.UUID,
    payload: FactStatusInput,
    session: Session = SessionDep,
) -> ProfileFact:
    fact = _get_or_404(session, ProfileFact, fact_id)
    fact.status = payload.status
    session.add(fact)
    session.commit()
    session.refresh(fact)
    return fact


@router.get("/resume-drafts", response_model=list[ResumeDraftPublic], tags=["profile"])
def list_resume_drafts(session: Session = SessionDep) -> list[ResumeDraft]:
    return list(
        session.exec(
            select(ResumeDraft).order_by(col(ResumeDraft.version).desc())
        ).all()
    )


@router.get("/work-entries", response_model=list[WorkEntryPublic], tags=["work"])
def list_work_entries(session: Session = SessionDep) -> list[WorkEntry]:
    return list(
        session.exec(
            select(WorkEntry).order_by(
                col(WorkEntry.work_date).desc(), col(WorkEntry.created_at).desc()
            )
        ).all()
    )


@router.post(
    "/work-entries",
    response_model=WorkEntryPublic,
    status_code=status.HTTP_201_CREATED,
    tags=["work"],
)
def create_work_entry(
    payload: WorkEntryInput, session: Session = SessionDep
) -> WorkEntry:
    entry = WorkEntry(**payload.model_dump())
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry


@router.put("/work-entries/{entry_id}", response_model=WorkEntryPublic, tags=["work"])
def update_work_entry(
    entry_id: uuid.UUID,
    payload: WorkEntryInput,
    session: Session = SessionDep,
) -> WorkEntry:
    entry = _get_or_404(session, WorkEntry, entry_id)
    for key, value in payload.model_dump().items():
        setattr(entry, key, value)
    entry.updated_at = datetime.now(UTC)
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry


@router.delete("/work-entries/{entry_id}", status_code=204, tags=["work"])
def delete_work_entry(entry_id: uuid.UUID, session: Session = SessionDep) -> None:
    entry = _get_or_404(session, WorkEntry, entry_id)
    session.delete(entry)
    session.commit()


@router.get("/reports", response_model=list[WorkReportPublic], tags=["work"])
def list_reports(session: Session = SessionDep) -> list[WorkReport]:
    return list(
        session.exec(
            select(WorkReport).order_by(col(WorkReport.created_at).desc())
        ).all()
    )


@router.post("/reports", response_model=AgentRunPublic, tags=["work", "agents"])
def create_report(payload: ReportRequest) -> AgentRun:
    return run_work_report(
        report_type=payload.report_type,
        period_start=payload.period_start,
        period_end=payload.period_end,
    )


@router.get("/agent-runs", response_model=list[AgentRunPublic], tags=["agents"])
def list_agent_runs(
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = SessionDep,
) -> list[AgentRun]:
    return list(
        session.exec(
            select(AgentRun).order_by(col(AgentRun.started_at).desc()).limit(limit)
        ).all()
    )


@router.post(
    "/agent-runs/{run_id}/retry",
    response_model=AgentRunPublic,
    tags=["agents"],
)
def retry_run(run_id: uuid.UUID) -> AgentRun:
    try:
        return retry_agent_run(run_id)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.get("/approvals", response_model=list[ApprovalPublic], tags=["approvals"])
def list_approvals(session: Session = SessionDep) -> list[ApprovalRequest]:
    return list(
        session.exec(
            select(ApprovalRequest).order_by(col(ApprovalRequest.created_at).desc())
        ).all()
    )


@router.post(
    "/approvals/{approval_id}/decision",
    response_model=ApprovalPublic,
    tags=["approvals"],
)
def decide_approval(
    approval_id: uuid.UUID,
    payload: ApprovalDecision,
    session: Session = SessionDep,
) -> ApprovalRequest:
    approval = _get_or_404(session, ApprovalRequest, approval_id)
    if approval.status != "pending":
        raise HTTPException(status_code=409, detail="Approval was already decided")
    approval.status = payload.decision
    approval.decided_at = datetime.now(UTC)
    session.add(approval)
    session.commit()
    session.refresh(approval)
    return approval


@router.get("/schedule", response_model=SchedulePublic, tags=["settings"])
def get_schedule(session: Session = SessionDep) -> ScheduleConfig:
    schedule = session.get(ScheduleConfig, 1)
    if schedule is None:
        schedule = ScheduleConfig(interval_minutes=settings.JOB_SCHEDULE_MINUTES)
        session.add(schedule)
        session.commit()
        session.refresh(schedule)
    return schedule


@router.put("/schedule", response_model=SchedulePublic, tags=["settings"])
def put_schedule(
    payload: ScheduleInput, session: Session = SessionDep
) -> ScheduleConfig:
    schedule = session.get(ScheduleConfig, 1) or ScheduleConfig()
    schedule.job_discovery_enabled = payload.job_discovery_enabled
    schedule.interval_minutes = payload.interval_minutes
    schedule.updated_at = datetime.now(UTC)
    session.add(schedule)
    session.commit()
    session.refresh(schedule)
    return schedule


@router.post("/schedule/run-once", tags=["settings", "agents"])
def trigger_schedule_once() -> dict[str, bool]:
    return {"triggered": run_schedule_tick(force=True)}
