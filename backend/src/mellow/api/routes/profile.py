"""用户画像路由。"""

from fastapi import APIRouter, Depends

from mellow.api.deps import get_container, get_current_user
from mellow.di import Container
from mellow.providers.auth import UserInfo

router = APIRouter(prefix="/api/v1/profile", tags=["profile"])


@router.get("")
async def get_profile(
    user: UserInfo = Depends(get_current_user),
    container: Container = Depends(get_container),
):
    """获取学习画像。"""
    profile = await container.profile_manager.get_or_create(user.id)
    summary = await container.profile_manager.get_profile_summary(user.id)
    return {
        "cefr_level": profile.cefr_level,
        "vocabulary_size": profile.vocabulary_size,
        "weak_areas": profile.weak_areas,
        "known_words_count": len([w for w, l in profile.mastered_words.items() if l >= 0.7]),
        "completed_lessons": profile.completed_lessons[-5:],
        "current_plan": profile.current_plan.model_dump() if profile.current_plan else None,
        "summary": summary,
    }


@router.get("/mistakes")
async def get_mistakes(
    user: UserInfo = Depends(get_current_user),
    container: Container = Depends(get_container),
):
    """获取最近错误记录。"""
    mistakes = await container.profile_manager.get_recent_mistakes(user.id, limit=20)
    return {"mistakes": [m.model_dump() for m in mistakes]}
