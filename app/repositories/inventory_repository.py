from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory import InventoryItem
from app.repositories.base import BaseRepository


class InventoryRepository(BaseRepository[InventoryItem]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, InventoryItem)

    async def list_by_vendor(
        self, vendor_id: int, skip: int = 0, limit: int = 100
    ) -> list[InventoryItem]:
        stmt = (
            select(InventoryItem)
            .where(InventoryItem.vendor_id == vendor_id)
            .offset(skip)
            .limit(limit)
            .order_by(InventoryItem.sku)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_vendor_sku(self, vendor_id: int, sku: str) -> InventoryItem | None:
        stmt = select(InventoryItem).where(
            InventoryItem.vendor_id == vendor_id,
            InventoryItem.sku == sku,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
