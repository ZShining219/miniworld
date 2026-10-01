"""Optional LLM enrichment for the job radar.

The default demo provider is fully deterministic and never leaves the machine.
The DeepSeek provider is an explicit opt-in channel (``JOB_AGENT_PROVIDER``)
that only receives public job-posting material which has already passed the
outbound policy gate; it produces a short brief plus an interview role/level
suggestion per *new* job.
"""

import json
from typing import Protocol

from openai import OpenAI
from pydantic import BaseModel, Field, field_validator

from app.agent.interview_mapping import (
    classify_job_role_level,
    role_is_valid,
)
from app.agent.policy import SanitizedPayload
from app.core.config import settings


class JobBrief(BaseModel):
    brief: str = Field(default="", max_length=280)
    role_id: str | None = None
    level: str | None = None

    @field_validator("role_id")
    @classmethod
    def _role_known(cls, value: str | None) -> str | None:
        if value is not None and not role_is_valid(value):
            return None
        return value


class JobInsightsProvider(Protocol):
    name: str
    model: str

    def summarize(
        self, payload: SanitizedPayload, job: dict[str, object]
    ) -> JobBrief: ...


def job_material_text(job: dict[str, object]) -> str:
    """Compose the minimized public material for enrichment."""

    return "\n".join(
        f"{label}: {value}"
        for label, value in (
            ("title", job.get("title")),
            ("company", job.get("company")),
            ("location", job.get("location_text")),
            ("job_type", job.get("job_type")),
            ("salary", job.get("salary_text")),
            ("summary", str(job.get("summary") or "")[:1200] or None),
        )
        if value
    )


class DemoJobInsightsProvider:
    name = "demo"
    model = "deterministic-demo"

    def summarize(
        self, payload: SanitizedPayload, job: dict[str, object]
    ) -> JobBrief:
        del payload
        return deterministic_job_brief(job)


def deterministic_job_brief(job: dict[str, object]) -> JobBrief:
    """Deterministic enrichment used by demo mode and as the safe fallback."""

    job_type = job.get("job_type")
    summary = job.get("summary")
    role_id, level = classify_job_role_level(
        str(job.get("title") or ""),
        job_type if isinstance(job_type, str) else None,
        summary if isinstance(summary, str) else None,
    )
    company = str(job.get("company") or "").strip()
    title = str(job.get("title") or "").strip()
    location = str(job.get("location_text") or "").strip()
    brief = " / ".join(part for part in (title, company, location) if part)
    return JobBrief(brief=brief[:280], role_id=role_id, level=level)


class DeepSeekJobInsightsProvider:
    name = "deepseek"

    def __init__(self) -> None:
        if not settings.JOB_AGENT_API_KEY:
            raise RuntimeError("JOB_AGENT_API_KEY is not configured")
        self.model = settings.JOB_AGENT_MODEL
        self.client = OpenAI(
            api_key=settings.JOB_AGENT_API_KEY,
            base_url=settings.JOB_AGENT_BASE_URL,
            timeout=settings.JOB_AGENT_TIMEOUT_SECONDS,
        )

    def summarize(
        self, payload: SanitizedPayload, job: dict[str, object]
    ) -> JobBrief:
        del job
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.2,
            max_tokens=300,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You summarize public job postings for a local job radar. "
                        "Return one JSON object with keys: brief (<=140 Chinese "
                        "characters describing the role, team and location), "
                        "role_id (one of python_backend, llm_app, frontend, "
                        "java_backend, go_backend, data_engineering, "
                        "qa_automation, platform_sre, or null), level (intern, "
                        "junior, mid, senior, lead or null). Use only the given "
                        "posting; never invent qualifications."
                    ),
                },
                {"role": "user", "content": payload.text},
            ],
        )
        content = response.choices[0].message.content if response.choices else None
        if not content:
            raise RuntimeError("Job enrichment provider returned an empty result")
        data = json.loads(content)
        if not isinstance(data, dict):
            raise RuntimeError("Job enrichment provider returned non-object JSON")
        brief = JobBrief.model_validate(data)
        if not brief.brief.strip():
            raise RuntimeError("Job enrichment provider returned an empty brief")
        return brief


def get_job_insights_provider() -> JobInsightsProvider | None:
    if settings.JOB_AGENT_PROVIDER == "disabled":
        return None
    if settings.JOB_AGENT_PROVIDER == "deepseek":
        return DeepSeekJobInsightsProvider()
    return DemoJobInsightsProvider()
