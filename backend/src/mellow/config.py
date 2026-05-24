"""全局配置 —— 基于 pydantic-settings 的环境变量驱动配置。"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用全局配置。

    所有配置项均可通过环境变量或 .env 文件设置。
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
        """启动时校验关键配置。"""
        if not self.jwt_secret:
            import warnings
            warnings.warn(
                "JWT_SECRET 未配置！请设置环境变量 JWT_SECRET 或在 .env 中添加。"
                "使用空密钥运行极不安全，仅适合本地开发。",
                stacklevel=2,
            )
            # 开发模式允许空密钥，但设置为随机值以避免伪造
            import secrets
            self.jwt_secret = f"dev-only-{secrets.token_hex(32)}"


@lru_cache
def get_settings() -> Settings:
    """获取全局配置单例。"""
    return Settings()
