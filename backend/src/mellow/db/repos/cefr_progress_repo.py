"""CEFR 进度追踪 Repository。"""

from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from mellow.db.models.cefr_progress import CefrProgressRow


class CefrProgressRepository:
    """CEFR 进度追踪数据访问。"""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def record(
        self,
        user_id: str,
        cefr_level: str,
        score: float,
        vocabulary_size: int = 0,
    ) -> CefrProgressRow:
        """记录一条 CEFR 进度快照。"""
        row = CefrProgressRow(
            user_id=user_id,
            cefr_level=cefr_level,
            score=score,
            vocabulary_size=vocabulary_size,
        )
        self._session.add(row)
        await self._session.flush()
        return row

    async def get_history(
        self,
        user_id: str,
        range_str: str = "month",
    ) -> list[CefrProgressRow]:
        """获取 CEFR 历史进度。

        Args:
            user_id: 用户 ID
            range_str: 时间范围 week/month/half_year
        """
        stmt = (
            select(CefrProgressRow)
            .where(CefrProgressRow.user_id == user_id)
            .order_by(CefrProgressRow.recorded_at.desc())
        )

        # 限制条数：周=7, 月=30, 半年=180
        limit_map = {"week": 7, "month": 30, "half_year": 180}
        limit = limit_map.get(range_str, 30)
        stmt = stmt.limit(limit)

        result = await self._session.execute(stmt)
        rows = list(result.scalars().all())
        # 按时间正序返回（从早到晚）
        rows.reverse()
        return rows