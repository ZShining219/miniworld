import pytest

from app.agent.policy import OutboundPolicy, PolicyViolation


def test_policy_blocks_exact_address_coordinates_and_secrets() -> None:
    policy = OutboundPolicy()
    with pytest.raises(PolicyViolation, match="exact_address"):
        policy.sanitize(
            "项目地点：仅测试的精确住址占位符",
            data_class="career_material",
            exact_address="仅测试的精确住址占位符",
            latitude=12.345678,
            longitude=98.765432,
        )
    with pytest.raises(PolicyViolation, match="exact_home_coordinates"):
        policy.sanitize(
            "坐标 12.345678",
            data_class="work_log",
            exact_address=None,
            latitude=12.345678,
            longitude=98.765432,
        )
    with pytest.raises(PolicyViolation, match="secret_like_value"):
        policy.sanitize(
            "api_key=sk-example-value-1234567890",
            data_class="career_material",
            exact_address=None,
            latitude=None,
            longitude=None,
        )


def test_policy_minimizes_and_hashes_allowed_text() -> None:
    payload = OutboundPolicy().sanitize(
        "  项目：MiniWorld  \n\n 技能：Python ",
        data_class="career_material",
        exact_address=None,
        latitude=None,
        longitude=None,
    )
    assert payload.text == "项目：MiniWorld\n技能：Python"
    assert len(payload.sha256) == 64
