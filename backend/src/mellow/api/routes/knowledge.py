"""知识库查词路由。"""

from fastapi import APIRouter, Depends, Query

from mellow.api.deps import get_container
from mellow.di import Container

router = APIRouter(prefix="/api/v1/knowledge", tags=["knowledge"])


@router.get("/lookup")
async def lookup(
    word: str = Query(..., min_length=1),
    container: Container = Depends(get_container),
):
    """精确查词。"""
    kb = await container.knowledge()
    entry = await kb.lookup(word)
    if not entry:
        return {"error": f"未找到词条: {word}"}, 404

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
    container: Container = Depends(get_container),
):
    """语义搜索。"""
    kb = await container.knowledge()
    results = await kb.search(q, top_k=top_k)
    return {
        "query": q,
        "results": [
            {"content": r.content, "score": r.score, "metadata": r.metadata}
            for r in results
        ],
    }
