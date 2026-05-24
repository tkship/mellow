"""知识库查词路由。"""

import logging

from fastapi import APIRouter, Depends, Query

from mellow.api.deps import get_container, get_current_user
from mellow.di import Container
from mellow.providers.auth import UserInfo

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/knowledge", tags=["knowledge"])


@router.get("/lookup")
async def lookup(
    word: str = Query(..., min_length=1),
    user: UserInfo = Depends(get_current_user),
    container: Container = Depends(get_container),
):
    """精确查词。"""
    kb = await container.knowledge()
    entry = await kb.lookup(word)
    if not entry:
        return {"error": f"未找到词条: {word}", "message": "词条不存在"}

    return {
        "word": entry.word,
        "phonetic": entry.phonetic,
        "part_of_speech": entry.part_of_speech,
        "definitions": entry.definitions,
        "examples": entry.examples,
        "synonyms": entry.synonyms,
        "source": entry.source,
    }


@router.get("/search")
async def search(
    q: str = Query(..., min_length=1),
    top_k: int = Query(5, ge=1, le=20),
    user: UserInfo = Depends(get_current_user),
    container: Container = Depends(get_container),
):
    """语义搜索。

    优先使用 Embedding + LanceDB 向量检索；
    若 Embedding 不可用则回退到 SQL LIKE 匹配。
    """
    kb = await container.knowledge()

    # 尝试向量检索
    try:
        embed = await container.embedding()
        vector_store = await container.vector_store()

        # 向量化查询
        vectors = await embed.embed([q])
        query_vector = vectors[0]

        # 在向量表中搜索
        table = await vector_store.get_table("knowledge_chunks")
        results = await table.search(query_vector).limit(top_k).to_pandas()

        search_results = []
        for _, row in results.iterrows():
            search_results.append({
                "content": row.get("content", ""),
                "score": float(row.get("_distance", row.get("score", 0.5))),
                "metadata": {
                    "word": row.get("chunk_id", ""),
                    "source": row.get("source", ""),
                    "topic": row.get("topic", ""),
                },
            })
        return {"query": q, "results": search_results}
    except Exception as e:
        logger.info("向量检索不可用，回退到 SQL LIKE 搜索: %s", e)

    # Fallback: SQL LIKE
    results = await kb.search(q, top_k=top_k)
    return {
        "query": q,
        "results": [
            {"content": r.content, "score": r.score, "metadata": r.metadata}
            for r in results
        ],
    }