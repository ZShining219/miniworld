from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings
from app.core.db import initialize_database


def custom_generate_unique_id(route: APIRoute) -> str:
    tag = route.tags[0] if route.tags else "api"
    return f"{tag}-{route.name}"


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    initialize_database()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Local-first personal job, profile, and work agent.",
    version="0.1.0-demo",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_HOST, "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _: Request, error: RequestValidationError
) -> JSONResponse:
    # FastAPI normally echoes invalid input values. Removing them prevents an
    # invalid exact address from appearing in an API error response or log.
    sanitized_errors = []
    for item in error.errors():
        sanitized_errors.append(
            {key: value for key, value in item.items() if key not in {"input", "ctx"}}
        )
    return JSONResponse(status_code=422, content={"detail": sanitized_errors})


app.include_router(api_router, prefix=settings.API_V1_STR)

frontend_dir = Path(__file__).parent / "frontend"
if frontend_dir.exists():
    assets_dir = frontend_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def frontend(path: str) -> FileResponse:
        candidate = frontend_dir / path
        if path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(frontend_dir / "index.html")
