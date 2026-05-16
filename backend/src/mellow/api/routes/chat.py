"""对话路由 —— 聊天 + SSE 流式对话。"""

import json

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from mellow.api.deps import get_container, get_current_user
from mellow.di import Container
from mellow.providers.auth import UserInfo

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


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

    persona = container.persona_manager.get_persona(req.persona_id)
    persona_name = persona.name if persona else "Mellow"

    context = AgentContext(
        user_id=user.id,
        persona_name=persona_name,
        session_id=req.session_id,
        system_prompt=container.persona_manager.render_system_prompt(persona, user.username)
        if persona else "",
    )

    result = await container.agent.run(req.message, context)
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

    persona = container.persona_manager.get_persona(persona_id)
    persona_name = persona.name if persona else "Mellow"

    context = AgentContext(
        user_id=user.id,
        persona_name=persona_name,
        session_id=session_id,
        system_prompt=container.persona_manager.render_system_prompt(persona, user.username)
        if persona else "",
    )

    async def event_stream():
        async for token in container.agent.run_stream(message, context):
            yield f"data: {json.dumps({'token': token})}\n\n"
        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
