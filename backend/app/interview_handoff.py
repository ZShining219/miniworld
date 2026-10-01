"""Bridge a persisted radar job into the local interview practice project.

Two delivery channels, both opt-in per call:

* ``file``    — always: a handoff package is written under
  ``runtime-data/interview-handoff/`` containing an ``ImportDocument``-shaped
  record and an ``InterviewPlanRequest`` template the user can paste into the
  interview UI.
* ``push``    — the record is submitted to the interview project's own pending
  queue. HTTP delivery uses its documented admin import endpoint after a local
  admin login; CLI delivery shells out to ``app.knowledge.cli import``. Both end
  in ``status='pending'`` — MiniWorld never approves or publishes anything.
"""

import hashlib
import json
import logging
import shutil
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

import httpx

from app.agent.interview_mapping import (
    classify_job_role_level,
    level_is_valid,
    role_is_valid,
)
from app.core.config import settings
from app.models import JobPosting

logger = logging.getLogger("miniworld.interview_handoff")

HANDOFF_SOURCE = "miniworld_radar"
DEFAULT_ROLE_ID = "llm_app"
DEFAULT_LEVEL = "unspecified"
_HANDOFF_JSON_VERSION = 1


class HandoffError(RuntimeError):
    pass


@dataclass(frozen=True)
class HandoffTarget:
    role_id: str
    level: str


def resolve_target(
    job: JobPosting, role_id: str | None, level: str | None
) -> HandoffTarget:
    resolved_role = (
        role_id
        or job.interview_role_id
        or classify_job_role_level(job.title, job.job_type, job.summary)[0]
        or DEFAULT_ROLE_ID
    )
    if not role_is_valid(resolved_role):
        raise HandoffError(f"未知面试岗位方向: {resolved_role}")
    resolved_level = (
        level
        or job.interview_level
        or classify_job_role_level(job.title, job.job_type, job.summary)[1]
        or DEFAULT_LEVEL
    )
    if not level_is_valid(resolved_role, resolved_level):
        raise HandoffError(
            f"面试级别 {resolved_level} 不适用于方向 {resolved_role}"
        )
    return HandoffTarget(role_id=resolved_role, level=resolved_level)


def _jd_text(job: JobPosting) -> str:
    header = [
        f"职位：{job.title}",
        f"公司：{job.company}",
        f"地点：{job.location_text}",
        f"类型：{job.job_type or '未标注'}",
        f"薪资：{job.salary_text or '未标注'}",
        f"来源：{job.source} · {job.url or '无链接'}",
        f"抓取时间：{job.observed_at.astimezone(UTC).isoformat()}",
    ]
    body = (job.summary or "").strip() or "（公开页面未提供 JD 正文，请在面试项目内补充。）"
    return "\n".join(header) + "\n\n" + body


def build_import_document(
    job: JobPosting, target: HandoffTarget, *, now: datetime | None = None
) -> dict[str, object]:
    """One ``ImportDocument`` record for the interview project's pending queue."""

    observed = now or job.observed_at or datetime.now(UTC)
    # SQLite returns naive datetimes even for timezone-aware columns.
    if observed.tzinfo is None:
        observed = observed.replace(tzinfo=UTC)
    content = _jd_text(job)[:30000]
    version = hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]
    return {
        "source": HANDOFF_SOURCE,
        "external_id": f"{job.source}:{job.external_id or job.fingerprint}"[:200],
        "title": f"{job.title} @ {job.company}"[:500],
        "content": content,
        "role_id": target.role_id,
        "level": target.level,
        "material_type": "jd",
        "audiences": ["interviewer"],
        "phase": "all",
        "url": job.url if job.url.startswith("http") else f"https://miniworld.local/job/{job.id}",
        "license": "公开职位页快照，由 MiniWorld 雷达导入，仅用于面试练习，待审核",
        "version": f"radar-{observed.date().isoformat()}-{version}",
        "expires_at": (observed + timedelta(days=30)).isoformat(),
    }


def build_plan_request(job: JobPosting, target: HandoffTarget) -> dict[str, object]:
    """Template for ``POST /api/interview/plan`` — the user supplies resume."""

    return {
        "role_id": target.role_id,
        "level": target.level if target.level != "unspecified" else "mid",
        "jd": {
            "role": job.title,
            "company": job.company,
            "location": job.location_text,
            "url": job.url,
            "salary": job.salary_text,
            "summary": (job.ai_summary or job.summary or "")[:1500],
            "source": HANDOFF_SOURCE,
            "fetched_at": job.observed_at.astimezone(UTC).isoformat(),
        },
        "resume": {},
    }


