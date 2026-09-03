import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic.alias_generators import to_camel


class CoachModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
    )


ToolName = Literal["completed_session", "exercise_history"]
RecommendationType = Literal[
    "increase_weight",
    "decrease_weight",
    "increase_reps",
    "hold",
    "observe",
]


class ToolPlan(CoachModel):
    tools: list[ToolName] = Field(min_length=1, max_length=2)
    focus_exercise_id: uuid.UUID | None = None
    rationale: str = Field(min_length=1, max_length=500)


class RecommendationAction(CoachModel):
    weight: float | None = Field(default=None, ge=0, le=9999)
    reps: int | None = Field(default=None, ge=0, le=999)
    sets: int | None = Field(default=None, ge=1, le=20)


class RecommendationEvidence(CoachModel):
    source: Literal["completed_session", "exercise_history"]
    summary: str = Field(min_length=1, max_length=500)
    session_id: uuid.UUID | None = None


class RecommendationDraft(CoachModel):
    recommendation_type: RecommendationType
    target_exercise_id: uuid.UUID | None = None
    title: str = Field(min_length=1, max_length=240)
    action: RecommendationAction
    reason: str = Field(min_length=1, max_length=1200)
    evidence: list[RecommendationEvidence] = Field(min_length=1, max_length=8)
    confidence: float = Field(ge=0, le=1)
    review_after: str = Field(default="next_session", min_length=1, max_length=80)

    @model_validator(mode="after")
    def validate_action_matches_recommendation(self) -> RecommendationDraft:
        if self.recommendation_type in {"increase_weight", "decrease_weight"}:
            if self.action.weight is None:
                raise ValueError("weight recommendations require an explicit target weight")
        if self.recommendation_type == "increase_reps" and self.action.reps is None:
            raise ValueError("rep recommendations require an explicit target rep count")
        return self


class RecommendationPublic(RecommendationDraft):
    id: uuid.UUID
    run_id: uuid.UUID
    session_id: uuid.UUID
    provider: str
    model: str
    created_at: datetime


class AnalysisResult(CoachModel):
    run_id: uuid.UUID
    status: str
    recommendation: RecommendationPublic | None = None


class AnalysisRequest(CoachModel):
    session_id: uuid.UUID
