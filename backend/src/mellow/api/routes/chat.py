"""对话路由 —— 聊天 + SSE 流式对话。"""

import asyncio
import json
import time

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from mellow.api.deps import get_container, get_current_user
from mellow.di import Container
from mellow.exceptions import NotFoundError
from mellow.memory.session_context import ChatMessage, SessionContextManager
from mellow.providers.auth import UserInfo

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

_session_contexts: dict[str, SessionContextManager] = {}
_MAX_SESSIONS = 50


def _get_session_context(session_id: str, user_id: str, persona_id: str) -> SessionContextManager:
    """获取或创建会话上下文管理器。"""
    if not session_id:
        session_id = f"{user_id}:{persona_id}:{int(time.time())}"
    key = f"{session_id}:{user_id}:{persona_id}"
    if key not in _session_contexts:
        # LRU: 如果超过最大会话数，移除最早的会话
        if len(_session_contexts) >= _MAX_SESSIONS:
            oldest_key = next(iter(_session_contexts))
            del _session_contexts[oldest_key]
        _session_contexts[key] = SessionContextManager(session_id, user_id, persona_id)
    return _session_contexts[key]


def _get_user_persona_context(user_id: str, persona_id: str) -> SessionContextManager | None:
    """查找用户与角色的会话上下文（不创建新会话）。"""
    for key, sctx in _session_contexts.items():
        if sctx.context.user_id == user_id and sctx.context.persona_id == persona_id:
            return sctx
    return None


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

    # Record user message
    user_msg = ChatMessage(
        id=f"msg_{user.id}_{req.persona_id}_{int(time.time() * 1000)}_user",
        role="user",
        content=req.message,
    )
    sctx.add_message(user_msg)

    agent = await container.agent()
    result = await agent.run(req.message, context)

    # Record AI reply
    ai_msg = ChatMessage(
        id=f"msg_{user.id}_{req.persona_id}_{int(time.time() * 1000)}_ai",
        role="assistant",
        content=result.content,
    )
    sctx.add_message(ai_msg)

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

    # Record user message
    user_msg = ChatMessage(
        id=f"msg_{user.id}_{persona_id}_{int(time.time() * 1000)}_user",
        role="user",
        content=message,
    )
    sctx.add_message(user_msg)

    agent = await container.agent()
    ai_reply_buffer: list[str] = []

    async def event_stream():
        try:
            async for token in agent.run_stream(message, context):
                ai_reply_buffer.append(token)
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

    # Record AI message after stream completes (via background task)
    async def _record_ai_message():
        await asyncio.sleep(0.5)  # Give stream time to finish
        ai_content = "".join(ai_reply_buffer)
        if ai_content:
            ai_msg = ChatMessage(
                id=f"msg_{user.id}_{persona_id}_{int(time.time() * 1000)}_ai",
                role="assistant",
                content=ai_content,
            )
            sctx.add_message(ai_msg)

    asyncio.create_task(_record_ai_message())

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/history")
async def get_chat_history(
    persona_id: str = Query(..., description="角色 ID"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    cursor: str | None = Query(None, description="分页游标（上一页最后一条消息 ID）"),
    user: UserInfo = Depends(get_current_user),
) -> dict:
    """分页获取聊天历史。

    按时间倒序返回（最新的在前）。
    """
    sctx = _get_user_persona_context(user.id, persona_id)
    if not sctx:
        return {"messages": [], "next_cursor": None}

    messages, next_cursor = sctx.get_messages(cursor=cursor, limit=limit)
    return {
        "messages": [m.to_dict() for m in messages],
        "next_cursor": next_cursor,
    }


@router.put("/messages/{message_id}/favorite")
async def toggle_message_favorite(
    message_id: str,
    persona_id: str = Query(..., description="角色 ID"),
    user: UserInfo = Depends(get_current_user),
) -> dict:
    """切换消息收藏状态。"""
    sctx = _get_user_persona_context(user.id, persona_id)
    if not sctx:
        raise NotFoundError("会话不存在")

    msg = sctx.toggle_favorite(message_id)
    if not msg:
        raise NotFoundError("消息不存在")

    return msg.to_dict()


@router.delete("/messages/{message_id}", status_code=204)
async def delete_message(
    message_id: str,
    persona_id: str = Query(..., description="角色 ID"),
    user: UserInfo = Depends(get_current_user),
) -> None:
    """删除消息。"""
    sctx = _get_user_persona_context(user.id, persona_id)
    if not sctx:
        raise NotFoundError("会话不存在")

    if not sctx.delete_message(message_id):
        raise NotFoundError("消息不存在")

    return None


@router.get("/phrases")
async def get_quick_phrases(
    persona_id: str,
    user: UserInfo = Depends(get_current_user),
    container: Container = Depends(get_container),
) -> dict:
    """获取角色化的动态开场白（快捷短语）。

    根据角色性格和用户画像生成 3-5 条开场白。
    """
    pm = await container.persona_manager()
    persona = pm.get_persona(persona_id)

    if not persona:
        return {"phrases": []}

    # Base phrases per persona role
    phrase_map: dict[str, list[str]] = {
        "girlfriend": [
            f"Hey sweetie~ 今天想练什么呢？💕",
            f"{persona.name}来陪你学英语啦！准备好了吗？",
            "要纠正发音吗？我一直在这里哦~",
            "聊聊你今天的心情吧，用英语告诉我！",
        ],
        "strict teacher": [
            f"Good morning, {user.username}. Let's get to work.",
            "今天的任务：完成 5 组对话练习。",
            "先复习昨天的内容，再开始新课。",
            "别偷懒，学习需要持之以恒。",
        ],
        "study buddy": [
            f"Hey {user.username}! Ready to study together? 🤝",
            "今天要学什么新词？一起探索吧！",
            "发现一个有趣的英语知识点，要看看吗？",
            "我们来做个快速测验吧，轻松又高效！",
        ],
        "humorous friend": [
            f"What's up, {user.username}! 😄",
            "英语其实没那么难，跟我一起你会觉得超有趣！",
            "我今天编了一个超搞笑的英语段子，想听吗？",
            "别紧张，犯错才好玩呢！我们一起出错一起进步~",
        ],
    }

    phrases = phrase_map.get(persona.role, [
        "Hi! 今天想学什么？",
        "准备好了吗？我们开始吧！",
    ])

    return {"phrases": phrases, "persona_name": persona.name}
