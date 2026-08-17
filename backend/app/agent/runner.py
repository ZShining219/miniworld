import uuid
from collections.abc import Callable
from datetime import UTC, date, datetime
from typing import Any

from pydantic import ValidationError
from sqlmodel import Session

from app.agent.checkpoints import checkpoint_saver
from app.agent.graphs import build_job_graph, build_profile_graph, build_work_graph
from app.agent.policy import PolicyViolation
from app.core.config import settings
from app.core.db import engine
from app.models import AgentRun, ImportArtifact

GraphBuilder = Callable[..., Any]


def _as_int(value: object, default: int = 0) -> int:
    if isinstance(value, (int, float, str)) and not isinstance(value, bool):
        try:
            return int(value)
        except ValueError:
            return default
    return default


def _as_dict(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        return {}
    return {str(key): item for key, item in value.items()}


def _item_count(value: object) -> int:
    return len(value) if isinstance(value, (list, tuple, set)) else 0


def _new_run(graph_name: str, *, execution_mode: str, trigger: str) -> AgentRun:
    run_id = uuid.uuid4()
    run = AgentRun(
        id=run_id,
        graph_name=graph_name,
        execution_mode=execution_mode,
        trigger=trigger,
        status="queued",
        checkpoint_thread_id=str(run_id),
    )
    with Session(engine) as session:
        session.add(run)
        session.commit()
        session.refresh(run)
    return run


def _set_run(
    run_id: uuid.UUID,
    *,
    status: str,
    current_node: str | None = None,
    message: str | None = None,
    result_json: dict[str, object] | None = None,
    finished: bool = False,
    reset_finished: bool = False,
    record_error: bool = False,
) -> AgentRun:
    with Session(engine) as session:
        run = session.get(AgentRun, run_id)
        if run is None:
            raise RuntimeError("Agent run disappeared")
        run.status = status
        run.current_node = current_node
        run.message = message
        run.result_json = result_json
        if reset_finished:
            run.finished_at = None
        if finished:
            run.finished_at = datetime.now(UTC)
        if record_error:
            run.error_history = [
                *run.error_history,
                {
                    "at": datetime.now(UTC).isoformat(),
                    "status": status,
                    "message": message or "运行失败",
                    "error_type": (result_json or {}).get("error_type", "unknown"),
                },
            ]
        session.add(run)
        session.commit()
        session.refresh(run)
        return run


def _error_status(error: Exception) -> str:
    if isinstance(error, PolicyViolation):
        return "blocked_by_policy"
    message = str(error).lower()
    if "not configured" in message or "disabled" in message:
        return "awaiting_configuration"
    return "failed"


def _safe_error_message(error: Exception) -> str:
    if isinstance(error, ValidationError):
        return "模型输出未通过结构化 schema 校验；正式事实和简历均未写入。"
    if isinstance(error, PolicyViolation):
        return str(error)
    message = str(error)
    if any(
        marker in message.lower()
        for marker in ("not configured", "disabled", "not found", "no work entries")
    ):
        return message[:500]
    return f"{type(error).__name__}: 运行已安全停止；可修复原因后从 checkpoint 重试。"


def _job_safe_result(value: dict[str, object]) -> dict[str, object]:
    return {
        "persisted": _as_int(value.get("persisted", 0)),
        "source": str(value.get("source", "unknown")),
        "landmark_id": str(_as_dict(value.get("landmark", {})).get("id", "")),
        "landmark_name": str(_as_dict(value.get("landmark", {})).get("name", "")),
    }


def _profile_safe_result(value: dict[str, object]) -> dict[str, object]:
    return {
        "artifact_id": str(value.get("artifact_id", "")),
        "fact_count": _item_count(value.get("facts", [])),
        "resume_version": _as_int(value.get("resume_version", 0)),
        "provider": str(value.get("provider", "unknown")),
    }


def _work_safe_result(value: dict[str, object]) -> dict[str, object]:
    return {
        "report_id": str(value.get("report_id", "")),
        "entry_count": _item_count(value.get("entry_ids", [])),
        "provider": str(value.get("provider", "unknown")),
    }


def _invoke(
    run: AgentRun,
    graph_builder: GraphBuilder,
    state: dict[str, object] | None,
    *,
    safe_result: Callable[[dict[str, object]], dict[str, object]],
) -> AgentRun:
    _set_run(
        run.id,
        status="running",
        current_node="graph_start",
        message="正在执行 LangGraph",
        reset_finished=True,
    )
    try:
        with checkpoint_saver() as checkpointer:
            graph = graph_builder(checkpointer=checkpointer)
            result = graph.invoke(
                state,
                config={"configurable": {"thread_id": run.checkpoint_thread_id}},
            )
        return _set_run(
            run.id,
            status="succeeded",
            current_node="complete",
            message="运行完成",
            result_json=safe_result(dict(result)),
            finished=True,
        )
    except Exception as error:
        return _set_run(
            run.id,
            status=_error_status(error),
            current_node="stopped",
            message=_safe_error_message(error),
            result_json={"error_type": type(error).__name__},
            finished=True,
            record_error=True,
        )


def run_job_discovery(
    *, query: str, live: bool = False, trigger: str = "manual"
) -> AgentRun:
    execution_mode = "live" if live else "demo"
    run = _new_run("job_discovery", execution_mode=execution_mode, trigger=trigger)
    if live and settings.EXECUTION_MODE != "live":
        return _set_run(
            run.id,
            status="awaiting_configuration",
            current_node="mode_gate",
            message="Live mode is not enabled. Set EXECUTION_MODE=live explicitly.",
            finished=True,
        )
    return _invoke(
        run,
        build_job_graph,
        {
            "run_id": str(run.id),
            "query": query,
            "live": live,
        },
        safe_result=_job_safe_result,
    )


def run_profile_import(artifact_id: uuid.UUID, *, trigger: str = "manual") -> AgentRun:
    mode = "live" if settings.MODEL_PROVIDER_MODE == "openai" else "demo"
    run = _new_run("profile_ingestion", execution_mode=mode, trigger=trigger)
    with Session(engine) as session:
        artifact = session.get(ImportArtifact, artifact_id)
        if artifact is None:
            return _set_run(
                run.id,
                status="failed",
                current_node="validate_artifact",
                message="Import artifact not found",
                finished=True,
            )
        if artifact.status == "processed":
            return _set_run(
                run.id,
                status="failed",
                current_node="validate_artifact",
                message="Artifact was already processed; import a new version to reprocess it.",
                finished=True,
            )
    return _invoke(
        run,
        build_profile_graph,
        {"run_id": str(run.id), "artifact_id": str(artifact_id)},
        safe_result=_profile_safe_result,
    )


def run_work_report(
    *, report_type: str, period_start: date, period_end: date, trigger: str = "manual"
) -> AgentRun:
    mode = "live" if settings.MODEL_PROVIDER_MODE == "openai" else "demo"
    run = _new_run("work_report", execution_mode=mode, trigger=trigger)
    return _invoke(
        run,
        build_work_graph,
        {
            "run_id": str(run.id),
            "report_type": report_type,
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
        },
        safe_result=_work_safe_result,
    )


def retry_agent_run(run_id: uuid.UUID) -> AgentRun:
    """Resume a failed graph task using its persisted LangGraph thread."""

    with Session(engine) as session:
        run = session.get(AgentRun, run_id)
        if run is None:
            raise LookupError("Agent run not found")
        if run.status != "failed" or run.current_node != "stopped":
            raise ValueError("Only failed Graph runs with a checkpoint can be retried")
        run.retry_count += 1
        session.add(run)
        session.commit()
        session.refresh(run)

    graph_contracts: dict[
        str, tuple[GraphBuilder, Callable[[dict[str, object]], dict[str, object]]]
    ] = {
        "job_discovery": (build_job_graph, _job_safe_result),
        "profile_ingestion": (build_profile_graph, _profile_safe_result),
        "work_report": (build_work_graph, _work_safe_result),
    }
    contract = graph_contracts.get(run.graph_name)
    if contract is None:
        raise ValueError("This Graph does not support checkpoint retry")
    graph_builder, safe_result = contract
    return _invoke(run, graph_builder, None, safe_result=safe_result)
