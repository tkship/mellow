"""角色管理路由。"""

from fastapi import APIRouter, Depends

from mellow.api.deps import get_container, get_current_user
from mellow.di import Container
from mellow.models import Persona
from mellow.providers.auth import UserInfo

router = APIRouter(prefix="/api/v1/personas", tags=["personas"])


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
        return {"error": "角色不存在"}, 404
    return persona.model_dump()
