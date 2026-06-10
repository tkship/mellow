"""全局配置 —— 基于 pydantic-settings 的环境变量驱动配置。

优先级（高到低）：
1. 环境变量
2. data/user_keys.json（用户通过 App 设置的 API Key）
3. .env 文件
4. 代码中的默认值
"""

import json
import logging
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

# 用户可通过 App 配置的 Key 列表（其他配置项不允许用户覆盖）
USER_CONFIGURABLE_KEYS = frozenset({
    "llm_api_key",
    "llm_base_url",
    "llm_model",
    "llm_fast_model",
    "embed_api_key",
    "embed_model",
    "embed_dimension",
    "asr_app_id",
    "asr_token",
    "tts_app_id",
    "tts_token",
})

# 用户配置文件路径（与 .env 同级，在 data/ 目录下）
USER_KEYS_PATH = Path("./data/user_keys.json")


class Settings(BaseSettings):
    """应用全局配置。

    所有配置项均可通过环境变量或 .env 文件设置。
    用户可通过 App 设置 API Key，保存在 data/user_keys.json 中。
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ---- 应用 ----
    app_name: str = "mellow"
    app_version: str = "0.1.0"
    debug: bool = False

    # ---- LLM ----
    llm_provider: str = "openai"
    llm_api_key: str = ""
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o"
    llm_fast_model: str = "gpt-4o-mini"

    # ---- Embedding ----
    embed_provider: str = "dashscope"
    embed_api_key: str = ""
    embed_model: str = "text-embedding-v4"
    # 0 = auto-detect from provider (SiliconFlow: 2560, DashScope: 1024)
    embed_dimension: int = 0

    # ---- JWT ----
    jwt_secret: str = ""  # 必须通过环境变量 JWT_SECRET 配置，无默认值
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24 小时

    # ---- 数据库 ----
    database_url: str = "sqlite+aiosqlite:///./data/mellow.db"
    database_echo: bool = False
    lancedb_path: str = "./data/lancedb"

    # ---- 语音 (火山引擎) ----
    asr_provider: str = "volcano"
    asr_app_id: str = ""
    asr_token: str = ""
    tts_provider: str = "volcano"
    tts_app_id: str = ""
    tts_token: str = ""

    # ---- 主动联系 ----
    proactive_check_interval_minutes: int = 15

    @property
    def data_dir(self) -> Path:
        """数据目录的绝对路径。"""
        return Path(self.lancedb_path).parent.resolve()

    def model_post_init(self, __context) -> None:
        """启动时加载用户配置覆盖和校验关键配置。"""
        _apply_user_overrides(self)

        if not self.jwt_secret:
            import warnings
            warnings.warn(
                "JWT_SECRET 未配置！请设置环境变量 JWT_SECRET 或在 .env 中添加。"
                "使用空密钥运行极不安全，仅适合本地开发。",
                stacklevel=2,
            )
            import secrets
            self.jwt_secret = f"dev-only-{secrets.token_hex(32)}"


def _apply_user_overrides(settings: Settings) -> None:
    """从 data/user_keys.json 加载用户配置覆盖。

    只有 USER_CONFIGURABLE_KEYS 中的字段允许被覆盖。
    值为空字符串或 null 的字段不会覆盖 .env 中的值。
    """
    if not USER_KEYS_PATH.is_file():
        return

    try:
        overrides: dict = json.loads(USER_KEYS_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("读取用户配置失败: %s — 忽略覆盖", e)
        return

    applied = {}
    for key, value in overrides.items():
        if key not in USER_CONFIGURABLE_KEYS:
            continue
        if value is None or value == "":
            continue
        if hasattr(settings, key):
            # 类型转换：确保覆盖值的类型与字段定义一致
            field_type = type(getattr(settings, key))
            try:
                converted = field_type(value)
                object.__setattr__(settings, key, converted)
                applied[key] = "***" if "key" in key.lower() or "token" in key.lower() else str(converted)
            except (ValueError, TypeError):
                logger.warning("用户配置类型转换失败: %s=%s (期望 %s)", key, value, field_type)

    if applied:
        logger.info("已加载用户配置覆盖: %s", applied)


def save_user_keys(overrides: dict) -> None:
    """保存用户配置到 data/user_keys.json。

    只保存 USER_CONFIGURABLE_KEYS 中的字段。
    空字符串表示清除该配置（用 .env 中的默认值）。
    """
    # 过滤只保留允许的 key
    filtered = {k: v for k, v in overrides.items() if k in USER_CONFIGURABLE_KEYS}

    # 读取现有配置，合并
    existing: dict = {}
    if USER_KEYS_PATH.is_file():
        try:
            existing = json.loads(USER_KEYS_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass

    existing.update(filtered)

    # 确保目录存在
    USER_KEYS_PATH.parent.mkdir(parents=True, exist_ok=True)
    USER_KEYS_PATH.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("用户配置已保存到 %s", USER_KEYS_PATH)


def reload_settings() -> Settings:
    """强制重新加载配置（从环境变量 + .env + user_keys.json）。

    用于用户通过 App 修改 API Key 后，热更新运行中的配置。
    返回新的 Settings 实例。
    """
    get_settings.cache_clear()
    return get_settings()


@lru_cache
def get_settings() -> Settings:
    """获取全局配置单例。"""
    return Settings()
