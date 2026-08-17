from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from langgraph.checkpoint.memory import InMemorySaver

from app.core.config import settings

_memory_saver = InMemorySaver()


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

    # Keep one process-local saver so a second API call can resume the same
    # thread during tests and direct local development.
    yield _memory_saver
