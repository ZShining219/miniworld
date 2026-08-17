import os
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel

TEST_DB = Path("/tmp/miniworld-agent-pytest.db")
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"
os.environ["FASTAPI_ENV"] = "test"
os.environ["EXECUTION_MODE"] = "demo"
os.environ["MODEL_PROVIDER_MODE"] = "demo"
os.environ["LANGGRAPH_CHECKPOINT_MODE"] = "memory"
os.environ["SEED_DEMO_DATA"] = "true"
os.environ["SCHEDULER_ENABLED"] = "false"

from app.core.db import engine, seed_demo_data  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def reset_database() -> Generator[None]:
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    seed_demo_data()
    yield


@pytest.fixture
def client() -> Generator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client
