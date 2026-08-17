import re
from typing import Protocol

from openai import OpenAI
from pydantic import BaseModel, Field

from app.agent.policy import SanitizedPayload
from app.core.config import settings


class ExtractedFact(BaseModel):
    fact_type: str
    value: dict[str, object]
    confidence: float = Field(ge=0, le=1)


class ProfileExtraction(BaseModel):
    facts: list[ExtractedFact]
    resume_summary: str


class ReportOutput(BaseModel):
    title: str
    summary: str
    highlights: list[str]
    next_actions: list[str]


class ModelProvider(Protocol):
    name: str
    model: str

    def extract_profile(self, payload: SanitizedPayload) -> ProfileExtraction: ...

    def generate_report(
        self, payload: SanitizedPayload, report_type: str
    ) -> ReportOutput: ...


class DemoModelProvider:
    name = "demo"
    model = "deterministic-demo"

    def extract_profile(self, payload: SanitizedPayload) -> ProfileExtraction:
        lines = [
            line.strip("-• \t") for line in payload.text.splitlines() if line.strip()
        ]
        facts: list[ExtractedFact] = []
        keyword_types = {
            "项目": "project",
            "技能": "skill",
            "负责": "experience",
            "成果": "achievement",
            "教育": "education",
        }
        for line in lines[:12]:
            fact_type = next(
                (value for key, value in keyword_types.items() if key in line),
                "note",
            )
            facts.append(
                ExtractedFact(
                    fact_type=fact_type,
                    value={"text": line},
                    confidence=0.65 if fact_type != "note" else 0.45,
                )
            )
        summary = "；".join(lines[:3]) or "尚无可提取内容"
        return ProfileExtraction(facts=facts, resume_summary=summary)

    def generate_report(
        self, payload: SanitizedPayload, report_type: str
    ) -> ReportOutput:
        lines = [
            line.strip("-• \t") for line in payload.text.splitlines() if line.strip()
        ]
        highlights = lines[:5]
        actions = [
            line for line in lines if re.search(r"待|下一步|计划|TODO", line, re.I)
        ][:3]
        return ReportOutput(
            title="日报" if report_type == "daily" else "周报",
            summary=f"共整理 {len(lines)} 条工作记录。",
            highlights=highlights or ["本周期暂无可总结记录"],
            next_actions=actions or ["继续记录下一阶段进展"],
        )


class OpenAIModelProvider:
    name = "openai"

    def __init__(self) -> None:
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is not configured")
        self.model = settings.OPENAI_MODEL
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def extract_profile(self, payload: SanitizedPayload) -> ProfileExtraction:
        response = self.client.responses.parse(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": (
                        "Extract only career facts explicitly supported by the material. "
                        "Do not infer private attributes. Keep concise evidence-grounded values."
                    ),
                },
                {"role": "user", "content": payload.text},
            ],
            text_format=ProfileExtraction,
        )
        if response.output_parsed is None:
            raise RuntimeError("Model did not return a parsed profile result")
        return response.output_parsed

    def generate_report(
        self, payload: SanitizedPayload, report_type: str
    ) -> ReportOutput:
        response = self.client.responses.parse(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": (
                        f"Create a concise Chinese {report_type} work report. "
                        "Use only supplied records and do not invent achievements."
                    ),
                },
                {"role": "user", "content": payload.text},
            ],
            text_format=ReportOutput,
        )
        if response.output_parsed is None:
            raise RuntimeError("Model did not return a parsed report")
        return response.output_parsed


def get_model_provider() -> ModelProvider:
    if settings.MODEL_PROVIDER_MODE == "openai":
        return OpenAIModelProvider()
    if settings.MODEL_PROVIDER_MODE == "disabled":
        raise RuntimeError("Remote model provider is disabled")
    return DemoModelProvider()


def report_to_markdown(output: ReportOutput) -> str:
    lines = [f"# {output.title}", "", output.summary, "", "## 重点"]
    lines.extend(f"- {item}" for item in output.highlights)
    lines.extend(("", "## 下一步"))
    lines.extend(f"- {item}" for item in output.next_actions)
    return "\n".join(lines)


def resume_content(summary: str, facts: list[ExtractedFact]) -> dict[str, object]:
    return {
        "basics": {"summary": summary},
        "projects": [fact.value for fact in facts if fact.fact_type == "project"],
        "skills": [fact.value for fact in facts if fact.fact_type == "skill"],
        "work": [fact.value for fact in facts if fact.fact_type == "experience"],
        "meta": {"fact_count": len(facts), "format": "json-resume-inspired"},
    }
