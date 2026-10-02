import math
import uuid
from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import NotRequired

from langgraph.graph import END, START, StateGraph
from sqlmodel import Session, col, func, select
from typing_extensions import TypedDict

from app.agent.adapters import default_job_source_names, resolve_job_adapters
from app.agent.geocode import LandmarkLike, resolve_job_location
from app.agent.jobs_enrich import (
    DeepSeekJobInsightsProvider,
    DemoJobInsightsProvider,
    deterministic_job_brief,
    get_job_insights_provider,
    job_material_text,
)
from app.agent.policy import OutboundPolicy
from app.agent.providers import (
    ExtractedFact,
    get_model_provider,
    report_to_markdown,
    resume_content,
)
from app.core.config import settings
from app.core.db import engine
from app.models import (
    ExternalLandmark,
    ImportArtifact,
    JobPosting,
    ModelCallAudit,
    PrivateLocation,
    ProfileFact,
    ResumeDraft,
    WorkEntry,
    WorkReport,
)


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_km = 6371.0088
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    value = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    return radius_km * 2 * math.atan2(math.sqrt(value), math.sqrt(1 - value))


class JobState(TypedDict):
    run_id: str
    query: str
    live: bool
    sources: NotRequired[list[str]]
    landmark: NotRequired[dict[str, object]]
    landmarks: NotRequired[list[dict[str, object]]]
    home: NotRequired[dict[str, float]]
    jobs: NotRequired[list[dict[str, object]]]
    source_errors: NotRequired[list[dict[str, object]]]
    new_fingerprints: NotRequired[list[str]]
    persisted: NotRequired[int]
    new_count: NotRequired[int]
    updated_count: NotRequired[int]
    unchanged_count: NotRequired[int]
    unresolved_count: NotRequired[int]
    failed_count: NotRequired[int]
    enrichment: NotRequired[str]
    source: NotRequired[str]


class ProfileState(TypedDict):
    run_id: str
    artifact_id: str
    sanitized_text: NotRequired[str]
    payload_sha256: NotRequired[str]
    facts: NotRequired[list[dict[str, object]]]
    resume_summary: NotRequired[str]
    resume_version: NotRequired[int]
    provider: NotRequired[str]


class WorkState(TypedDict):
    run_id: str
    report_type: str
    period_start: str
    period_end: str
    entry_ids: NotRequired[list[str]]
    context: NotRequired[str]
    payload_sha256: NotRequired[str]
    report_content: NotRequired[str]
    report_id: NotRequired[str]
    provider: NotRequired[str]


@dataclass
class _LandmarkView:
    name: str
    query_text: str
    latitude: float | None
    longitude: float | None


def _as_float(value: object) -> float | None:
    return float(value) if isinstance(value, (int, float)) else None


def _select_job_context(state: JobState) -> dict[str, object]:
    del state
    with Session(engine) as session:
        home = session.get(PrivateLocation, 1)
        landmarks = list(
            session.exec(
                select(ExternalLandmark)
                .where(ExternalLandmark.enabled)
                .order_by(
                    col(ExternalLandmark.rotation_order), col(ExternalLandmark.name)
                )
            ).all()
        )
        if home is None:
            raise RuntimeError("Exact local coordinates are not configured")
        if not landmarks:
            raise RuntimeError("At least one external landmark is required")
        run_count = session.exec(select(func.count("*")).select_from(JobPosting)).one()
        landmark = landmarks[int(run_count or 0) % len(landmarks)]
        return {
            "home": {"latitude": home.latitude, "longitude": home.longitude},
            "landmark": {
                "id": str(landmark.id),
                "name": landmark.name,
                "query_text": landmark.query_text,
            },
            "landmarks": [
                {
                    "name": item.name,
                    "query_text": item.query_text,
                    "latitude": item.latitude,
                    "longitude": item.longitude,
                }
                for item in landmarks
            ],
        }


