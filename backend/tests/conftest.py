"""pytest 固件 —— 共享的测试依赖。"""

import pytest

from mellow.config import Settings


@pytest.fixture
def settings():
    """测试环境配置。"""
    return Settings(
        jwt_secret="test-secret",
        jwt_expire_minutes=60,
        llm_api_key="test-key",
        embed_api_key="test-key",
        database_url="sqlite+aiosqlite:///./data/test.db",
        lancedb_path="./data/test_lancedb",
    )
