"""记忆路由。"""

from fastapi import APIRouter, Depends, Query

from mellow.api.deps import get_container, get_current_user
from mellow.di import Container
from mellow.providers.auth import UserInfo

router = APIRouter(prefix="/api/v1/memory", tags=["memory"])


@router.get("/emotions")
async def get_emotions(
    persona_id: str = Query(...),
    user: UserInfo = Depends(get_current_user),
    container: Container = Depends(get_container),
):
    """获取角色记忆中的情绪轨迹。"""
    mm = await container.memory_manager()
    memory = await mm.get_or_create(persona_id, user.id)
    return {
        "emotions": [m.model_dump() for m in memory.emotional_trajectory[-10:]],
    }


@router.get("/facts")
async def get_facts(
    persona_id: str = Query(...),
    user: UserInfo = Depends(get_current_user),
    container: Container = Depends(get_container),
):
    """获取角色对用户的关键认知。"""
    mm = await container.memory_manager()
    memory = await mm.get_or_create(persona_id, user.id)
    return {"facts": memory.key_facts}


@router.get("/summary")
async def get_summary(
    persona_id: str = Query(...),
    user: UserInfo = Depends(get_current_user),
    container: Container = Depends(get_container),
):
    """获取角色记忆摘要。"""
    mm = await container.memory_manager()
    context = await mm.get_memory_context(persona_id, user.id)
    return {"summary": context}