def _fetch_jobs(state: JobState) -> dict[str, object]:
    landmark = state["landmark"]
    adapters = resolve_job_adapters(
        state.get("sources") or default_job_source_names(live=state["live"]),
        live=state["live"],
    )
    jobs: list[dict[str, object]] = []
    source_errors: list[dict[str, object]] = []
    used: list[str] = []
    for adapter in adapters:
        try:
            raw_jobs = adapter.search(state["query"], str(landmark["query_text"]))
        except Exception as error:  # per-source isolation: one failure is not fatal
            source_errors.append(
                {
                    "source": adapter.name,
                    "error_type": type(error).__name__,
                    "error": str(error)[:300],
                }
            )
            continue
        used.append(adapter.name)
        for item in raw_jobs:
            jobs.append(
                {
                    "source": item.source,
                    "external_id": item.external_id,
                    "title": item.title,
                    "company": item.company,
                    "location_text": item.location_text,
                    "url": item.url,
                    "latitude": item.latitude,
                    "longitude": item.longitude,
                    "job_type": item.job_type,
                    "summary": item.summary,
                    "salary_text": item.salary_text,
                    "published_at": item.published_at.isoformat()
                    if item.published_at
                    else None,
                    "fingerprint": item.fingerprint(),
                }
            )
    if not jobs and source_errors and not used:
        first = source_errors[0]
        raise RuntimeError(
            f"所有岗位来源均失败：{first['source']} {first['error']}"
        )
    deduped: dict[str, dict[str, object]] = {}
    for job in jobs:
        deduped.setdefault(str(job["fingerprint"]), job)
    return {
        "source": "+".join(used) or "none",
        "jobs": list(deduped.values()),
        "source_errors": source_errors,
    }


def _resolve_locations(state: JobState) -> dict[str, object]:
    home = state["home"]
    landmarks: list[LandmarkLike] = [
        _LandmarkView(
            name=str(item.get("name") or ""),
            query_text=str(item.get("query_text") or ""),
            latitude=_as_float(item.get("latitude")),
            longitude=_as_float(item.get("longitude")),
        )
        for item in state.get("landmarks", [])
    ]
    enriched: list[dict[str, object]] = []
    unresolved = 0
    for job in state.get("jobs", []):
        item = dict(job)
        latitude = item.get("latitude")
        longitude = item.get("longitude")
        geocode_source = "source"
        if not (
            isinstance(latitude, (int, float))
            and isinstance(longitude, (int, float))
        ):
            resolved = resolve_job_location(str(item.get("location_text") or ""), landmarks)
            if resolved is not None:
                latitude, longitude = resolved.latitude, resolved.longitude
                geocode_source = resolved.geocode_source
        if isinstance(latitude, (int, float)) and isinstance(longitude, (int, float)):
            item["latitude"] = latitude
            item["longitude"] = longitude
            item["geocode_source"] = geocode_source
            item["distance_km"] = round(
                haversine_km(
                    float(home["latitude"]),
                    float(home["longitude"]),
                    float(latitude),
                    float(longitude),
                ),
                2,
            )
            item["distance_status"] = "calculated"
            item["distance_reason"] = None
        else:
            item["latitude"] = None
            item["longitude"] = None
            item["geocode_source"] = None
            item["distance_km"] = None
            item["distance_status"] = "location_unresolved"
            item["distance_reason"] = (
                "公开职位来源未提供可验证坐标；职位已保留，未伪造距离"
            )
            unresolved += 1
        enriched.append(item)
    return {"jobs": enriched, "unresolved_count": unresolved}