def _handoff_dir() -> Path:
    directory = settings.INTERVIEW_HANDOFF_DIR
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def write_handoff_package(
    job: JobPosting, document: dict[str, object], plan_request: dict[str, object]
) -> Path:
    package = {
        "format": "miniworld-interview-handoff",
        "version": _HANDOFF_JSON_VERSION,
        "generated_at": datetime.now(UTC).isoformat(),
        "knowledge_import": {
            "cli": "python -m app.knowledge.cli --db data/knowledge.db import <records.json>",
            "endpoint": "POST /api/admin/acquisition/import (admin session)",
            "records": [document],
        },
        "interview_plan_request": plan_request,
        "note": (
            "The record stays 'pending' inside the interview project until its "
            "knowledge agent or an admin reviews it. MiniWorld cannot approve it."
        ),
    }
    path = _handoff_dir() / f"job-{str(job.id)[:8]}.json"
    path.write_text(
        json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return path


def _records_file(job: JobPosting, document: dict[str, object]) -> Path:
    path = _handoff_dir() / f"job-{str(job.id)[:8]}.records.json"
    path.write_text(
        json.dumps([document], ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return path


def _read_admin_key() -> str | None:
    if not settings.INTERVIEW_AGENT_KEY_FILE:
        return None
    path = Path(settings.INTERVIEW_AGENT_KEY_FILE).expanduser()
    if not path.is_file():
        raise HandoffError(
            f"INTERVIEW_AGENT_KEY_FILE 不存在: {path}"
        )
    key = path.read_text(encoding="utf-8").strip()
    if len(key) < 24:
        raise HandoffError("面试项目管理密钥过短，拒绝使用")
    return key


def push_via_admin_api(document: dict[str, object]) -> dict[str, object]:
    key = _read_admin_key()
    if key is None:
        raise HandoffError("未配置 INTERVIEW_AGENT_KEY_FILE，无法调用管理导入接口")
    base = settings.INTERVIEW_AGENT_BASE_URL.rstrip("/")
    with httpx.Client(
        base_url=base,
        timeout=settings.INTERVIEW_AGENT_TIMEOUT_SECONDS,
        follow_redirects=True,
        headers={"X-Admin-Request": "1"},
        # Loopback traffic must never leave the machine through a system proxy.
        trust_env=False,
    ) as client:
        login = client.post("/api/admin/login", json={"key": key})
        login.raise_for_status()
        response = client.post(
            "/api/admin/acquisition/import", json={"records": [document]}
        )
        if response.status_code >= 400:
            raise HandoffError(
                f"面试项目导入接口返回 {response.status_code}: "
                f"{response.text[:200]}"
            )
        return response.json()


def push_via_cli(document: dict[str, object], job: JobPosting) -> dict[str, object]:
    if not settings.INTERVIEW_AGENT_DIR:
        raise HandoffError("未配置 INTERVIEW_AGENT_DIR，无法调用面试项目 CLI")
    root = Path(settings.INTERVIEW_AGENT_DIR).expanduser()
    if not (root / "app" / "knowledge" / "cli.py").is_file():
        raise HandoffError(f"INTERVIEW_AGENT_DIR 不是面试项目目录: {root}")
    python = root / ".venv" / "bin" / "python"
    interpreter = str(python) if python.is_file() else shutil.which("python3")
    if interpreter is None:
        raise HandoffError("找不到可用的 Python 解释器来调用面试项目 CLI")
    records = _records_file(job, document)
    completed = subprocess.run(
        [
            interpreter,
            "-m",
            "app.knowledge.cli",
            "--db",
            "data/knowledge.db",
            "--actor",
            "miniworld-radar",
            "import",
            str(records),
        ],
        cwd=str(root),
        capture_output=True,
        text=True,
        timeout=60,
    )
    if completed.returncode != 0:
        raise HandoffError(
            "面试项目 CLI 导入失败: " + (completed.stderr or completed.stdout)[:300]
        )
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {"imported": 1, "detail": completed.stdout[:200]}


def deliver_handoff(
    job: JobPosting, *, push: bool, role_id: str | None, level: str | None
) -> dict[str, object]:
    target = resolve_target(job, role_id, level)
    document = build_import_document(job, target)
    plan_request = build_plan_request(job, target)
    package_path = write_handoff_package(job, document, plan_request)

    result: dict[str, object] = {
        "job_id": str(job.id),
        "role_id": target.role_id,
        "level": target.level,
        "pushed": False,
        "push_channel": "none",
        "file": str(package_path),
        "document_external_id": document["external_id"],
        "detail": "已导出对接文件；面试项目内导入后进入待审核队列。",
    }
    if not push:
        return result

    errors: list[str] = []
    for channel, pusher in (
        ("admin_api", push_via_admin_api),
        ("cli", lambda doc: push_via_cli(doc, job)),
    ):
        try:
            response = pusher(document)
        except HandoffError as error:
            errors.append(f"{channel}: {error}")
            continue
        except (httpx.HTTPError, OSError, subprocess.TimeoutExpired) as error:
            errors.append(f"{channel}: {type(error).__name__} {str(error)[:160]}")
            continue
        result["pushed"] = True
        result["push_channel"] = channel
        result["push_response"] = response
        result["detail"] = (
            "已推送到面试项目待审核语料库（pending），仍需其审核流程。"
        )
        return result
    result["detail"] = "；".join(errors) + "。已保留本地导出文件。"
    return result
