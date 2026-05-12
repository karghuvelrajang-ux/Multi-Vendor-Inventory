from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vendor import Vendor
from app.repositories.vendor_repository import VendorRepository
from app.schemas.vendor import VendorCreate


class VendorService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._vendors = VendorRepository(session)

    async def create(self, data: VendorCreate) -> Vendor:
        if await self._vendors.get_by_slug(data.slug):
            raise ValueError("Vendor slug already exists")
        vendor = Vendor(
            name=data.name,
            slug=data.slug,
            platform_type=data.platform_type,
            external_account_id=data.external_account_id,
        )
        await self._vendors.add(vendor)
        await self._session.commit()
        await self._session.refresh(vendor)
        return vendor

    async def list_active(self, skip: int = 0, limit: int = 100) -> list[Vendor]:
        return await self._vendors.list_active(skip=skip, limit=limit)

    async def get(self, vendor_id: int) -> Vendor | None:
        return await self._vendors.get_by_id(vendor_id)
