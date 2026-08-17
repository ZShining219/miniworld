from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from langgraph.checkpoint.memory import InMemorySaver

from app.core.config import settings


@contextmanager
def checkpoint_saver() -> Iterator[Any]:
    """Yield the configured checkpointer for one synchronous graph run.

    PostgreSQL is used by Docker Compose. Tests and direct local development can
    select memory mode without requiring a second service.
    """

    if settings.LANGGRAPH_CHECKPOINT_MODE == "postgres":
        from langgraph.checkpoint.postgres import PostgresSaver

        with PostgresSaver.from_conn_string(
            settings.checkpoint_database_url
        ) as checkpointer:
            checkpointer.setup()
            yield checkpointer
        return

    yield InMemorySaver()
