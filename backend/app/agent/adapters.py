import hashlib
import html
import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol

import httpx

from app.core.config import settings


@dataclass(frozen=True)
class RawJob:
    source: str
    external_id: str | None
    title: str
    company: str
    location_text: str
    url: str
    latitude: float | None = None
    longitude: float | None = None
    job_type: str | None = None
    summary: str | None = None
    salary_text: str | None = None
    published_at: datetime | None = None

    def fingerprint(self) -> str:
        source = self.source.lower().strip()
        if self.external_id and self.external_id.strip():
            canonical = f"source-id|{source}|{self.external_id.lower().strip()}"
        elif self.url.strip():
            canonical = f"url|{self.url.split('?')[0].lower().strip()}"
        else:
            canonical = "|".join(
                (
                    "composite",
                    source,
                    self.title.lower().strip(),
                    self.company.lower().strip(),
                    self.location_text.lower().strip(),
                    self.published_at.date().isoformat() if self.published_at else "",
                )
            )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class JobSourceAdapter(Protocol):
    name: str

    def search(self, query: str, landmark_query: str) -> list[RawJob]: ...


class DemoJobAdapter:
    name = "demo"

    def search(self, query: str, landmark_query: str) -> list[RawJob]:
        del query
        return [
            RawJob(
                source="demo",
                external_id="demo-frontend-intern",
                title="前端开发实习生",
                company="星轨工作室",
                location_text=f"{landmark_query} · 创新园区",
                latitude=31.2243,
                longitude=121.4768,
                url="https://example.com/jobs/frontend-intern",
                job_type="internship",
                salary_text="CNY 300–400/天",
                summary="参与 React 数据看板与设计系统建设。",
                published_at=datetime.now(UTC),
            ),
            RawJob(
                source="demo",
                external_id="demo-agent-engineer",
                title="Agent 应用工程师",
                company="远望智能",
                location_text=f"{landmark_query} · 数字大厦",
                latitude=31.2351,
                longitude=121.4552,
                url="https://example.com/jobs/agent-engineer",
                job_type="fulltime",
                summary="使用 Python、LangGraph 与检索系统构建智能工作流。",
                published_at=datetime.now(UTC),
            ),
            RawJob(
                source="demo",
                external_id="demo-product-intern",
                title="AI 产品实习生",
                company="纸飞机科技",
                location_text=f"{landmark_query} · 联合办公空间",
                latitude=31.2176,
                longitude=121.4381,
                url="https://example.com/jobs/ai-product-intern",
                job_type="internship",
                summary="负责用户研究、Agent 场景拆解和数据复盘。",
                published_at=datetime.now(UTC),
            ),
        ]


class LeverJobAdapter:
    """Read public company Job Boards through Lever's documented GET endpoint."""

    name = "lever"
    _site_pattern = re.compile(r"^[a-zA-Z0-9_-]+$")

    def search(self, query: str, landmark_query: str) -> list[RawJob]:
        del query  # Lever's public endpoint filters by board/location, not free text.
        if not settings.ALLOW_LIVE_JOB_SEARCH:
            raise RuntimeError("Live job search is disabled by configuration")
        if not settings.lever_sites:
            raise RuntimeError("LEVER_SITES is not configured")

        jobs: list[RawJob] = []
        with httpx.Client(
            timeout=settings.LEVER_TIMEOUT_SECONDS,
            follow_redirects=True,
            headers={"User-Agent": "MiniWorld-Agent/0.1 (public job read)"},
        ) as client:
            for site in settings.lever_sites:
                if not self._site_pattern.fullmatch(site):
                    raise RuntimeError("LEVER_SITES contains an invalid site identifier")
                response = client.get(
                    f"https://api.lever.co/v0/postings/{site}",
                    params={
                        "mode": "json",
                        "limit": settings.JOB_RESULTS_LIMIT,
                        "location": landmark_query,
                    },
                )
                response.raise_for_status()
                payload = response.json()
                if not isinstance(payload, list):
                    raise RuntimeError("Lever returned an unexpected response schema")
                for record in payload:
                    if not isinstance(record, dict):
                        continue
                    categories = record.get("categories")
                    categories = categories if isinstance(categories, dict) else {}
                    created_at = record.get("createdAt")
                    published_at = (
                        datetime.fromtimestamp(float(created_at) / 1000, tz=UTC)
                        if isinstance(created_at, (int, float))
                        else None
                    )
                    jobs.append(
                        RawJob(
                            source=f"lever:{site}",
                            external_id=str(record.get("id") or "") or None,
                            title=str(record.get("text") or "未命名职位"),
                            company=site,
                            location_text=str(
                                categories.get("location") or landmark_query
                            ),
                            url=str(record.get("hostedUrl") or ""),
                            job_type=str(categories.get("commitment") or "") or None,
                            summary=str(record.get("descriptionPlain") or "")[:2000]
                            or None,
                            salary_text=_lever_salary_text(record.get("salaryRange")),
                            published_at=published_at,
                        )
                    )
        return jobs


