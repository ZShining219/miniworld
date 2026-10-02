import logging
from datetime import UTC, datetime, timedelta

from apscheduler.schedulers.blocking import (  # type: ignore[import-untyped]
    BlockingScheduler,
)
from sqlmodel import Session

from app.agent.runner import run_job_discovery
from app.core.config import settings
from app.core.db import engine, initialize_database
from app.models import ScheduleConfig

logger = logging.getLogger("miniworld.worker")


def run_schedule_tick(*, force: bool = False) -> bool:
    """Run the persisted job-radar schedule when it is due.

    The schedule row carries the source list, query text and whether live public
    reads are allowed. ``live`` runs additionally require ``EXECUTION_MODE=live``
    in the environment, so a worker can never upgrade itself to live fetching.
    Returns True when a graph run was triggered.
    """

    now = datetime.now(UTC)
    with Session(engine) as session:
        schedule = session.get(ScheduleConfig, 1)
        if schedule is None or not schedule.job_discovery_enabled:
            return False
        last_triggered = schedule.last_triggered_at
        # SQLite returns naive datetimes even for timezone-aware columns.
        if last_triggered is not None and last_triggered.tzinfo is None:
            last_triggered = last_triggered.replace(tzinfo=UTC)
        due_at = (
            last_triggered + timedelta(minutes=schedule.interval_minutes)
            if last_triggered
            else now
        )
        if not force and due_at > now:
            return False
        schedule.last_triggered_at = now
        schedule.updated_at = now
        session.add(schedule)
        session.commit()
        sources = list(schedule.sources or [])
        query = schedule.query_text or "实习 OR internship"
        live = bool(schedule.live_enabled)

    run = run_job_discovery(
        query=query,
        live=live,
        trigger="scheduler",
        sources=sources or None,
    )

    result = run.result_json or {}
    with Session(engine) as session:
        schedule = session.get(ScheduleConfig, 1)
        if schedule is not None:
            schedule.last_run_at = run.finished_at or datetime.now(UTC)
            schedule.last_run_status = run.status
            new_count = result.get("new_count")
            updated_count = result.get("updated_count")
            failed_count = result.get("failed_count")
            schedule.last_run_new = (
                int(new_count) if isinstance(new_count, (int, float)) else None
            )
            schedule.last_run_updated = (
                int(updated_count)
                if isinstance(updated_count, (int, float))
                else None
            )
            schedule.last_run_failed = (
                int(failed_count)
                if isinstance(failed_count, (int, float))
                else (1 if run.status in {"failed", "awaiting_configuration"} else 0)
            )
            schedule.last_run_message = (run.message or "")[:500] or None
            session.add(schedule)
            session.commit()
    logger.info(
        "Scheduled job discovery finished status=%s new=%s updated=%s failed=%s",
        run.status,
        result.get("new_count"),
        result.get("updated_count"),
        result.get("failed_count"),
    )
    return True


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    initialize_database()
    if not settings.SCHEDULER_ENABLED:
        logger.info("Scheduler is disabled; worker exits cleanly")
        return
    scheduler = BlockingScheduler(timezone="UTC")
    scheduler.add_job(
        run_schedule_tick,
        "interval",
        seconds=settings.SCHEDULER_POLL_SECONDS,
        id="job-discovery-schedule-poll",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    logger.info("MiniWorld worker started")
    scheduler.start()


if __name__ == "__main__":
    main()
