from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine, select

from app.core.config import settings
from app.models import ExternalLandmark, PrivateLocation, ScheduleConfig


def _engine_kwargs() -> dict[str, object]:
    if settings.DATABASE_URL.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}}
    return {"pool_pre_ping": True}


engine = create_engine(settings.DATABASE_URL, **_engine_kwargs())


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def seed_demo_data() -> None:
    if not settings.SEED_DEMO_DATA:
        return
    with Session(engine) as session:
        if session.get(PrivateLocation, 1) is None:
            session.add(
                PrivateLocation(
                    exact_address="虚构演示住址（不会外发）",
                    latitude=31.2304,
                    longitude=121.4737,
                    is_demo=True,
                )
            )
        if not session.exec(select(ExternalLandmark)).first():
            session.add_all(
                [
                    ExternalLandmark(
                        name="演示地标 A",
                        query_text="人民广场附近",
                        latitude=31.2304,
                        longitude=121.4737,
                        rotation_order=0,
                    ),
                    ExternalLandmark(
                        name="演示地标 B",
                        query_text="静安寺附近",
                        latitude=31.2231,
                        longitude=121.4455,
                        rotation_order=1,
                    ),
                ]
            )
        if session.get(ScheduleConfig, 1) is None:
            session.add(
                ScheduleConfig(
                    job_discovery_enabled=True,
                    interval_minutes=settings.JOB_SCHEDULE_MINUTES,
                )
            )
        session.commit()


def initialize_database() -> None:
    create_db_and_tables()
    seed_demo_data()


def get_session() -> Generator[Session]:
    with Session(engine) as session:
        yield session