def _lever_salary_text(value: object) -> str | None:
    if not isinstance(value, dict):
        return None
    minimum = value.get("min")
    maximum = value.get("max")
    if not isinstance(minimum, (int, float)) and not isinstance(maximum, (int, float)):
        return None
    currency = str(value.get("currency") or "").strip()
    interval = str(value.get("interval") or "").replace("-salary", "").replace("-", "")
    span = "–".join(
        str(int(v)) for v in (minimum, maximum) if isinstance(v, (int, float))
    )
    label = " ".join(part for part in (currency, span) if part)
    if not label:
        return None
    return f"{label}/{interval}" if interval else label


def _greenhouse_salary_text(record: dict[str, object]) -> str | None:
    ranges = record.get("pay_input_ranges")
    if not isinstance(ranges, list) or not ranges:
        return None
    first = ranges[0]
    if not isinstance(first, dict):
        return None
    currency_obj = first.get("currency_type")
    currency = (
        str(currency_obj.get("code") or "")
        if isinstance(currency_obj, dict)
        else ""
    )
    min_cents = first.get("min_cents")
    max_cents = first.get("max_cents")
    if not isinstance(min_cents, (int, float)) or not isinstance(max_cents, (int, float)):
        return None
    label = f"{currency} {int(min_cents / 100)}–{int(max_cents / 100)}/year".strip()
    return label or None


_TAG_PATTERN = re.compile(r"<[^>]+>")


def _strip_html(value: object) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = html.unescape(_TAG_PATTERN.sub(" ", value))
    compact = " ".join(text.split())
    return compact[:2000] or None


class GreenhouseJobAdapter:
    """Read public company boards through Greenhouse's documented GET endpoint."""

    name = "greenhouse"
    _board_pattern = re.compile(r"^[a-zA-Z0-9_-]+$")

    def search(self, query: str, landmark_query: str) -> list[RawJob]:
        del query  # The public board endpoint lists jobs; no free-text search.
        if not settings.ALLOW_LIVE_JOB_SEARCH:
            raise RuntimeError("Live job search is disabled by configuration")
        if not settings.greenhouse_boards:
            raise RuntimeError("GREENHOUSE_BOARDS is not configured")

        jobs: list[RawJob] = []
        with httpx.Client(
            timeout=settings.GREENHOUSE_TIMEOUT_SECONDS,
            follow_redirects=True,
            headers={"User-Agent": "MiniWorld-Agent/0.1 (public job read)"},
        ) as client:
            for board in settings.greenhouse_boards:
                if not self._board_pattern.fullmatch(board):
                    raise RuntimeError(
                        "GREENHOUSE_BOARDS contains an invalid board identifier"
                    )
                response = client.get(
                    f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs",
                    params={"content": "true"},
                )
                response.raise_for_status()
                payload = response.json()
                records = payload.get("jobs") if isinstance(payload, dict) else None
                if not isinstance(records, list):
                    raise RuntimeError(
                        "Greenhouse returned an unexpected response schema"
                    )
                for record in records[: settings.JOB_RESULTS_LIMIT]:
                    if not isinstance(record, dict):
                        continue
                    location = record.get("location")
                    location_text = (
                        str(location.get("name") or "")
                        if isinstance(location, dict)
                        else ""
                    )
                    updated = record.get("updated_at")
                    published_at = None
                    if isinstance(updated, str) and updated.strip():
                        try:
                            published_at = datetime.fromisoformat(
                                updated.replace("Z", "+00:00")
                            )
                        except ValueError:
                            published_at = None
                    jobs.append(
                        RawJob(
                            source=f"greenhouse:{board}",
                            external_id=str(record.get("id") or "") or None,
                            title=str(record.get("title") or "未命名职位"),
                            company=board,
                            location_text=location_text or landmark_query,
                            url=str(record.get("absolute_url") or ""),
                            job_type=None,
                            summary=_strip_html(record.get("content")),
                            salary_text=_greenhouse_salary_text(record),
                            published_at=published_at,
                        )
                    )
        return jobs


