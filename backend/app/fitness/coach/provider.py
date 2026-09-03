import json
from typing import Protocol

from openai import OpenAI

from app.core.config import settings
from app.fitness.coach.schemas import RecommendationDraft, ToolPlan


class CoachProvider(Protocol):
    name: str
    model: str

    def select_tools(self, trigger: dict[str, object]) -> ToolPlan: ...

    def recommend(
        self, trigger: dict[str, object], observations: dict[str, object]
    ) -> RecommendationDraft: ...


class DeepSeekCoachProvider:
    name = "deepseek"

    def __init__(self) -> None:
        if not settings.FITNESS_AGENT_API_KEY:
            raise RuntimeError("FITNESS_AGENT_API_KEY is not configured")
        self.model = settings.FITNESS_AGENT_MODEL
        base_url = settings.FITNESS_AGENT_BASE_URL.rstrip("/")
        if not base_url.endswith("/v1"):
            base_url += "/v1"
        self.client = OpenAI(
            api_key=settings.FITNESS_AGENT_API_KEY,
            base_url=base_url,
            timeout=settings.FITNESS_AGENT_TIMEOUT_SECONDS,
        )

    def _json(self, system: str, payload: dict[str, object]) -> dict[str, object]:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("Fitness Coach model returned an empty response")
        value = json.loads(content)
        if not isinstance(value, dict):
            raise RuntimeError("Fitness Coach model did not return a JSON object")
        return value

    def select_tools(self, trigger: dict[str, object]) -> ToolPlan:
        value = self._json(
            """You are the planning stage of a non-conversational fitness coach agent.
Select the minimum useful tools for a post-workout recommendation. Available tools:
completed_session and exercise_history. Return JSON with tools, focusExerciseId,
and rationale. Never invent an exercise id; use null when uncertain.""",
            {
                "trigger": trigger,
                "output_schema": ToolPlan.model_json_schema(by_alias=True),
            },
        )
        return ToolPlan.model_validate(value)

    def recommend(
        self, trigger: dict[str, object], observations: dict[str, object]
    ) -> RecommendationDraft:
        value = self._json(
            """You are a conservative strength-training coach agent for one user.
Using only the supplied tool observations, produce exactly one actionable recommendation.
Allowed recommendationType values: increase_weight, decrease_weight, increase_reps,
hold, observe. Include concrete evidence copied from observations, a confidence from
0 to 1, and reviewAfter. Do not diagnose injury, invent exertion/recovery data, or
change any plan. When evidence is insufficient choose observe. Return JSON only.""",
            {
                "trigger": trigger,
                "observations": observations,
                "output_schema": RecommendationDraft.model_json_schema(by_alias=True),
            },
        )
        return RecommendationDraft.model_validate(value)


def get_coach_provider() -> CoachProvider:
    if settings.FITNESS_AGENT_PROVIDER == "deepseek":
        return DeepSeekCoachProvider()
    if settings.FITNESS_AGENT_PROVIDER == "disabled":
        raise RuntimeError("Fitness Coach provider is disabled")
    raise RuntimeError("Fitness Coach demo provider is test-only and was not injected")
