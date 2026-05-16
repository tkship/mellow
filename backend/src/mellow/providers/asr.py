"""语音识别 (ASR) 抽象接口。"""

from abc import ABC, abstractmethod


class ASRProvider(ABC):
    """语音识别提供者抽象接口。

    将音频字节流转换为文字。
    """

    @abstractmethod
    async def transcribe(self, audio_bytes: bytes, lang: str = "auto") -> str:
        """语音转文字。

        Args:
            audio_bytes: 音频数据（WAV/PCM 格式）。
            lang: 语言代码，"auto" 为自动检测。

        Returns:
            识别出的文字。
        """
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """服务商名称。"""
        ...