def _enrich_jobs(state: JobState) -> dict[str, object]:
    jobs = state.get("jobs", [])
    if not jobs:
        return {"enrichment": "skipped-empty"}
    try:
        provider = get_job_insights_provider()
    except RuntimeError:
        provider = DemoJobInsightsProvider()
    if provider is None:
        return {"enrichment": "disabled"}
    fingerprints = [str(job["fingerprint"]) for job in jobs]
    with Session(engine) as session:
        known = set(
            session.exec(
                select(JobPosting.fingerprint).where(
                    col(JobPosting.fingerprint).in_(fingerprints or ["__none__"])
                )
            ).all()
        )
        home = session.get(PrivateLocation, 1)

    llm_budget = settings.JOB_LLM_MAX_PER_RUN
    enriched: list[dict[str, object]] = []
    audits: list[dict[str, object]] = []
    for job in jobs:
        item = dict(job)
        if str(job["fingerprint"]) in known:
            enriched.append(item)
            continue
        baseline = deterministic_job_brief(item)
        item["ai_summary"] = baseline.brief
        item["interview_role_id"] = baseline.role_id
        item["interview_level"] = baseline.level
        if isinstance(provider, DeepSeekJobInsightsProvider) and llm_budget > 0:
            llm_budget -= 1
            try:
                material = job_material_text(item)
                payload = OutboundPolicy().sanitize(
                    material,
                    data_class="public_job_posting",
                    exact_address=home.exact_address if home else None,
                    latitude=home.latitude if home else None,
                    longitude=home.longitude if home else None,
                )
                brief = provider.summarize(payload, item)
                item["ai_summary"] = brief.brief or baseline.brief
                if brief.role_id:
                    item["interview_role_id"] = brief.role_id
                if brief.level:
                    item["interview_level"] = brief.level
                audits.append(
                    {
                        "provider": provider.name,
                        "model": provider.model,
                        "payload_sha256": payload.sha256,
                        "status": "succeeded",
                    }
                )
            except Exception as error:
                audits.append(
                    {
                        "provider": provider.name,
                        "model": provider.model,
                        "payload_sha256": "",
                        "status": f"failed_fallback:{type(error).__name__}",
                    }
                )
        enriched.append(item)

    with Session(engine) as session:
        for audit in audits:
            session.add(
                ModelCallAudit(
                    run_id=uuid.UUID(state["run_id"]),
                    provider=str(audit["provider"]),
                    model=str(audit["model"]),
                    task="job_enrichment",
                    data_class="public_job_posting",
                    payload_sha256=str(audit["payload_sha256"] or "fallback"),
                    status=str(audit["status"]),
                )
            )
        session.commit()
    return {
        "jobs": enriched,
        "enrichment": provider.name,
    }


def _persist_jobs(state: JobState) -> dict[str, object]:
    new_ids: list[str] = []
    updated = 0
    unchanged = 0
    persisted = 0
    tracked_fields = (
        "title",
        "company",
        "location_text",
        "url",
        "salary_text",
        "job_type",
        "summary",
        "latitude",
        "longitude",
        "geocode_source",
        "distance_status",
    )
    now = datetime.now(UTC)
    with Session(engine) as session:
        fingerprints = [str(job["fingerprint"]) for job in state.get("jobs", [])]
        existing_map = {
            item.fingerprint: item
            for item in session.exec(
                select(JobPosting).where(
                    col(JobPosting.fingerprint).in_(fingerprints or ["__none__"])
                )
            ).all()
        }
        for raw in state.get("jobs", []):
            published_at = (
                datetime.fromisoformat(str(raw["published_at"]))
                if raw.get("published_at")
                else None
            )
            values = {
                "source": str(raw["source"]),
                "external_id": raw.get("external_id"),
                "title": str(raw["title"]),
                "company": str(raw["company"]),
                "location_text": str(raw["location_text"]),
                "url": str(raw["url"]),
                "latitude": raw.get("latitude"),
                "longitude": raw.get("longitude"),
                "geocode_source": raw.get("geocode_source"),
                "distance_km": raw.get("distance_km"),
                "distance_status": str(raw["distance_status"]),
                "distance_reason": raw.get("distance_reason"),
                "job_type": raw.get("job_type"),
                "summary": raw.get("summary"),
                "salary_text": raw.get("salary_text"),
                "ai_summary": raw.get("ai_summary"),
                "interview_role_id": raw.get("interview_role_id"),
                "interview_level": raw.get("interview_level"),
                "fingerprint": str(raw["fingerprint"]),
                "published_at": published_at,
                "observed_at": now,
            }
            existing = existing_map.get(str(raw["fingerprint"]))
            if existing is None:
                new_ids.append(str(raw["fingerprint"]))
                session.add(
                    JobPosting.model_validate({**values, "first_seen_at": now})
                )
            else:
                changed = any(
                    getattr(existing, field) != values.get(field)
                    for field in tracked_fields
                )
                if changed:
                    updated += 1
                else:
                    unchanged += 1
                for key, value in values.items():
                    if key in {"ai_summary", "interview_role_id", "interview_level"}:
                        if value is None:
                            continue
                        setattr(existing, key, value)
                    else:
                        setattr(existing, key, value)
                session.add(existing)
            persisted += 1
        session.commit()
    return {
        "persisted": persisted,
        "new_count": len(new_ids),
        "updated_count": updated,
        "unchanged_count": unchanged,
        "new_fingerprints": new_ids[:200],
        "failed_count": len(state.get("source_errors", [])),
    }


