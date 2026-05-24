"""火山引擎 (Volcano Engine) 语音服务实现。

ASR: 一句话识别 (HTTP API)
TTS: 语音合成 (HTTP API)

文档:
- ASR: https://www.volcengine.com/docs/6561/80816
- TTS: https://www.volcengine.com/docs/6561/97465

当 API Key 未配置时，方法会抛出 NotImplementedError 并提供友好提示。
"""

import base64
import json
import logging

import httpx

from mellow.config import Settings
from mellow.providers.asr import ASRProvider
from mellow.providers.tts import TTSProvider

logger = logging.getLogger(__name__)

# 火山引擎语音服务 API 端点
_ASR_URL = "https://openspeech.bytedance.com/api/v1/asr"
_TTS_URL = "https://openspeech.bytedance.com/api/v1/tts"


class VolcanoASRProvider(ASRProvider):
    """火山引擎语音识别。

    使用火山引擎一句话识别 HTTP API。
    需要配置 ASR_APP_ID 和 ASR_TOKEN。
    """

    def __init__(self, settings: Settings | None = None):
        self._settings = settings or Settings()
        self._app_id = self._settings.asr_app_id
        self._token = self._settings.asr_token
        self._client: httpx.AsyncClient | None = None

    def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=30.0,
                headers={
                    "Authorization": f"Bearer; {self._token}",
                    "Content-Type": "application/json",
                },
            )
        return self._client

    @property
    def provider_name(self) -> str:
        return "volcano-asr"

    async def transcribe(self, audio_bytes: bytes, lang: str = "auto") -> str:
        """语音转文字。

        Args:
            audio_bytes: 音频数据（WAV/PCM 格式）。
            lang: 语言代码，"auto" 为自动检测。

        Returns:
            识别出的文字。

        Raises:
            NotImplementedError: 当 API Key 未配置时。
        """
        if not self._app_id or not self._token:
            raise NotImplementedError(
                "火山引擎 ASR 未配置。请在 .env 中设置 ASR_APP_ID 和 ASR_TOKEN。"
            )

        client = self._ensure_client()
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

        payload = {
            "app": {
                "appid": self._app_id,
                "cluster": "volcengine_upload_common",
            },
            "user": {
                "uid": "mellow-user",
            },
            "audio": {
                "format": "wav",
                "codec": "raw",
                "rate": 16000,
                "bits": 16,
                "channel": 1,
                "data": audio_b64,
            },
            "request": {
                "reqid": "mellow-asr-request",
                "sequence": 1,
                "nbest": 1,
                "language": lang if lang != "auto" else "en",
                "show_utterances": False,
            },
        }

        try:
            response = await client.post(_ASR_URL, json=payload)
            response.raise_for_status()
            result = response.json()

            # 解析结果
            if result.get("code", -1) != 0:
                logger.warning("ASR API error: %s", result.get("message", "unknown"))
                return ""

            utterances = result.get("result", [])
            if utterances:
                return utterances[0].get("text", "")
            return ""
        except httpx.HTTPStatusError as e:
            logger.error("ASR HTTP error: %s", e)
            return ""
        except Exception as e:
            logger.error("ASR error: %s", e)
            return ""

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None


class VolcanoTTSProvider(TTSProvider):
    """火山引擎语音合成。

    使用火山引擎 TTS HTTP API。
    需要配置 TTS_APP_ID 和 TTS_TOKEN。
    """

    def __init__(self, settings: Settings | None = None):
        self._settings = settings or Settings()
        self._app_id = self._settings.tts_app_id
        self._token = self._settings.tts_token
        self._client: httpx.AsyncClient | None = None
        self._voices: list[dict[str, str]] = [
            {"id": "zh_female_qingxin", "name": "清新女声", "gender": "female"},
            {"id": "zh_male_qingse", "name": "青涩男声", "gender": "male"},
            {"id": "en_female_gentle", "name": "Gentle Female", "gender": "female"},
            {"id": "en_male_serious", "name": "Serious Male", "gender": "male"},
        ]

    def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=30.0,
                headers={
                    "Authorization": f"Bearer; {self._token}",
                    "Content-Type": "application/json",
                },
            )
        return self._client

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
        """文字转语音。

        Args:
            text: 待合成的文本。
            voice: 音色 ID。
            speed: 语速 (0.5 ~ 2.0)。

        Returns:
            音频数据 (MP3 格式)。

        Raises:
            NotImplementedError: 当 API Key 未配置时。
        """
        if not self._app_id or not self._token:
            raise NotImplementedError(
                "火山引擎 TTS 未配置。请在 .env 中设置 TTS_APP_ID 和 TTS_TOKEN。"
            )

        client = self._ensure_client()

        payload = {
            "app": {
                "appid": self._app_id,
                "cluster": "volcengine_tts_common",
            },
            "user": {
                "uid": "mellow-user",
            },
            "audio": {
                "voice_type": voice,
                "encoding": "mp3",
                "speed": speed,
                "volume": 1.0,
                "pitch": 1.0,
            },
            "request": {
                "reqid": "mellow-tts-request",
                "text": text,
                "operation": "query",
            },
        }

        try:
            response = await client.post(_TTS_URL, json=payload)
            response.raise_for_status()

            # 火山引擎 TTS 返回的是二进制音频数据
            content_type = response.headers.get("content-type", "")
            if "audio" in content_type or "octet-stream" in content_type:
                return response.content

            # 如果返回 JSON，检查错误
            try:
                result = response.json()
                logger.error("TTS API error: %s", result.get("message", "unknown"))
            except json.JSONDecodeError:
                pass
            return b""
        except httpx.HTTPStatusError as e:
            logger.error("TTS HTTP error: %s", e)
            return b""
        except Exception as e:
            logger.error("TTS error: %s", e)
            return b""

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None