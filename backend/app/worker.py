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
    """Run the persisted job-discovery schedule when it is due.

    Returns True when a graph run was triggered. The deterministic Demo source
    remains the scheduled default; live mode is always an explicit manual choice.
    """

    now = datetime.now(UTC)
    with Session(engine) as session:
        schedule = session.get(ScheduleConfig, 1)
        if schedule is None or not schedule.job_discovery_enabled:
            return False
        due_at = (
            schedule.last_triggered_at + timedelta(minutes=schedule.interval_minutes)
            if schedule.last_triggered_at
            else now
        )
        if not force and due_at > now:
            return False
        schedule.last_triggered_at = now
        schedule.updated_at = now
        session.add(schedule)
        session.commit()

    run = run_job_discovery(
        query="实习 OR internship",
        live=False,
        trigger="scheduler",
    )
    logger.info("Scheduled job discovery finished with status=%s", run.status)
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