def _sanitize_profile(state: ProfileState) -> dict[str, object]:
    with Session(engine) as session:
        artifact = session.get(ImportArtifact, uuid.UUID(state["artifact_id"]))
        if artifact is None:
            raise RuntimeError("Import artifact not found")
        home = session.get(PrivateLocation, 1)
        payload = OutboundPolicy().sanitize(
            artifact.content,
            data_class="career_material",
            exact_address=home.exact_address if home else None,
            latitude=home.latitude if home else None,
            longitude=home.longitude if home else None,
        )
    return {"sanitized_text": payload.text, "payload_sha256": payload.sha256}


def _extract_profile(state: ProfileState) -> dict[str, object]:
    provider = get_model_provider()
    payload = OutboundPolicy().sanitize(
        state["sanitized_text"],
        data_class="career_material",
        exact_address=None,
        latitude=None,
        longitude=None,
    )
    result = provider.extract_profile(payload)
    return {
        "facts": [fact.model_dump() for fact in result.facts],
        "resume_summary": result.resume_summary,
        "provider": provider.name,
    }


def _persist_profile(state: ProfileState) -> dict[str, object]:
    artifact_id = uuid.UUID(state["artifact_id"])
    facts = [ExtractedFact.model_validate(item) for item in state.get("facts", [])]
    with Session(engine) as session:
        for fact in facts:
            session.add(
                ProfileFact(
                    fact_type=fact.fact_type,
                    value_json=fact.value,
                    confidence=fact.confidence,
                    evidence_artifact_id=artifact_id,
                )
            )
        latest = session.exec(select(func.max(ResumeDraft.version))).one() or 0
        version = int(latest) + 1
        session.add(
            ResumeDraft(
                version=version,
                content_json=resume_content(state.get("resume_summary", ""), facts),
            )
        )
        session.add(
            ModelCallAudit(
                run_id=uuid.UUID(state["run_id"]),
                provider=state.get("provider", "unknown"),
                model=settings.OPENAI_MODEL
                if state.get("provider") == "openai"
                else "deterministic-demo",
                task="profile_extraction",
                data_class="career_material",
                payload_sha256=state["payload_sha256"],
                status="succeeded",
            )
        )
        artifact = session.get(ImportArtifact, artifact_id)
        if artifact:
            artifact.status = "processed"
            artifact.processed_at = datetime.now(UTC)
            session.add(artifact)
        session.commit()
    return {"resume_version": version}


