from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vendor import Vendor
from app.repositories.base import BaseRepository


class VendorRepository(BaseRepository[Vendor]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Vendor)

    async def list_active(self, skip: int = 0, limit: int = 100) -> list[Vendor]:
        stmt = (
            select(Vendor).where(Vendor.is_active.is_(True)).offset(skip).limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_slug(self, slug: str) -> Vendor | None:
        stmt = select(Vendor).where(Vendor.slug == slug)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
