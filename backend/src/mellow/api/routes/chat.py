"""对话路由 —— 聊天 + SSE 流式对话。"""

import asyncio
import json
import time

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from mellow.api.deps import get_container, get_current_user
from mellow.di import Container
from mellow.memory.session_context import SessionContextManager
from mellow.providers.auth import UserInfo

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

_session_contexts: dict[str, SessionContextManager] = {}


def _get_session_context(session_id: str, user_id: str, persona_id: str) -> SessionContextManager:
    """获取或创建会话上下文管理器。"""
    if not session_id:
        session_id = f"{user_id}:{persona_id}:{int(time.time())}"
    key = f"{session_id}:{user_id}:{persona_id}"
    if key not in _session_contexts:
        _session_contexts[key] = SessionContextManager(session_id, user_id, persona_id)
    return _session_contexts[key]


class ChatRequest(BaseModel):
    persona_id: str = Field(..., description="角色 ID")
    message: str = Field(..., min_length=1)
    session_id: str = ""


class ChatResponse(BaseModel):
    reply: str
    intent: str = "chat"
    action: str | None = None


@router.post("", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    user: UserInfo = Depends(get_current_user),
    container: Container = Depends(get_container),
):
    """同步对话 —— 返回完整回复。"""
    from mellow.agent.base import AgentContext

    pm = await container.persona_manager()
    persona = pm.get_persona(req.persona_id)
    persona_name = persona.name if persona else "Mellow"

    profile_mgr = await container.profile_manager()
    profile_summary = await profile_mgr.get_profile_summary(user.id)
    memory_mgr = await container.memory_manager()
    memory_context = await memory_mgr.get_memory_context(
        persona_id=req.persona_id, user_id=user.id
    )

    context = AgentContext(
        user_id=user.id,
        persona_name=persona_name,
        session_id=req.session_id,
        system_prompt=pm.render_system_prompt(
            persona, user.username,
            profile_summary=profile_summary,
            memory_context=memory_context,
        ) if persona else "",
    )

    # Wire session context
    sctx = _get_session_context(req.session_id or user.id, user.id, req.persona_id)
    session_summary = sctx.get_summary_for_agent()
    if session_summary:
        context.extra["session_summary"] = session_summary

    agent = await container.agent()
    result = await agent.run(req.message, context)

    # Record interaction for persona memory
    await memory_mgr.record_interaction(
        persona_id=req.persona_id,
        user_id=user.id,
        summary=f"用户: {req.message[:200]}",
    )

    return ChatResponse(reply=result.content, intent=result.intent)


@router.get("/stream")
async def chat_stream(
    persona_id: str = Query(...),
    message: str = Query(..., min_length=1),
    session_id: str = Query(""),
    user: UserInfo = Depends(get_current_user),
    container: Container = Depends(get_container),
):
    """SSE 流式对话 —— 逐 token 推送。"""
    from mellow.agent.base import AgentContext

    pm = await container.persona_manager()
    persona = pm.get_persona(persona_id)
    persona_name = persona.name if persona else "Mellow"

    profile_mgr = await container.profile_manager()
    profile_summary = await profile_mgr.get_profile_summary(user.id)
    memory_mgr = await container.memory_manager()
    memory_context = await memory_mgr.get_memory_context(
        persona_id=persona_id, user_id=user.id
    )

    context = AgentContext(
        user_id=user.id,
        persona_name=persona_name,
        session_id=session_id,
        system_prompt=pm.render_system_prompt(
            persona, user.username,
            profile_summary=profile_summary,
            memory_context=memory_context,
        ) if persona else "",
    )

    # Wire session context
    sctx = _get_session_context(session_id or user.id, user.id, persona_id)
    session_summary = sctx.get_summary_for_agent()
    if session_summary:
        context.extra["session_summary"] = session_summary

    agent = await container.agent()

    async def event_stream():
        try:
            async for token in agent.run_stream(message, context):
                yield f"data: {json.dumps({'token': token})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        except asyncio.CancelledError:
            # Client disconnected — stream will be cancelled
            pass

    # Record interaction asynchronously (don't block the stream)
    asyncio.create_task(
        memory_mgr.record_interaction(
            persona_id=persona_id,
            user_id=user.id,
            summary=f"用户: {message[:200]}",
        )
    )

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
