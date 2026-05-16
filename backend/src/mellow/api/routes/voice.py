"""语音 WebSocket 端点。

Phase 8: 双向音频流 —— Flutter 录音 → WS → ASR → Agent → TTS → WS → Flutter 播放。
"""

import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from mellow.di import Container
from mellow.providers.auth import UserInfo

router = APIRouter()


@router.websocket("/api/v1/voice/stream")
async def voice_stream(
    websocket: WebSocket,
    token: str = Query(...),
    persona_id: str = Query(...),
):
    """WebSocket 双向音频流。

    客户端发送: 二进制音频数据 (PCM/WAV)
    服务端返回:
      {"type": "text", "content": "转写文字"}  # ASR 结果
      二进制音频数据  # TTS 结果
      {"type": "done"}
    """
    # Phase 8: 基础骨架，完整 ASR/TTS 集成待实现
    await websocket.accept()

    container = Container.instance()

    try:
        # 验证 token
        try:
            auth = await container.auth()
            user = await auth.verify_token(token)
        except Exception:
            await websocket.send_json({"type": "error", "message": "认证失败"})
            await websocket.close()
            return

        pm = await container.persona_manager()
        persona = pm.get_persona(persona_id)

        while True:
            # 接收音频数据
            audio_data = await websocket.receive_bytes()

            # TODO: ASR 转文字（火山引擎 SDK）
            # text = await container.asr.transcribe(audio_data)
            text = "[Phase 8: ASR 待实现]"

            if not text.strip():
                continue

            # 发送转写结果
            await websocket.send_json({"type": "text", "content": text})

            # Agent 处理
            from mellow.agent.base import AgentContext
            context = AgentContext(
                user_id=user.id,
                persona_name=persona.name if persona else "Mellow",
                system_prompt=pm.render_system_prompt(persona, user.username)
                if persona else "",
            )
            agent = await container.agent()
            result = await agent.run(text, context)

            # TTS 合成
            # audio = await container.tts.synthesize(result.content, voice=persona.voice_id)
            # await websocket.send_bytes(audio)

            await websocket.send_json({"type": "text", "content": result.content})
            await websocket.send_json({"type": "done"})

    except WebSocketDisconnect:
        pass