def _load_work_entries(state: WorkState) -> dict[str, object]:
    start = date.fromisoformat(state["period_start"])
    end = date.fromisoformat(state["period_end"])
    if end < start:
        raise RuntimeError("period_end must not be before period_start")
    with Session(engine) as session:
        entries = list(
            session.exec(
                select(WorkEntry)
                .where(WorkEntry.work_date >= start, WorkEntry.work_date <= end)
                .order_by(col(WorkEntry.work_date), col(WorkEntry.created_at))
            ).all()
        )
    if not entries:
        raise RuntimeError("No work entries found for the selected period")
    context = "\n".join(
        f"{entry.work_date.isoformat()} | {entry.content}" for entry in entries
    )
    return {"entry_ids": [str(entry.id) for entry in entries], "context": context}


def _generate_work_report(state: WorkState) -> dict[str, object]:
    with Session(engine) as session:
        home = session.get(PrivateLocation, 1)
        payload = OutboundPolicy().sanitize(
            state["context"],
            data_class="work_log",
            exact_address=home.exact_address if home else None,
            latitude=home.latitude if home else None,
            longitude=home.longitude if home else None,
        )
    provider = get_model_provider()
    output = provider.generate_report(payload, state["report_type"])
    return {
        "payload_sha256": payload.sha256,
        "report_content": report_to_markdown(output),
        "provider": provider.name,
    }


def _persist_work_report(state: WorkState) -> dict[str, object]:
    report = WorkReport(
        report_type=state["report_type"],
        period_start=date.fromisoformat(state["period_start"]),
        period_end=date.fromisoformat(state["period_end"]),
        content=state["report_content"],
        source_entry_ids=state["entry_ids"],
        provider=state.get("provider", "unknown"),
    )
    with Session(engine) as session:
        session.add(report)
        session.add(
            ModelCallAudit(
                run_id=uuid.UUID(state["run_id"]),
                provider=state.get("provider", "unknown"),
                model=settings.OPENAI_MODEL
                if state.get("provider") == "openai"
                else "deterministic-demo",
                task="work_report",
                data_class="work_log",
                payload_sha256=state["payload_sha256"],
                status="succeeded",
            )
        )
        session.commit()
        session.refresh(report)
    return {"report_id": str(report.id)}


def build_job_graph(*, checkpointer=None):
    graph = StateGraph(JobState)  # ty: ignore[invalid-argument-type]
    graph.add_node("select_context", _select_job_context)
    graph.add_node("fetch_jobs", _fetch_jobs)
    graph.add_node("resolve_locations", _resolve_locations)
    graph.add_node("enrich_jobs", _enrich_jobs)
    graph.add_node("persist_jobs", _persist_jobs)
    graph.add_edge(START, "select_context")
    graph.add_edge("select_context", "fetch_jobs")
    graph.add_edge("fetch_jobs", "resolve_locations")
    graph.add_edge("resolve_locations", "enrich_jobs")
    graph.add_edge("enrich_jobs", "persist_jobs")
    graph.add_edge("persist_jobs", END)
    return graph.compile(checkpointer=checkpointer)


def build_profile_graph(*, checkpointer=None):
    graph = StateGraph(ProfileState)  # ty: ignore[invalid-argument-type]
    graph.add_node("apply_outbound_policy", _sanitize_profile)
    graph.add_node("extract_structured_facts", _extract_profile)
    graph.add_node("persist_profile", _persist_profile)
    graph.add_edge(START, "apply_outbound_policy")
    graph.add_edge("apply_outbound_policy", "extract_structured_facts")
    graph.add_edge("extract_structured_facts", "persist_profile")
    graph.add_edge("persist_profile", END)
    return graph.compile(checkpointer=checkpointer)


def build_work_graph(*, checkpointer=None):
    graph = StateGraph(WorkState)  # ty: ignore[invalid-argument-type]
    graph.add_node("load_work_entries", _load_work_entries)
    graph.add_node("generate_report", _generate_work_report)
    graph.add_node("persist_report", _persist_work_report)
    graph.add_edge(START, "load_work_entries")
    graph.add_edge("load_work_entries", "generate_report")
    graph.add_edge("generate_report", "persist_report")
    graph.add_edge("persist_report", END)
    return graph.compile(checkpointer=checkpointer)
