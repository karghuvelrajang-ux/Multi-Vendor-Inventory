from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import WebhookStatus
from app.models.webhook import WebhookEvent
from app.repositories.base import BaseRepository


class WebhookRepository(BaseRepository[WebhookEvent]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, WebhookEvent)

    async def list_recent_for_vendor(
        self, vendor_id: int, limit: int = 50
    ) -> list[WebhookEvent]:
        stmt = (
            select(WebhookEvent)
            .where(WebhookEvent.vendor_id == vendor_id)
            .order_by(WebhookEvent.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update_status(
        self,
        event_id: int,
        status: WebhookStatus,
        *,
        error_message: str | None = None,
    ) -> WebhookEvent | None:
        entity = await self.get_by_id(event_id)
        if entity is None:
            return None
        entity.status = status
        entity.error_message = error_message
        await self._session.flush()
        await self._session.refresh(entity)
        return entity
