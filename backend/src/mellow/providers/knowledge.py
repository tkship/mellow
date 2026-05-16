"""知识库抽象接口。

所有知识库实现必须遵循此协议。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class WordEntry:
    """词条查询结果。"""
    word: str
    part_of_speech: str | None = None
    phonetic: str | None = None
    definitions: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    synonyms: list[str] = field(default_factory=list)
    source: str = "unknown"


@dataclass
class SearchResult:
    """语义检索结果。"""
    content: str
    score: float = 0.0
    metadata: dict = field(default_factory=dict)


class KnowledgeProvider(ABC):
    """知识库提供者抽象接口。

    支持两种检索模式：
    - lookup(): 精确查词，用于学习计划，必须准确
    - search(): 语义检索，用于日常对话，可容错
    """

    @abstractmethod
    async def lookup(self, word: str) -> WordEntry | None:
        """精确查词 —— 返回标准化词条，未找到返回 None。"""
        ...

    @abstractmethod
    async def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        """语义检索 —— 返回相关知识点列表。"""
        ...

    @property
    @abstractmethod
    def source_name(self) -> str:
        """知识来源标识，用于溯源和展示。"""
        ...
