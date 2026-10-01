"""Role/level vocabulary shared with the local interview practice project.

The interview service validates imported materials against its own catalog
(`config/roles.json` inside that project). Keeping the same identifier list here
lets MiniWorld propose a role/level per job without calling the other app, and
the handoff endpoint still lets the user override before anything is written.
"""

INTERVIEW_ROLES: dict[str, tuple[str, ...]] = {
    "python_backend": ("intern", "junior", "mid", "senior", "lead"),
    "llm_app": ("intern", "junior", "mid", "senior", "lead"),
    "frontend": ("intern", "junior", "mid", "senior", "lead"),
    "java_backend": ("intern", "junior", "mid", "senior", "lead"),
    "go_backend": ("intern", "junior", "mid", "senior", "lead"),
    "data_engineering": ("intern", "junior", "mid", "senior", "lead"),
    "qa_automation": ("intern", "junior", "mid", "senior", "lead"),
    "platform_sre": ("intern", "junior", "mid", "senior", "lead"),
}
INTERVIEW_LEVELS = ("intern", "junior", "mid", "senior", "lead")
EXTRA_LEVELS = ("all", "unspecified")

_ROLE_KEYWORDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "llm_app",
        (
            "llm", "大模型", "agent", "rag", "machine learning", "ml engineer",
            "deep learning", "nlp", "ai engineer", "算法", "深度学习", "aigc",
        ),
    ),
    (
        "frontend",
        ("frontend", "front-end", "front end", "react", "vue", "前端", "web engineer"),
    ),
    (
        "go_backend",
        ("golang", " go ", "go engineer", "go语言"),
    ),
    (
        "java_backend",
        ("java", "spring", "jvm"),
    ),
    (
        "data_engineering",
        ("data engineer", "etl", "数据工程", "数据", "analytics", "spark", "flink"),
    ),
    (
        "qa_automation",
        ("qa", "sdet", "测试", "quality", "automation test"),
    ),
    (
        "platform_sre",
        ("sre", "devops", "运维", "site reliability", "infra", "kubernetes", "k8s"),
    ),
    (
        "python_backend",
        ("python", "django", "fastapi", "flask", "后端"),
    ),
)

_INTERN_MARKERS = ("intern", "实习", "trainee", "校招", "campus", "graduate")
_LEAD_MARKERS = ("lead", "head", "director", "负责人", "chief", "principal")
_SENIOR_MARKERS = ("senior", "staff", "资深", "高级", "专家", "5+", "5 years")
_JUNIOR_MARKERS = ("junior", "初级", "entry", "0-3")


def classify_job_role_level(
    title: str, job_type: str | None, summary: str | None
) -> tuple[str | None, str | None]:
    """Best-effort keyword classifier; returns None when no signal exists."""

    text = " ".join(
        part for part in (title, job_type or "", summary or "") if part
    ).lower()
    role_id = next(
        (
            role
            for role, keywords in _ROLE_KEYWORDS
            if any(keyword in text for keyword in keywords)
        ),
        None,
    )
    padded = f" {text} "
    level: str | None = None
    if any(marker in padded for marker in _INTERN_MARKERS) or (
        job_type and "intern" in job_type.lower()
    ):
        level = "intern"
    elif any(marker in padded for marker in _LEAD_MARKERS):
        level = "lead"
    elif any(marker in padded for marker in _SENIOR_MARKERS):
        level = "senior"
    elif any(marker in padded for marker in _JUNIOR_MARKERS):
        level = "junior"
    return role_id, level


def role_is_valid(role_id: str) -> bool:
    return role_id in INTERVIEW_ROLES


def level_is_valid(role_id: str, level: str) -> bool:
    if level in EXTRA_LEVELS:
        return True
    levels = INTERVIEW_ROLES.get(role_id)
    return levels is not None and level in levels
