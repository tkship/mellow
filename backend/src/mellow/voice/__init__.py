"""语音接口基类 —— re-export ASR 和 TTS 协议。"""

from mellow.providers.asr import ASRProvider
from mellow.providers.tts import TTSProvider

__all__ = ["ASRProvider", "TTSProvider"]