class JobSpyAdapter:
    name = "jobspy"

    def search(self, query: str, landmark_query: str) -> list[RawJob]:
        if not settings.ALLOW_LIVE_JOB_SEARCH:
            raise RuntimeError("Live job search is disabled by configuration")

        from jobspy import scrape_jobs  # type: ignore[import-untyped]

        frame = scrape_jobs(
            # python-jobspy 1.1.x supports LinkedIn, Indeed, and ZipRecruiter.
            # Keep the initial China adapter to the source with an explicit
            # country parameter instead of naming unsupported newer sources.
            site_name=["indeed"],
            search_term=query,
            location=landmark_query,
            results_wanted=settings.JOB_RESULTS_LIMIT,
            country_indeed="China",
        )
        jobs: list[RawJob] = []
        for record in frame.to_dict(orient="records"):
            location = record.get("location") or ""
            if not isinstance(location, str):
                location = ", ".join(
                    str(part)
                    for part in (
                        getattr(location, "city", None),
                        getattr(location, "state", None),
                        getattr(location, "country", None),
                    )
                    if part
                )
            jobs.append(
                RawJob(
                    source=str(record.get("site") or "jobspy"),
                    external_id=str(record.get("id") or "") or None,
                    title=str(record.get("title") or "未命名职位"),
                    company=str(record.get("company") or "未知公司"),
                    location_text=location or landmark_query,
                    url=str(record.get("job_url") or ""),
                    job_type=str(record.get("job_type") or "") or None,
                    summary=str(record.get("description") or "")[:2000] or None,
                    published_at=record.get("date_posted"),
                )
            )
        return jobs


# Provider registry: one adapter per source. New public read-only sources are
# added by implementing JobSourceAdapter and registering a factory here.
JobAdapterFactory = Callable[[], JobSourceAdapter]
JOB_ADAPTER_FACTORIES: dict[str, JobAdapterFactory] = {
    "demo": DemoJobAdapter,
    "lever": LeverJobAdapter,
    "greenhouse": GreenhouseJobAdapter,
    "jobspy": JobSpyAdapter,
}
LIVE_JOB_SOURCES = ("lever", "greenhouse", "jobspy")


def known_job_sources() -> tuple[str, ...]:
    return tuple(JOB_ADAPTER_FACTORIES)


def resolve_job_adapters(
    names: list[str] | tuple[str, ...], *, live: bool
) -> list[JobSourceAdapter]:
    """Instantiate adapters for a run while keeping demo/live separated.

    Demo mode can only use deterministic demo sources; live mode can only use
    public read-only providers. Mixing them is refused so fictional jobs can
    never be presented as live evidence.
    """

    adapters: list[JobSourceAdapter] = []
    skipped: list[str] = []
    for raw_name in names:
        name = raw_name.strip().lower()
        if not name:
            continue
        factory = JOB_ADAPTER_FACTORIES.get(name)
        if factory is None:
            raise RuntimeError(f"unknown job source: {name}")
        if live != (name in LIVE_JOB_SOURCES):
            skipped.append(name)
            continue
        adapters.append(factory())
    if not adapters:
        mode = "live" if live else "demo"
        detail = f"；已跳过与本模式不符的来源: {', '.join(skipped)}" if skipped else ""
        raise RuntimeError(f"没有可用于 {mode} 模式的岗位来源{detail}")
    return adapters


def default_job_source_names(*, live: bool) -> list[str]:
    """Resolve the effective source list for a run.

    The explicit list wins; otherwise fall back to the configured scheduled
    default, then to the legacy single-source switch for compatibility.
    """

    if live:
        return [name for name in settings.radar_fetch_sources if name != "demo"] or [
            settings.LIVE_JOB_SOURCE
        ]
    demo_sources = [
        name
        for name in settings.radar_fetch_sources
        if name in JOB_ADAPTER_FACTORIES and name not in LIVE_JOB_SOURCES
    ]
    return demo_sources or ["demo"]
