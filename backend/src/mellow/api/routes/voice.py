"""语音 WebSocket 端点。

Phase 8: 双向音频流 —— Flutter 录音 → WS → ASR → Agent → TTS → WS → Flutter 播放。
"""

import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from mellow.di import Container
from mellow.providers.auth import UserInfo

logger = logging.getLogger(__name__)

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

        # 检查 ASR/TTS 可用性
        asr_available = bool(container.settings.asr_app_id and container.settings.asr_token)
        tts_available = bool(container.settings.tts_app_id and container.settings.tts_token)

        if not asr_available and not tts_available:
            await websocket.send_json({
                "type": "error",
                "message": "语音功能开发中，请配置 ASR_APP_ID/ASR_TOKEN 和 TTS_APP_ID/TTS_TOKEN",
            })
            await websocket.close()
            return

        while True:
            # 接收音频数据
            audio_data = await websocket.receive_bytes()

            # ASR: 语音转文字
            if asr_available:
                try:
                    from mellow.voice.implementations.volcano import VolcanoASRProvider
                    asr = VolcanoASRProvider(container.settings)
                    text = await asr.transcribe(audio_data, lang="en")
                    await asr.close()
                except NotImplementedError as e:
                    text = f"[ASR 未配置: {e}]"
                except Exception as e:
                    logger.error("ASR error: %s", e)
                    text = ""
            else:
                text = "[ASR 未配置]"

            if not text.strip():
                continue

            # 发送转写结果
            await websocket.send_json({"type": "text", "content": text})

            # Agent 处理
            from mellow.agent.base import AgentContext
            context = AgentContext(
                user_id=user.id,
                persona_name=persona.name if persona else "Mellow",
                session_id=f"voice_{user.id}_{persona_id}",
                system_prompt=pm.render_system_prompt(persona, user.username)
                if persona else "",
            )
            agent = await container.agent()
            result = await agent.run(text, context)

            # TTS: 文字转语音
            if tts_available:
                try:
                    from mellow.voice.implementations.volcano import VolcanoTTSProvider
                    tts = VolcanoTTSProvider(container.settings)
                    voice_id = persona.voice_id if hasattr(persona, 'voice_id') and persona.voice_id else "zh_female_qingxin"
                    audio = await tts.synthesize(result.content, voice=voice_id)
                    await tts.close()
                    if audio:
                        await websocket.send_bytes(audio)
                except NotImplementedError:
                    # TTS 未配置，仅发送文字
                    await websocket.send_json({"type": "text", "content": result.content})
                except Exception as e:
                    logger.error("TTS error: %s", e)
                    await websocket.send_json({"type": "text", "content": result.content})
            else:
                # TTS 未配置，仅发送文字
                await websocket.send_json({"type": "text", "content": result.content})

            await websocket.send_json({"type": "done"})

    except WebSocketDisconnect:
        pass