"""ImSingee/open-english-dictionary SQLite 实现。

GitHub: https://github.com/ImSingee/open-english-dictionary
许可证: MIT
字段: word, phonetic, summary (en+zh), definitions (partOfSpeech, definition, examples), synonyms
"""

import sqlite3
from pathlib import Path

from mellow.providers.knowledge import KnowledgeProvider, SearchResult, WordEntry


class OpenEnglishDictProvider(KnowledgeProvider):
    """基于 open-english-dictionary SQLite 的知识库实现。

    启动时需确保 .db 文件存在于 data_dir 中。
    未找到时优雅降级（lookup 返回 None）。
    """

    def __init__(self, db_path: str | Path = "./data/open-english-dictionary.db"):
        self._db_path = Path(db_path)
        self._conn: sqlite3.Connection | None = None

    @property
    def source_name(self) -> str:
        return "open-english-dictionary"

    def _ensure_connection(self):
        if self._conn is None:
            if not self._db_path.exists():
                raise FileNotFoundError(
                    f"词典数据库未找到: {self._db_path}。"
                    f"请从 https://github.com/ImSingee/open-english-dictionary/releases 下载。"
                )
            self._conn = sqlite3.connect(str(self._db_path))
            self._conn.row_factory = sqlite3.Row

    async def lookup(self, word: str) -> WordEntry | None:
        """精确查词 —— 大小写不敏感。"""
        try:
            self._ensure_connection()
        except FileNotFoundError:
            return None

        cursor = self._conn.execute(
            "SELECT * FROM entries WHERE word = ? COLLATE NOCASE",
            (word.strip().lower(),),
        )
        row = cursor.fetchone()
        if row is None:
            return None

        entry = WordEntry(
            word=row["word"],
            phonetic=row["phonetic"] if "phonetic" in row.keys() else None,
        )

        # 解析 definitions JSON 字段
        import json

        if "definitions" in row.keys() and row["definitions"]:
            try:
                defs = json.loads(row["definitions"])
                for d in defs if isinstance(defs, list) else [defs]:
                    entry.part_of_speech = d.get("partOfSpeech", entry.part_of_speech)
                    if d.get("definition", {}).get("en"):
                        entry.definitions.append(d["definition"]["en"])
                    if d.get("examples"):
                        entry.examples.extend(
                            e.get("en", str(e))
                            for e in (d["examples"] if isinstance(d["examples"], list) else [])
                        )
            except (json.JSONDecodeError, TypeError):
                pass

        if "synonyms" in row.keys() and row["synonyms"]:
            try:
                entry.synonyms = json.loads(row["synonyms"])
            except (json.JSONDecodeError, TypeError):
                pass

        entry.source = self.source_name
        return entry

    async def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        """语义检索 —— SQLite FTS 全文搜索降级方案。

        注：SQLite 不支持真正的语义检索。
        完整语义检索需配合 LanceDB + Embedding 使用。
        """
        try:
            self._ensure_connection()
        except FileNotFoundError:
            return []

        # 使用 SQL LIKE 作为简易降级搜索
        pattern = f"%{query.strip().lower()}%"
        cursor = self._conn.execute(
            "SELECT word, phonetic FROM entries WHERE word LIKE ? OR word LIKE ? LIMIT ?",
            (pattern, f"%{query.strip().lower()}", top_k),
        )
        results = []
        for row in cursor.fetchall():
            entry = await self.lookup(row["word"])
            if entry:
                results.append(SearchResult(
                    content="; ".join(entry.definitions[:2]) if entry.definitions else entry.word,
                    score=0.5,
                    metadata={"word": entry.word, "phonetic": entry.phonetic},
                ))
        return results

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None
