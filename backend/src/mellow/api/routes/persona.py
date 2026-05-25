"""角色管理路由。"""

import re
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from mellow.api.deps import get_container, get_current_user
from mellow.di import Container
from mellow.models import Persona
from mellow.providers.auth import UserInfo

router = APIRouter(prefix="/api/v1/personas", tags=["personas"])

# Voice demo MP3 directory — contains fixed preview files per persona
_VOICE_DEMO_DIR = Path(__file__).parent.parent.parent.parent / "data" / "voice_demos"


def _sanitize_filename(name: str) -> str:
    """Sanitize a string for use as a filename component.

    Only allows alphanumeric characters, underscores, and hyphens.
    Replaces any other character with underscore.
    Prevents path traversal by removing path separators.
    """
    # Remove any path separators and parent directory references
    name = name.replace("\\", "_").replace("/", "_")
    name = name.replace("..", "_")
    # Allow only safe characters
    name = re.sub(r'[^a-zA-Z0-9_\-]', '_', name)
    # Remove consecutive underscores
    name = re.sub(r'_+', '_', name)
    # Strip leading/trailing underscores
    name = name.strip('_')
    return name or "unknown"


@router.get("")
async def list_presets(container: Container = Depends(get_container)):
    """获取所有预设角色。"""
    pm = await container.persona_manager()
    presets = pm.list_presets()
    return {"personas": [p.model_dump() for p in presets]}


@router.get("/custom")
async def list_custom(
    user: UserInfo = Depends(get_current_user),
    container: Container = Depends(get_container),
):
    """获取当前用户的自定义角色。"""
    pm = await container.persona_manager()
    customs = pm.list_custom(user.id)
    return {"personas": [p.model_dump() for p in customs]}


@router.get("/{persona_id}")
async def get_persona(
    persona_id: str,
    container: Container = Depends(get_container),
):
    """获取指定角色详情。"""
    pm = await container.persona_manager()
    persona = pm.get_persona(persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="角色不存在")
    return persona.model_dump()


@router.get("/{persona_id}/voice")
async def get_persona_voice(
    persona_id: str,
    container: Container = Depends(get_container),
):
    """获取角色配音预览 MP3 文件。

    返回固定 MP3 样本文件。文件存放在 backend/data/voice_demos/ 目录下，
    命名规则为 {persona_id}_demo.mp3。
    """
    pm = await container.persona_manager()
    persona = pm.get_persona(persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="角色不存在")

    # Sanitize inputs to prevent path traversal
    safe_id = _sanitize_filename(persona_id)
    safe_name = _sanitize_filename(persona.name.lower())
    mp3_path = _VOICE_DEMO_DIR / f"{safe_id}_demo.mp3"
    if not mp3_path.exists():
        mp3_path = _VOICE_DEMO_DIR / f"{safe_name}_demo.mp3"

    if not mp3_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"File not found: {persona.name} voice demo",
        )

    # Ensure the resolved path is within _VOICE_DEMO_DIR
    resolved = mp3_path.resolve()
    if not str(resolved).startswith(str(_VOICE_DEMO_DIR.resolve())):
        raise HTTPException(status_code=400, detail="Invalid file path")

    return FileResponse(
        resolved,
        media_type="audio/mpeg",
        filename=f"{persona.name}_demo.mp3",
    )
