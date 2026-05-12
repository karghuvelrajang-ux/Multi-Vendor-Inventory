import json
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import ensure_vendor_scope
from app.dependencies import get_db_session, require_roles
from app.events.dispatcher import dispatch_webhook_processing
from app.models.enums import UserRole, WebhookStatus
from app.models.user import User
from app.services.audit_service import AuditService
from app.services.vendor_service import VendorService
from app.services.webhook_service import WebhookService

router = APIRouter()


@router.post("/vendor/{vendor_id}")
async def ingest_vendor_webhook(
    vendor_id: int,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[
        User,
        Depends(
            require_roles(
                UserRole.SUPER_ADMIN, UserRole.OPS_ADMIN, UserRole.VENDOR_MANAGER
            )
        ),
    ],
    x_inventory_signature: Annotated[str | None, Header()] = None,
    x_webhook_topic: Annotated[str | None, Header()] = None,
) -> dict[str, int | str | None]:
    """Authenticated ingest endpoint (HMAC simulates platform-signed delivery)."""
    ensure_vendor_scope(user, vendor_id)
    vendor_service = VendorService(session)
    vendor = await vendor_service.get(vendor_id)
    if vendor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found"
        )

    raw = await request.body()
    webhook_service = WebhookService(session)
    signature_ok = webhook_service.verify_hmac(raw, x_inventory_signature)
    try:
        payload = json.loads(raw.decode("utf-8")) if raw else {}
        if not isinstance(payload, dict):
            raise ValueError("payload must be a JSON object")
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON body"
        ) from e

    topic = x_webhook_topic or payload.get("topic") or "inventory.update"
    event = await webhook_service.ingest(
        vendor_id,
        str(topic),
        payload,
        signature_valid=signature_ok,
    )
    audit = AuditService(session)
    await audit.record(
        actor_user_id=user.id,
        action="webhook.received",
        resource_type="webhook_event",
        resource_id=str(event.id),
        vendor_id=vendor_id,
        details={"topic": topic, "signature_valid": signature_ok},
    )

    task_id = None
    if signature_ok and event.status != WebhookStatus.FAILED:
        task_id = dispatch_webhook_processing(event.id)

    return {"webhook_event_id": event.id, "celery_task_id": task_id}
