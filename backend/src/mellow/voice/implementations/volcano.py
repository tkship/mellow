"""火山引擎 (Volcano Engine) 语音服务实现。

ASR: 流式语音识别 (豆包同款)
TTS: 语音合成 (多种音色)

文档:
- ASR: https://www.volcengine.com/docs/6561
- TTS: https://www.volcengine.com/docs/6569

注：此为占位实现。完整的火山引擎 ASR/TTS 需要引入官方 SDK
或实现其 WebSocket 二进制协议。Phase 8 完善。
"""

from mellow.config import Settings
from mellow.providers.asr import ASRProvider
from mellow.providers.tts import TTSProvider


class VolcanoASRProvider(ASRProvider):
    """火山引擎语音识别。

    Phase 2 提供骨架，Phase 8 实现完整 WebSocket 流式协议。
    """

    def __init__(self, settings: Settings | None = None):
        self._settings = settings or Settings()
        self._app_id = self._settings.asr_app_id
        self._token = self._settings.asr_token

    @property
    def provider_name(self) -> str:
        return "volcano-asr"

    async def transcribe(self, audio_bytes: bytes, lang: str = "auto") -> str:
        # TODO: Phase 8 实现完整的火山引擎 ASR 调用
        raise NotImplementedError(
            "火山引擎 ASR 将在 Phase 8 实现。"
            "需要引入火山引擎 SDK 并建立 WebSocket 连接。"
        )


class VolcanoTTSProvider(TTSProvider):
    """火山引擎语音合成。

    Phase 2 提供骨架，Phase 8 实现完整调用。
    """

    def __init__(self, settings: Settings | None = None):
        self._settings = settings or Settings()
        self._app_id = self._settings.tts_app_id
        self._token = self._settings.tts_token
        self._voices: list[dict[str, str]] = [
            {"id": "zh_female_qingxin", "name": "清新女声", "gender": "female"},
            {"id": "zh_male_qingse", "name": "青涩男声", "gender": "male"},
            {"id": "en_female_gentle", "name": "Gentle Female", "gender": "female"},
            {"id": "en_male_serious", "name": "Serious Male", "gender": "male"},
        ]

    @property
    def provider_name(self) -> str:
        return "volcano-tts"

    def list_voices(self) -> list[dict[str, str]]:
        return self._voices

    async def synthesize(
        self,
        text: str,
        voice: str = "zh_female_qingxin",
        speed: float = 1.0,
        **kwargs,
    ) -> bytes:
        # TODO: Phase 8 实现完整的火山引擎 TTS 调用
        raise NotImplementedError(
            "火山引擎 TTS 将在 Phase 8 实现。"
        )
