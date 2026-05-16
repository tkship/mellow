"""语音合成 (TTS) 抽象接口。"""

from abc import ABC, abstractmethod


class TTSProvider(ABC):
    """语音合成提供者抽象接口。

    将文字转换为音频字节。
    """

    @abstractmethod
    async def synthesize(
        self,
        text: str,
        voice: str = "default",
        speed: float = 1.0,
        **kwargs,
    ) -> bytes:
        """文字转语音。

        Args:
            text: 待合成的文本。
            voice: 音色 ID。
            speed: 语速 (0.5 ~ 2.0)。

        Returns:
            音频数据（MP3/WAV 格式）。
        """
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """服务商名称。"""
        ...

    @abstractmethod
    def list_voices(self) -> list[dict[str, str]]:
        """列出可用音色。"""
        ...
