import uuid
from typing import Any, NotRequired, cast

from langgraph.graph import END, START, StateGraph
from sqlmodel import Session
from typing_extensions import TypedDict

from app.core.db import engine
from app.fitness.coach.provider import CoachProvider, get_coach_provider
from app.fitness.coach.schemas import ToolPlan
from app.fitness.coach.tools import completed_session, run_tool


class FitnessCoachState(TypedDict):
    run_id: str
    session_id: str
    trigger: NotRequired[dict[str, object]]
    tool_plan: NotRequired[dict[str, object]]
    observations: NotRequired[dict[str, object]]
    recommendation: NotRequired[dict[str, object]]
    provider: NotRequired[str]
    model: NotRequired[str]


def build_fitness_coach_graph(
    *, checkpointer: Any = None, provider: CoachProvider | None = None
) -> Any:
    active_provider = provider or get_coach_provider()

    def load_trigger(state: FitnessCoachState) -> dict[str, object]:
        session_id = uuid.UUID(state["session_id"])
        with Session(engine) as db:
            summary = completed_session(db, session_id)
        sets = summary.get("sets")
        if not isinstance(sets, list):
            raise RuntimeError("Fitness Coach received an invalid session summary")
        exercise_ids: list[str] = []
        for raw_item in sets:
            if isinstance(raw_item, dict) and "exercise_id" in raw_item:
                item = cast(dict[str, object], raw_item)
                value = str(item["exercise_id"])
                if value not in exercise_ids:
                    exercise_ids.append(value)
        return {
            "trigger": {
                "event": "session_completed",
                "session_id": str(session_id),
                "workout_date": summary["workout_date"],
                "plan_name": summary["plan_name"],
                "exercise_ids": exercise_ids,
            }
        }

    def select_tools(state: FitnessCoachState) -> dict[str, object]:
        plan = active_provider.select_tools(state["trigger"])
        return {
            "tool_plan": plan.model_dump(mode="json"),
            "provider": active_provider.name,
            "model": active_provider.model,
        }

    def execute_tools(state: FitnessCoachState) -> dict[str, object]:
        plan = ToolPlan.model_validate(state["tool_plan"])
        session_id = uuid.UUID(state["session_id"])
        observations: dict[str, object] = {}
        with Session(engine) as db:
            for tool_name in dict.fromkeys(plan.tools):
                observations[tool_name] = run_tool(
                    tool_name, db, session_id, plan.focus_exercise_id
                )
        return {"observations": observations}

    def create_recommendation(state: FitnessCoachState) -> dict[str, object]:
        draft = active_provider.recommend(state["trigger"], state["observations"])
        raw_exercise_ids = state["trigger"].get("exercise_ids")
        if not isinstance(raw_exercise_ids, list):
            raise RuntimeError("Fitness Coach trigger has no exercise ids")
        trigger_ids = {uuid.UUID(str(value)) for value in raw_exercise_ids}
        if (
            draft.target_exercise_id is not None
            and draft.target_exercise_id not in trigger_ids
        ):
            raise RuntimeError("Fitness Coach recommended an exercise outside the session")
        observation_sources = set(state["observations"])
        if any(item.source not in observation_sources for item in draft.evidence):
            raise RuntimeError("Fitness Coach cited evidence from an unexecuted tool")
        return {"recommendation": draft.model_dump(mode="json")}

    graph = StateGraph(FitnessCoachState)  # ty: ignore[invalid-argument-type]
    graph.add_node("load_fitness_context", load_trigger)
    graph.add_node("agent_select_tools", select_tools)
    graph.add_node("execute_read_only_tools", execute_tools)
    graph.add_node("agent_recommend", create_recommendation)
    graph.add_edge(START, "load_fitness_context")
    graph.add_edge("load_fitness_context", "agent_select_tools")
    graph.add_edge("agent_select_tools", "execute_read_only_tools")
    graph.add_edge("execute_read_only_tools", "agent_recommend")
    graph.add_edge("agent_recommend", END)
    return graph.compile(checkpointer=checkpointer)
