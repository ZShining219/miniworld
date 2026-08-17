import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol

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
