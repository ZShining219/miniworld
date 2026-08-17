from fastapi import APIRouter

from app.api.routes.miniworld import router as miniworld_router
from app.core.config import settings
from app.schemas import HealthResponse

api_router = APIRouter()


@api_router.get("/health", response_model=HealthResponse, tags=["health"])
def health() -> HealthResponse:
    database = "sqlite" if settings.DATABASE_URL.startswith("sqlite") else "postgresql"
    return HealthResponse(
        status="ok",
        project=settings.PROJECT_NAME,
        execution_mode=settings.EXECUTION_MODE,
        database=database,
        checkpoint_mode=settings.LANGGRAPH_CHECKPOINT_MODE,
    )


api_router.include_router(miniworld_router)
