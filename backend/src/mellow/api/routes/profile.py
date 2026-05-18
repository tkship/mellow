"""用户画像路由。"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from mellow.api.deps import get_container, get_current_user
from mellow.di import Container
from mellow.providers.auth import UserInfo

router = APIRouter(prefix="/api/v1/profile", tags=["profile"])


class ProfileUpdateRequest(BaseModel):
    """画像更新请求。"""

    cefr_level: str | None = Field(default=None, pattern=r"^(A0|A1|A2|B1|B2|C1|C2)$")
    vocabulary_size: int | None = Field(default=None, ge=0)
    learning_goal: str | None = Field(default=None, max_length=500)


@router.get("")
async def get_profile(
    user: UserInfo = Depends(get_current_user),
    container: Container = Depends(get_container),
):
    """获取学习画像。"""
    pm = await container.profile_manager()
    profile = await pm.get_or_create(user.id)
    summary = await pm.get_profile_summary(user.id)
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
    pm = await container.profile_manager()
    mistakes = await pm.get_recent_mistakes(user.id, limit=20)
    return {"mistakes": [m.model_dump() for m in mistakes]}


@router.put("")
async def update_profile(
    req: ProfileUpdateRequest,
    user: UserInfo = Depends(get_current_user),
    container: Container = Depends(get_container),
):
    """更新学习画像。"""
    pm = await container.profile_manager()

    # Build update kwargs from non-None fields
    update_data = req.model_dump(exclude_unset=True)
    if update_data:
        await pm.update(user.id, **update_data)

    # Return updated profile in same format as GET
    profile = await pm.get_or_create(user.id)
    summary = await pm.get_profile_summary(user.id)
    return {
        "cefr_level": profile.cefr_level,
        "vocabulary_size": profile.vocabulary_size,
        "weak_areas": profile.weak_areas,
        "known_words_count": len([w for w, l in profile.mastered_words.items() if l >= 0.7]),
        "completed_lessons": profile.completed_lessons[-5:],
        "current_plan": profile.current_plan.model_dump() if profile.current_plan else None,
        "summary": summary,
    }


@router.get("/stats")
async def get_stats(
    user: UserInfo = Depends(get_current_user),
    container: Container = Depends(get_container),
    range: str = "month",
):
    """获取使用统计数据。

    Args:
        range: 时间范围 — week, month, half_year
    """
    pm = await container.profile_manager()
    profile = await pm.get_or_create(user.id)

    # Calculate learning days (unique dates with activity)
    now = datetime.now(timezone.utc)
    days_count = _estimate_learning_days(profile, range)

    # CEFR progress over time
    cefr_progress = [
        {"date": now.strftime("%Y-%m-%d"), "level": profile.cefr_level, "score": _cefr_score(profile.cefr_level)},
    ]

    return {
        "total_messages": getattr(profile, 'message_count', 0),
        "learning_days": days_count,
        "check_in_count": getattr(profile, 'check_in_count', 0),
        "cefr_level": profile.cefr_level,
        "vocabulary_size": profile.vocabulary_size,
        "weak_areas": profile.weak_areas,
        "cefr_progress": cefr_progress,
        "range": range,
    }


def _cefr_score(level: str) -> float:
    """CEFR level → numeric score for charting."""
    scores = {"A0": 0, "A1": 1, "A2": 2, "B1": 3, "B2": 4, "C1": 5, "C2": 6}
    return float(scores.get(level, 0))


def _estimate_learning_days(profile, range_str: str) -> int:
    """Estimate active learning days based on profile data."""
    # Derive from known words and completed lessons as a heuristic
    word_count = len(profile.mastered_words)
    lesson_count = len(profile.completed_lessons)

    base = max(1, min(word_count // 3 + lesson_count, 365))

    if range_str == "week":
        return min(base, 7)
    elif range_str == "month":
        return min(base, 30)
    elif range_str == "half_year":
        return min(base, 180)
    return base
