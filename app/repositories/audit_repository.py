from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.repositories.base import BaseRepository


class AuditRepository(BaseRepository[AuditLog]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, AuditLog)

    async def recent(
        self, skip: int = 0, limit: int = 100, vendor_id: int | None = None
    ) -> list[AuditLog]:
        stmt = (
            select(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        if vendor_id is not None:
            stmt = stmt.where(AuditLog.vendor_id == vendor_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
