from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory import InventoryItem
from app.repositories.inventory_repository import InventoryRepository


class InventoryService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._inventory = InventoryRepository(session)

    async def upsert_item(
        self,
        vendor_id: int,
        *,
        sku: str,
        title: str | None,
        quantity_available: int,
        quantity_reserved: int,
        external_product_id: str | None,
    ) -> InventoryItem:
        existing = await self._inventory.get_by_vendor_sku(vendor_id, sku)
        if existing:
            existing.title = title if title is not None else existing.title
            existing.quantity_available = quantity_available
            existing.quantity_reserved = quantity_reserved
            existing.external_product_id = (
                external_product_id
                if external_product_id is not None
                else existing.external_product_id
            )
            existing.version = existing.version + 1
            await self._session.flush()
            await self._session.refresh(existing)
            item = existing
        else:
            item = InventoryItem(
                vendor_id=vendor_id,
                sku=sku,
                title=title,
                quantity_available=quantity_available,
                quantity_reserved=quantity_reserved,
                external_product_id=external_product_id,
            )
            await self._inventory.add(item)
        await self._session.commit()
        await self._session.refresh(item)
        return item

    async def patch_item(
        self,
        vendor_id: int,
        sku: str,
        *,
        title: str | None = None,
        quantity_available: int | None = None,
        quantity_reserved: int | None = None,
        external_product_id: str | None = None,
    ) -> InventoryItem | None:
        existing = await self._inventory.get_by_vendor_sku(vendor_id, sku)
        if existing is None:
            return None
        if title is not None:
            existing.title = title
        if quantity_available is not None:
            existing.quantity_available = quantity_available
        if quantity_reserved is not None:
            existing.quantity_reserved = quantity_reserved
        if external_product_id is not None:
            existing.external_product_id = external_product_id
        existing.version = existing.version + 1
        await self._session.flush()
        await self._session.commit()
        await self._session.refresh(existing)
        return existing

    async def list_vendor_inventory(
        self, vendor_id: int, skip: int = 0, limit: int = 100
    ) -> list[InventoryItem]:
        return await self._inventory.list_by_vendor(vendor_id, skip=skip, limit=limit)
