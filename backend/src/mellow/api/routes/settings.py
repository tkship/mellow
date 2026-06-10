"""用户配置管理 API — 允许通过 App 管理 API Key 等敏感配置。

配置优先级（高到低）：
  1. 环境变量（不可通过此 API 修改）
  2. data/user_keys.json（用户通过此 API 设置）
  3. .env 文件（服务端默认值）

用户只能修改 USER_CONFIGURABLE_KEYS 中列出的字段。
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from mellow.config import USER_CONFIGURABLE_KEYS, save_user_keys, get_settings

router = APIRouter(prefix="/api/v1/settings", tags=["settings"])


class ApiKeyConfig(BaseModel):
    """用户可配置的 API Key 等敏感字段。

    所有字段可选 — 未提供的字段不会修改。
    空字符串表示清除该字段（回退到 .env 默认值）。
    """

    llm_api_key: str | None = None
    llm_base_url: str | None = None
    llm_model: str | None = None
    llm_fast_model: str | None = None
    embed_api_key: str | None = None
    embed_model: str | None = None
    embed_dimension: int | None = None
    asr_app_id: str | None = None
    asr_token: str | None = None
    tts_app_id: str | None = None
    tts_token: str | None = None


class ApiKeyConfigResponse(BaseModel):
    """配置查询响应 — 敏感字段脱敏显示。"""

    llm_api_key: str = Field(description="LLM API Key（脱敏）")
    llm_base_url: str
    llm_model: str
    llm_fast_model: str
    embed_api_key: str = Field(description="Embedding API Key（脱敏）")
    embed_model: str
    embed_dimension: int
    asr_app_id: str = Field(description="ASR App ID（脱敏）")
    asr_token: str = Field(description="ASR Token（脱敏）")
    tts_app_id: str = Field(description="TTS App ID（脱敏）")
    tts_token: str = Field(description="TTS Token（脱敏）")


def _mask(value: str, visible_chars: int = 4) -> str:
    """脱敏显示：只显示前几个字符和最后几个字符。"""
    if not value:
        return ""
    if len(value) <= visible_chars * 2:
        return "***"
    return f"{value[:visible_chars]}...{value[-4:]}"


@router.get("/keys", response_model=ApiKeyConfigResponse)
async def get_api_keys():
    """获取当前 API Key 配置（脱敏显示）。"""
    settings = get_settings()
    return ApiKeyConfigResponse(
        llm_api_key=_mask(settings.llm_api_key),
        llm_base_url=settings.llm_base_url,
        llm_model=settings.llm_model,
        llm_fast_model=settings.llm_fast_model,
        embed_api_key=_mask(settings.embed_api_key),
        embed_model=settings.embed_model,
        embed_dimension=settings.embed_dimension,
        asr_app_id=_mask(settings.asr_app_id),
        asr_token=_mask(settings.asr_token),
        tts_app_id=_mask(settings.tts_app_id),
        tts_token=_mask(settings.tts_token),
    )


@router.put("/keys", response_model=ApiKeyConfigResponse)
async def update_api_keys(config: ApiKeyConfig):
    """更新 API Key 配置 — 保存到 data/user_keys.json 并热更新运行中的服务。

    只有 USER_CONFIGURABLE_KEYS 中的字段允许修改。
    提供空字符串表示清除该字段（回退到 .env 默认值）。
    """
    # 过滤掉 None 值（未提供的字段不修改）
    updates = {k: v for k, v in config.model_dump().items() if v is not None}

    # 保存到文件
    save_user_keys(updates)

    # 热更新运行中的配置
    container = __import__("mellow.di", fromlist=["Container"]).Container.instance()
    container.reload_settings()

    # 返回脱敏后的当前配置
    settings = get_settings()
    return ApiKeyConfigResponse(
        llm_api_key=_mask(settings.llm_api_key),
        llm_base_url=settings.llm_base_url,
        llm_model=settings.llm_model,
        llm_fast_model=settings.llm_fast_model,
        embed_api_key=_mask(settings.embed_api_key),
        embed_model=settings.embed_model,
        embed_dimension=settings.embed_dimension,
        asr_app_id=_mask(settings.asr_app_id),
        asr_token=_mask(settings.asr_token),
        tts_app_id=_mask(settings.tts_app_id),
        tts_token=_mask(settings.tts_token),
    )