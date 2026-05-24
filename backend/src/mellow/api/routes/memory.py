"""记忆路由。"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from mellow.api.deps import get_container, get_db_session, get_current_user
from mellow.di import Container
from mellow.providers.auth import UserInfo

router = APIRouter(prefix="/api/v1/memory", tags=["memory"])


@router.get("/emotions")
async def get_emotions(
    persona_id: str = Query(...),
    user: UserInfo = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """获取角色记忆中的情绪轨迹。"""
    from mellow.db.repos.persona_memory_repo import SqlAlchemyPersonaMemoryRepository
    from mellow.memory.persona_memory import PersonaMemoryManager
    repo = SqlAlchemyPersonaMemoryRepository(session)
    mm = PersonaMemoryManager(repo)
    memory = await mm.get_or_create(persona_id, user.id)
    return {
        "emotions": [m.model_dump() for m in memory.emotional_trajectory[-10:]],
    }


@router.get("/facts")
async def get_facts(
    persona_id: str = Query(...),
    user: UserInfo = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """获取角色对用户的关键认知。"""
    from mellow.db.repos.persona_memory_repo import SqlAlchemyPersonaMemoryRepository
    from mellow.memory.persona_memory import PersonaMemoryManager
    repo = SqlAlchemyPersonaMemoryRepository(session)
    mm = PersonaMemoryManager(repo)
    memory = await mm.get_or_create(persona_id, user.id)
    return {"facts": memory.key_facts}


@router.get("/summary")
async def get_summary(
    persona_id: str = Query(...),
    user: UserInfo = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """获取角色记忆摘要。"""
    from mellow.db.repos.persona_memory_repo import SqlAlchemyPersonaMemoryRepository
    from mellow.memory.persona_memory import PersonaMemoryManager
    repo = SqlAlchemyPersonaMemoryRepository(session)
    mm = PersonaMemoryManager(repo)
    context = await mm.get_memory_context(persona_id, user.id)
    return {"summary": context}


@router.get("/proactive")
async def get_proactive_messages(
    persona_id: str = Query(...),
    user: UserInfo = Depends(get_current_user),
    container: Container = Depends(get_container),
):
    """获取角色的主动联系消息并标记已读。

    返回待投递的主动消息列表，获取后自动标记为已投递。
    """
    messenger = await container.proactive_messenger()
    messages = messenger.get_pending(user.id, persona_id)
    return {
        "messages": [m.model_dump() for m in messages],
        "count": len(messages),
    }
