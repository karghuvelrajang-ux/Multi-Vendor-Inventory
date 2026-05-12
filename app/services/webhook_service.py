import hashlib
import hmac
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.enums import WebhookStatus
from app.models.webhook import WebhookEvent
from app.repositories.webhook_repository import WebhookRepository


class WebhookService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._webhooks = WebhookRepository(session)

    @staticmethod
    def verify_hmac(raw_body: bytes, signature_header: str | None) -> bool:
        settings = get_settings()
        if not signature_header:
            return False
        expected = hmac.new(
            settings.webhook_hmac_secret.encode(),
            raw_body,
            hashlib.sha256,
        ).hexdigest()
        provided = signature_header.strip()
        if provided.startswith("sha256="):
            provided = provided.removeprefix("sha256=")
        return hmac.compare_digest(expected, provided)

    async def ingest(
        self,
        vendor_id: int,
        topic: str,
        payload: dict,
        *,
        signature_valid: bool,
    ) -> WebhookEvent:
        event = WebhookEvent(
            vendor_id=vendor_id,
            topic=topic,
            payload=payload,
            signature_valid=signature_valid,
            status=WebhookStatus.QUEUED if signature_valid else WebhookStatus.FAILED,
        )
        if not signature_valid:
            event.error_message = "Invalid webhook signature"
        await self._webhooks.add(event)
        await self._session.commit()
        await self._session.refresh(event)
        return event

    async def mark_processed(self, event_id: int) -> WebhookEvent | None:
        entity = await self._webhooks.get_by_id(event_id)
        if entity is None:
            return None
        entity.status = WebhookStatus.PROCESSED
        entity.processed_at = datetime.now(timezone.utc)
        await self._session.flush()
        await self._session.commit()
        await self._session.refresh(entity)
        return entity
